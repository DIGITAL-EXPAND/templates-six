from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin
from .models import Notification, Task, TaskComment


class TaskSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = Task
        fields = [
            'id', 'operating_context', 'title', 'description', 'department',
            'assigned_to', 'assigned_by', 'work_type', 'due_date', 'priority', 'status',
            'started_at', 'blocked_reason', 'completed_at', 'completed_by', 'evidence_required', 'evidence_provided',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'assigned_by', 'started_at', 'blocked_reason', 'completed_at', 'completed_by',
            'evidence_provided', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate_assigned_to(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Assigned user')


class CompleteTaskSerializer(serializers.Serializer):
    has_evidence = serializers.BooleanField(default=False, required=False)


class TaskActionCommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)


class TaskCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True, default=None)
    author_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'author_email', 'author_name', 'body', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'author_email', 'author_name', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.author is None:
            return None
        full_name = getattr(obj.author, 'full_name', None)
        if full_name:
            return full_name
        parts = [obj.author.first_name, obj.author.last_name]
        return ' '.join(p for p in parts if p).strip() or obj.author.email


class AssignTaskSerializer(serializers.Serializer):
    assigned_to = serializers.UUIDField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor.email', read_only=True, default=None)
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_email', 'actor', 'actor_email',
            'notification_type', 'title', 'message', 'task', 'department',
            'department_name', 'read_at', 'created_at',
        ]
        read_only_fields = fields
