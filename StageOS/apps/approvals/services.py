from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditEvent
from common.permissions import UserRoles, can_decide_approval, is_admin_user, user_type
from common import department_permissions
from .models import ApprovalDecision


def submit_for_approval(context, approval_step, user, comment=''):
    """Create an approval request with pending status."""
    from .models import ApprovalRequest

    request = ApprovalRequest.objects.create(
        organisation=context.organisation,
        operating_context=context,
        approval_step=approval_step,
        requested_by=user,
        decision=ApprovalDecision.PENDING,
        decision_comment=comment,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='approval.requested',
        payload={
            'approval_request_id': str(request.id),
            'context_id': str(context.id),
            'approval_step_id': str(approval_step.id),
            'step_name': approval_step.name,
        },
    )
    return request


def decide_approval(approval_request, user, decision, comment='', evidence=None):
    """Record an approval decision."""
    approver_department = approval_request.approval_step.approver_department
    has_global_authority = is_admin_user(user) or user_type(user) == UserRoles.EXECUTIVE
    if approver_department and department_permissions.has_department_membership(user):
        has_authority = has_global_authority or department_permissions.can_approve_department_work(user, approver_department)
    else:
        has_authority = can_decide_approval(user)
    if not has_authority:
        raise PermissionDenied('You do not have permission to decide approvals.')

    if decision == ApprovalDecision.PENDING:
        raise ValidationError(
            {'detail': "Decision cannot be 'pending'. Please provide an actual decision."}
        )

    if decision in {
        ApprovalDecision.REJECTED,
        ApprovalDecision.CHANGES_REQUESTED,
        ApprovalDecision.ESCALATED,
        ApprovalDecision.EXCEPTION_APPROVED,
    } and not comment.strip():
        raise ValidationError({'comment': 'A comment is required for this approval decision.'})

    if approval_request.decision != ApprovalDecision.PENDING:
        raise ValidationError(
            {'detail': (
                f"This request has already been decided "
                f"(current decision: '{approval_request.decision}'). "
                "Cannot re-decide."
            )}
        )

    old_decision = approval_request.decision
    approval_request.decision = decision
    approval_request.decided_by = user
    approval_request.decided_at = timezone.now()
    approval_request.decision_comment = comment
    approval_request.evidence_reviewed = evidence
    approval_request.save(update_fields=[
        'decision', 'decided_by', 'decided_at',
        'decision_comment', 'evidence_reviewed', 'updated_at',
    ])

    AuditEvent.objects.create(
        organisation=approval_request.organisation,
        actor=user,
        event_type='approval.decided',
        payload={
            'approval_request_id': str(approval_request.id),
            'context_id': str(approval_request.operating_context_id),
            'old_value': old_decision,
            'new_value': decision,
            'comment': comment,
            'evidence_reviewed_id': str(evidence.id) if evidence else None,
        },
    )

    if decision != ApprovalDecision.PENDING and approval_request.requested_by:
        from apps.tasks.services import _notify as notify_user
        decision_labels = {
            'approved': 'Your sign-off request was approved',
            'rejected': 'Your sign-off request was not approved',
            'changes_requested': 'Changes requested on your sign-off',
            'escalated': 'Your sign-off has been escalated',
            'exception_approved': 'Your sign-off was exception-approved',
        }
        msg = decision_labels.get(decision, f'Sign-off decision: {decision}')
        approver_dept = getattr(approval_request.approval_step, 'approver_department', None)
        notify_user(
            recipient=approval_request.requested_by,
            actor=user,
            notification_type='approval_decided',
            title=msg,
            message=comment or '',
            department=approver_dept,
        )

    return approval_request
