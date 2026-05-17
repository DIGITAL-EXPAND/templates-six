from django.utils import timezone
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService


def approve_rider(rider, user):
    rider.status = 'approved'
    rider.approved_by = user
    rider.approved_at = timezone.now()
    rider.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
    AuditEvent.objects.create(
        organisation=rider.organisation,
        actor=user,
        event_type='rider.approved',
        payload={
            'rider_id': str(rider.id),
            'context_id': str(rider.operating_context_id),
        },
    )
    return rider


def set_rider_status(rider, user, status, comment=''):
    old_status = rider.status
    rider.status = status
    fields = ['status', 'updated_at']
    if status == 'approved':
        rider.approved_by = user
        rider.approved_at = timezone.now()
        fields.extend(['approved_by', 'approved_at'])
    rider.save(update_fields=fields)
    AuditService.record(
        organisation=rider.organisation,
        actor=user,
        event_type=f'rider.{status}',
        target_type='TechnicalRider',
        target_id=rider.id,
        old_value=old_status,
        new_value=status,
        reason=comment,
        payload={'context_id': str(rider.operating_context_id)},
    )
    return rider
