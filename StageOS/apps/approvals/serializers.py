from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin
from .models import ApprovalRoute, ApprovalStep, ApprovalRequest, ApprovalDecision


class ApprovalRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRoute
        fields = [
            'id', 'name', 'context_type', 'description',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApprovalStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = [
            'id', 'route', 'step_number', 'name',
            'approver_department', 'approver_role_description', 'can_delegate',
        ]
        read_only_fields = ['id']

    def validate_route(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Route')

    def validate_approver_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Approver department')


class ApprovalRequestSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('decision', 'decided_by', 'decided_at')
    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'operating_context', 'approval_step', 'requested_by',
            'requested_at', 'decision', 'decided_by', 'decided_at',
            'decision_comment', 'evidence_reviewed',
        ]
        read_only_fields = [
            'id', 'requested_by', 'requested_at',
            'decision', 'decided_by', 'decided_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_approval_step(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Approval step')

    def validate_evidence_reviewed(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')


class ApprovalDecisionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, default='', allow_blank=True)
    evidence = serializers.UUIDField(required=False, allow_null=True, default=None)
