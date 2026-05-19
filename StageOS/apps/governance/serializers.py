from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin, require_non_negative
from .models import (
    KPI, KPIEvidence, Risk, CorrectiveAction, ExecutiveAction,
    Budget, BudgetLine, BoardMeeting, BoardResolution,
)


class KPISerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('actual_value',)
    class Meta:
        model = KPI
        fields = [
            'id', 'name', 'owner_department', 'owner_description',
            'target_value', 'actual_value', 'unit',
            'evidence_description', 'reporting_period', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'actual_value', 'created_at', 'updated_at']

    def validate_owner_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner department')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['target_value'])
        return attrs


class KPIEvidenceSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('value_reported',)
    class Meta:
        model = KPIEvidence
        fields = [
            'id', 'kpi', 'operating_context', 'value_reported',
            'evidence_document', 'reported_by', 'reported_date', 'notes',
        ]
        read_only_fields = ['id', 'value_reported', 'reported_by', 'reported_date']

    def validate_kpi(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'KPI')

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')


class ReportKPISerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, default='', allow_blank=True)
    context = serializers.UUIDField(required=False, allow_null=True, default=None)
    evidence_document = serializers.UUIDField(required=False, allow_null=True, default=None)

    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError('Value cannot be negative.')
        return value


class RiskSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'closed_date', 'closed_by')
    class Meta:
        model = Risk
        fields = [
            'id', 'operating_context', 'title', 'description', 'risk_level',
            'owner', 'status', 'mitigation_plan',
            'raised_date', 'closed_date', 'closed_by',
        ]
        read_only_fields = ['id', 'status', 'raised_date', 'closed_date', 'closed_by']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_owner(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner')


class CloseRiskSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, default='', allow_blank=True)


class CorrectiveActionSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'completed_date', 'completed_by')
    class Meta:
        model = CorrectiveAction
        fields = [
            'id', 'risk', 'action', 'owner', 'due_date', 'status',
            'completed_date', 'completed_by', 'evidence_document',
        ]
        read_only_fields = ['id', 'status', 'completed_date', 'completed_by']

    def validate_risk(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Risk')

    def validate_owner(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')


class ExecutiveActionSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = (
        'status', 'created_by', 'acknowledged_by', 'acknowledged_at',
        'completed_by', 'completed_at', 'linked_task',
        'linked_risk', 'linked_corrective_action',
    )

    class Meta:
        model = ExecutiveAction
        fields = [
            'id', 'action_type', 'status', 'title', 'reason', 'instruction',
            'operating_context', 'target_type', 'target_id', 'department',
            'assigned_to', 'due_date', 'created_by', 'acknowledged_by',
            'acknowledged_at', 'completed_by', 'completed_at', 'linked_task',
            'linked_risk', 'linked_corrective_action', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'created_by', 'acknowledged_by', 'acknowledged_at',
            'completed_by', 'completed_at', 'linked_task',
            'linked_risk', 'linked_corrective_action', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Workspace')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate_assigned_to(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Assigned user')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        action_type = attrs.get('action_type', getattr(self.instance, 'action_type', ''))
        reason = attrs.get('reason', getattr(self.instance, 'reason', ''))
        instruction = attrs.get('instruction', getattr(self.instance, 'instruction', ''))
        if action_type in {
            'request_change', 'flag_issue', 'flag_risk',
            'assign_corrective_action', 'decline', 'override',
            'request_more_information', 'escalate',
        } and not reason.strip():
            raise serializers.ValidationError({'reason': 'A reason is required for this executive action.'})
        if action_type in {'request_change', 'assign_corrective_action', 'request_more_information'} and not instruction.strip():
            raise serializers.ValidationError({'instruction': 'An instruction is required for this executive action.'})
        return attrs


class ExecutiveActionStatusSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class BudgetLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLine
        fields = [
            'id', 'budget', 'category', 'description',
            'quantity', 'unit_cost', 'amount',
            'actual_amount', 'variance', 'notes', 'sort_order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'amount', 'variance', 'created_at', 'updated_at']

    def validate_budget(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Budget')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['quantity', 'unit_cost', 'actual_amount'])
        return attrs


class BudgetSerializer(serializers.ModelSerializer):
    lines = BudgetLineSerializer(many=True, read_only=True)
    net_position = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'operating_context', 'name', 'financial_year', 'status',
            'total_income', 'total_expenditure', 'net_position',
            'approved_by', 'approved_at', 'notes',
            'created_at', 'updated_at', 'lines',
        ]
        read_only_fields = [
            'id', 'total_income', 'total_expenditure', 'net_position',
            'approved_by', 'approved_at', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')


class BoardResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardResolution
        fields = [
            'id', 'meeting', 'resolution_number', 'title', 'description',
            'status', 'proposed_by', 'seconded_by',
            'votes_for', 'votes_against', 'votes_abstained',
            'action_required', 'action_owner', 'action_due_date', 'action_completed',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_meeting(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Board meeting')

    def validate_action_owner(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Action owner')


class BoardMeetingSerializer(serializers.ModelSerializer):
    resolutions = BoardResolutionSerializer(many=True, read_only=True)

    class Meta:
        model = BoardMeeting
        fields = [
            'id', 'meeting_type', 'title', 'meeting_date', 'venue', 'status',
            'quorum_required', 'quorum_achieved', 'members_present', 'apologies',
            'agenda_document', 'minutes_document',
            'chaired_by', 'minuted_by', 'notes',
            'created_at', 'updated_at', 'resolutions',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_agenda_document(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Agenda document')

    def validate_minutes_document(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Minutes document')
