from apps.audit.models import AuditEvent
from apps.audit.services import AuditService
from rest_framework.exceptions import ValidationError


def log_incident(context, user, data):
    from .models import Incident
    incident = Incident.objects.create(
        organisation=context.organisation,
        operating_context=context,
        reported_by=user,
        **data,
    )
    event_type = (
        'incident.critical_logged'
        if incident.severity in ('high', 'critical')
        else 'incident.logged'
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type=event_type,
        payload={
            'incident_id': str(incident.id),
            'context_id': str(context.id),
            'incident_type': incident.incident_type,
            'severity': incident.severity,
        },
    )
    return incident


def set_foh_status(foh_plan, user, status, comment=''):
    if status == 'closed' and foh_plan.checklist_items.filter(is_checked=False).exists():
        raise ValidationError({
            'detail': 'All FOH / Show-day checklist items must be checked before close-out.'
        })
    old_status = foh_plan.status
    foh_plan.status = status
    foh_plan.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=foh_plan.organisation,
        actor=user,
        event_type='foh.status_changed',
        target_type='FOHPlan',
        target_id=foh_plan.id,
        old_value=old_status,
        new_value=status,
        reason=comment,
    )
    return foh_plan


def check_checklist_item(item, user, comment=''):
    old_value = item.is_checked
    item.is_checked = True
    item.checked_by = user
    from django.utils import timezone
    item.checked_at = timezone.now()
    item.save(update_fields=['is_checked', 'checked_by', 'checked_at', 'updated_at'])
    AuditService.record(
        organisation=item.organisation,
        actor=user,
        event_type='foh.checklist_checked',
        target_type='ShowDayChecklist',
        target_id=item.id,
        old_value=old_value,
        new_value=True,
        reason=comment,
    )
    return item
