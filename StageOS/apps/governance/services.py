from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService
from .models import ActionStatus, ExecutiveActionStatus, ExecutiveActionType, RiskStatus


def report_kpi(kpi, user, value, evidence_doc=None, context=None, notes=''):
    from .models import KPIEvidence
    if kpi.evidence_description.strip() and evidence_doc is None:
        raise ValidationError({
            'evidence_document': 'Evidence is required for this KPI report.'
        })
    old_value = str(kpi.actual_value)
    evidence = KPIEvidence.objects.create(
        organisation=kpi.organisation,
        kpi=kpi,
        operating_context=context,
        value_reported=value,
        evidence_document=evidence_doc,
        reported_by=user,
        notes=notes,
    )
    kpi.actual_value = value
    kpi.save(update_fields=['actual_value', 'updated_at'])
    AuditEvent.objects.create(
        organisation=kpi.organisation,
        actor=user,
        event_type='governance.kpi_reported',
        payload={
            'kpi_id': str(kpi.id),
            'kpi_name': kpi.name,
            'old_value': old_value,
            'new_value': str(value),
            'evidence_id': str(evidence.id),
        },
    )
    return evidence


def close_risk(risk, user, comment=''):
    if risk.status == RiskStatus.CLOSED:
        raise ValidationError({'detail': 'Risk is already closed.'})
    risk.status = RiskStatus.CLOSED
    risk.closed_date = timezone.now().date()
    risk.closed_by = user
    risk.save(update_fields=['status', 'closed_date', 'closed_by', 'updated_at'])
    AuditEvent.objects.create(
        organisation=risk.organisation,
        actor=user,
        event_type='governance.risk_closed',
        payload={
            'risk_id': str(risk.id),
            'title': risk.title,
            'comment': comment,
        },
    )
    return risk


def complete_corrective_action(action, user):
    if action.status == ActionStatus.COMPLETED:
        raise ValidationError({'detail': 'Already completed.'})
    if action.evidence_document_id is None:
        raise ValidationError({
            'evidence_document': 'Evidence is required before a corrective action can be completed.'
        })
    action.status = ActionStatus.COMPLETED
    action.completed_date = timezone.now().date()
    action.completed_by = user
    action.save(update_fields=['status', 'completed_date', 'completed_by', 'updated_at'])
    AuditEvent.objects.create(
        organisation=action.organisation,
        actor=user,
        event_type='governance.corrective_action_completed',
        payload={
            'action_id': str(action.id),
            'risk_id': str(action.risk_id),
        },
    )
    return action


