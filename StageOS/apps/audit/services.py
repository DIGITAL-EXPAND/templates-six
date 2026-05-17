class AuditService:
    @staticmethod
    def record(
        *,
        organisation,
        actor=None,
        event_type,
        target_type='',
        target_id=None,
        old_value='',
        new_value='',
        reason='',
        payload=None,
    ):
        from .models import AuditEvent

        data = payload or {}
        if target_type and 'target_type' not in data:
            data['target_type'] = target_type
        if target_id is not None and 'target_id' not in data:
            data['target_id'] = str(target_id)
        if old_value != '' and 'old_value' not in data:
            data['old_value'] = str(old_value)
        if new_value != '' and 'new_value' not in data:
            data['new_value'] = str(new_value)
        if reason and 'reason' not in data:
            data['reason'] = reason

        return AuditEvent.objects.create(
            organisation=organisation,
            actor=actor,
            event_type=event_type,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else '',
            old_value=str(old_value) if old_value != '' else '',
            new_value=str(new_value) if new_value != '' else '',
            reason=reason,
            payload=data,
        )
