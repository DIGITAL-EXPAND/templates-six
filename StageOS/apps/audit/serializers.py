from rest_framework import serializers
from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor.email', read_only=True, default=None)

    class Meta:
        model = AuditEvent
        fields = [
            'id', 'event_type', 'actor_email', 'target_type', 'target_id',
            'old_value', 'new_value', 'reason', 'payload', 'created_at',
        ]
        read_only_fields = fields