def create_executive_action(organisation, user, data):
    from apps.tasks.models import Task
    from .models import CorrectiveAction, ExecutiveAction, Risk

    action = ExecutiveAction.objects.create(
        organisation=organisation,
        created_by=user,
        **data,
    )

    linked_task = None
    linked_risk = action.linked_risk
    linked_corrective_action = None

    if action.action_type in {
        ExecutiveActionType.REQUEST_CHANGE,
        ExecutiveActionType.FLAG_ISSUE,
        ExecutiveActionType.ASSIGN_CORRECTIVE_ACTION,
        ExecutiveActionType.REQUEST_MORE_INFORMATION,
    } and action.operating_context_id:
        linked_task = Task.objects.create(
            organisation=organisation,
            operating_context=action.operating_context,
            title=f'Executive action: {action.title}',
            description=action.instruction or action.reason,
            department=action.department,
            assigned_to=action.assigned_to,
            due_date=action.due_date,
            priority='high' if action.action_type != ExecutiveActionType.FLAG_ISSUE else 'medium',
            evidence_required=action.action_type in {
                ExecutiveActionType.REQUEST_CHANGE,
                ExecutiveActionType.ASSIGN_CORRECTIVE_ACTION,
            },
        )
        action.linked_task = linked_task

    if action.action_type == ExecutiveActionType.FLAG_RISK:
        linked_risk = Risk.objects.create(
            organisation=organisation,
            operating_context=action.operating_context,
            title=action.title,
            description=action.reason or action.instruction,
            risk_level='high',
            owner=action.assigned_to or user,
            mitigation_plan=action.instruction,
        )
        action.linked_risk = linked_risk

    if action.action_type == ExecutiveActionType.ASSIGN_CORRECTIVE_ACTION:
        if not linked_risk:
            linked_risk = Risk.objects.create(
                organisation=organisation,
                operating_context=action.operating_context,
                title=f'Corrective action risk: {action.title}',
                description=action.reason,
                risk_level='medium',
                owner=action.assigned_to or user,
                mitigation_plan=action.instruction,
            )
            action.linked_risk = linked_risk
        linked_corrective_action = CorrectiveAction.objects.create(
            organisation=organisation,
            risk=linked_risk,
            action=action.instruction,
            owner=action.assigned_to or user,
            due_date=action.due_date,
        )
        action.linked_corrective_action = linked_corrective_action

    if linked_task or linked_risk or linked_corrective_action:
        action.save(update_fields=[
            'linked_task', 'linked_risk', 'linked_corrective_action', 'updated_at',
        ])

    AuditService.record(
        organisation=organisation,
        actor=user,
        event_type='executive.action_created',
        target_type='ExecutiveAction',
        target_id=action.id,
        reason=action.reason,
        payload={
            'action_id': str(action.id),
            'action_type': action.action_type,
            'title': action.title,
            'context_id': str(action.operating_context_id) if action.operating_context_id else None,
            'target_type': action.target_type,
            'target_id': action.target_id,
            'department_id': str(action.department_id) if action.department_id else None,
            'linked_task_id': str(action.linked_task_id) if action.linked_task_id else None,
            'linked_risk_id': str(action.linked_risk_id) if action.linked_risk_id else None,
            'linked_corrective_action_id': (
                str(action.linked_corrective_action_id)
                if action.linked_corrective_action_id else None
            ),
        },
    )
    return action


def acknowledge_executive_action(action, user, comment=''):
    if action.status != ExecutiveActionStatus.OPEN:
        raise ValidationError({'detail': f"Cannot acknowledge an executive action in '{action.status}' status."})
    old_status = action.status
    action.status = ExecutiveActionStatus.ACKNOWLEDGED
    action.acknowledged_by = user
    action.acknowledged_at = timezone.now()
    action.save(update_fields=['status', 'acknowledged_by', 'acknowledged_at', 'updated_at'])
    _audit_executive_action_status(action, user, old_status, comment)
    return action


def complete_executive_action(action, user, comment=''):
    if action.status in {ExecutiveActionStatus.COMPLETED, ExecutiveActionStatus.CANCELLED}:
        raise ValidationError({'detail': f"Executive action is already '{action.status}'."})
    old_status = action.status
    action.status = ExecutiveActionStatus.COMPLETED
    action.completed_by = user
    action.completed_at = timezone.now()
    action.save(update_fields=['status', 'completed_by', 'completed_at', 'updated_at'])
    _audit_executive_action_status(action, user, old_status, comment)
    return action


def cancel_executive_action(action, user, comment=''):
    if not comment.strip():
        raise ValidationError({'comment': 'A comment is required to cancel an executive action.'})
    if action.status in {ExecutiveActionStatus.COMPLETED, ExecutiveActionStatus.CANCELLED}:
        raise ValidationError({'detail': f"Executive action is already '{action.status}'."})
    old_status = action.status
    action.status = ExecutiveActionStatus.CANCELLED
    action.save(update_fields=['status', 'updated_at'])
    _audit_executive_action_status(action, user, old_status, comment)
    return action


def _audit_executive_action_status(action, user, old_status, comment=''):
    AuditService.record(
        organisation=action.organisation,
        actor=user,
        event_type=f'executive.action_{action.status}',
        target_type='ExecutiveAction',
        target_id=action.id,
        old_value=old_status,
        new_value=action.status,
        reason=comment,
        payload={
            'action_id': str(action.id),
            'action_type': action.action_type,
            'title': action.title,
        },
    )
