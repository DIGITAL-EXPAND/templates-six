from common.enums import ContextStatus
from apps.audit.models import AuditEvent

VALID_TRANSITIONS = {
    ContextStatus.DRAFT:         [ContextStatus.SUBMITTED, ContextStatus.CANCELLED],
    ContextStatus.SUBMITTED:     [ContextStatus.UNDER_REVIEW, ContextStatus.CANCELLED],
    ContextStatus.UNDER_REVIEW:  [ContextStatus.CONFIRMED, ContextStatus.REJECTED, ContextStatus.CANCELLED],
    ContextStatus.CONFIRMED:     [ContextStatus.IN_PRODUCTION, ContextStatus.CANCELLED],
    ContextStatus.IN_PRODUCTION: [ContextStatus.IN_DELIVERY, ContextStatus.CANCELLED],
    ContextStatus.IN_DELIVERY:   [ContextStatus.COMPLETED, ContextStatus.CANCELLED],
    ContextStatus.COMPLETED:     [ContextStatus.CLOSED],
    ContextStatus.REJECTED:      [ContextStatus.DRAFT],
    ContextStatus.CANCELLED:     [],
    ContextStatus.CLOSED:        [],
}


def create_context(organisation, user, data):
    from .models import OperatingContext

    context = OperatingContext.objects.create(organisation=organisation, **data)
    AuditEvent.objects.create(
        organisation=organisation,
        actor=user,
        event_type='context.created',
        payload={
            'context_id': str(context.id),
            'title': context.title,
            'context_type': context.context_type,
            'status': context.status,
        },
    )
    return context


def change_context_status(context, user, new_status, comment=''):
    try:
        new_status_enum = ContextStatus(new_status)
    except ValueError:
        raise ValueError(f"'{new_status}' is not a valid status.")

    current_enum = ContextStatus(context.status)
    allowed = VALID_TRANSITIONS.get(current_enum, [])

    if new_status_enum not in allowed:
        if not allowed:
            raise ValueError(
                f"'{context.status}' is a terminal status. No transitions are allowed."
            )
        valid_values = ', '.join(s.value for s in allowed)
        raise ValueError(
            f"Cannot transition from '{context.status}' to '{new_status}'. "
            f"Valid transitions: {valid_values}."
        )

    old_status = context.status
    context.status = new_status_enum.value
    context.save(update_fields=['status', 'updated_at'])

    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='context.status_changed',
        payload={
            'context_id': str(context.id),
            'old_status': old_status,
            'new_status': context.status,
            'comment': comment,
        },
    )
    return context
