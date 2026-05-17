from django.utils import timezone
from rest_framework.exceptions import APIException, ValidationError

from apps.audit.models import AuditEvent
from apps.approvals.models import ApprovalDecision


class EvidenceRequired(APIException):
    status_code = 422
    default_detail = 'Evidence document is required before this step can be advanced.'
    default_code = 'evidence_required'


def instantiate_workflow(context, template, user):
    """Create a WorkflowInstance from a template for a context."""
    from .models import WorkflowInstance, WorkflowStepInstance, WorkflowStepStatus

    if template.context_type != context.context_type:
        raise ValidationError(
            f"Template context_type '{template.context_type}' does not match "
            f"context context_type '{context.context_type}'."
        )

    instance = WorkflowInstance.objects.create(
        organisation=context.organisation,
        template=template,
        operating_context=context,
        status='active',
    )

    steps = list(template.steps.order_by('step_number'))
    step_instances = []
    for i, step_tpl in enumerate(steps):
        step_status = 'in_progress' if i == 0 else 'pending'
        step_instances.append(WorkflowStepInstance(
            organisation=context.organisation,
            workflow_instance=instance,
            step_template=step_tpl,
            step_number=step_tpl.step_number,
            status=step_status,
        ))
    WorkflowStepInstance.objects.bulk_create(step_instances)

    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='workflow.instantiated',
        payload={
            'workflow_instance_id': str(instance.id),
            'template_id': str(template.id),
            'template_name': template.name,
            'context_id': str(context.id),
            'step_count': len(steps),
        },
    )
    return instance


def advance_step(step_instance, user, notes='', evidence_document=None, approval_request=None):
    """Complete current step and activate the next."""
    from .models import WorkflowStepStatus, WorkflowInstanceStatus

    if step_instance.status != WorkflowStepStatus.IN_PROGRESS:
        raise ValidationError(
            {'detail': f"Step is '{step_instance.status}', not 'in_progress'. Cannot advance."},
            code='invalid_step_status',
        )

    if step_instance.step_template.requires_evidence and evidence_document is None:
        raise EvidenceRequired()

    if approval_request is None:
        approval_request = step_instance.approval_request

    if step_instance.step_template.requires_approval:
        if approval_request is None:
            raise ValidationError({
                'approval_request': 'Approved approval is required before this process step can be completed.'
            })
        if approval_request.organisation_id != step_instance.organisation_id:
            raise ValidationError({'approval_request': 'Approval must belong to the same organisation.'})
        if approval_request.operating_context_id != step_instance.workflow_instance.operating_context_id:
            raise ValidationError({'approval_request': 'Approval must belong to the same Workspace.'})
        if approval_request.decision not in {
            ApprovalDecision.APPROVED,
            ApprovalDecision.EXCEPTION_APPROVED,
        }:
            raise ValidationError({'approval_request': 'Approval must be approved before this process step can be completed.'})

    now = timezone.now()
    step_instance.status = WorkflowStepStatus.COMPLETED
    step_instance.completed_at = now
    step_instance.completed_by = user
    step_instance.notes = notes
    step_instance.evidence_document = evidence_document
    step_instance.approval_request = approval_request
    step_instance.save(update_fields=[
        'status', 'completed_at', 'completed_by', 'notes',
        'evidence_document', 'approval_request', 'updated_at',
    ])

    workflow = step_instance.workflow_instance
    next_step = (
        workflow.step_instances
        .filter(step_number__gt=step_instance.step_number)
        .order_by('step_number')
        .first()
    )

    if next_step:
        next_step.status = WorkflowStepStatus.IN_PROGRESS
        next_step.started_at = now
        next_step.save(update_fields=['status', 'started_at', 'updated_at'])
    else:
        workflow.status = WorkflowInstanceStatus.COMPLETED
        workflow.completed_at = now
        workflow.save(update_fields=['status', 'completed_at', 'updated_at'])

    AuditEvent.objects.create(
        organisation=step_instance.organisation,
        actor=user,
        event_type='workflow.step_completed',
        payload={
            'step_instance_id': str(step_instance.id),
            'workflow_instance_id': str(workflow.id),
            'step_number': step_instance.step_number,
            'notes': notes,
            'has_evidence': evidence_document is not None,
            'approval_request_id': str(approval_request.id) if approval_request else None,
            'has_approval': approval_request is not None,
            'workflow_completed': next_step is None,
        },
    )
    return step_instance
