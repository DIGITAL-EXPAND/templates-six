from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin, require_non_negative
from .models import (
    KPI, KPIEvidence, Risk, CorrectiveAction, ExecutiveAction,
    Budget, BudgetLine, BoardMeeting, BoardResolution,
    DelegationMatrix, DelegationRule,
    ShareholderCompact, CompactTarget, CompactActual, FundingTranche,
    IUFWIncident, IUFWInvestigation, IUFWRecovery,
    AGAuditRequest, AGAuditEvidence,
    ConflictOfInterest, PerformanceReport,
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


# ── Delegation Framework ──────────────────────────────────────────────────────

class DelegationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DelegationRule
        fields = [
            'id', 'matrix', 'category', 'action_description', 'delegated_to',
            'threshold_amount', 'requires_countersign', 'countersign_level',
            'requires_board_approval', 'notes',
        ]
        read_only_fields = ['id']

    def validate_matrix(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Delegation matrix')


class DelegationMatrixSerializer(serializers.ModelSerializer):
    rules = DelegationRuleSerializer(many=True, read_only=True)

    class Meta:
        model = DelegationMatrix
        fields = [
            'id', 'name', 'version', 'effective_date', 'is_active',
            'approved_by', 'notes', 'created_at', 'rules',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_approved_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Approved by')


# ── Shareholder Compact ───────────────────────────────────────────────────────

class CompactActualSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompactActual
        fields = [
            'id', 'target', 'quarter', 'actual_value', 'variance_notes',
            'reported_by', 'reported_at', 'evidence_reference',
        ]
        read_only_fields = ['id', 'reported_by', 'reported_at']

    def validate_target(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Compact target')


class CompactTargetSerializer(serializers.ModelSerializer):
    actuals = CompactActualSerializer(many=True, read_only=True)

    class Meta:
        model = CompactTarget
        fields = [
            'id', 'compact', 'category', 'indicator_name', 'baseline_value',
            'target_value', 'unit', 'weight_percent',
            'q1_target', 'q2_target', 'q3_target', 'q4_target', 'actuals',
        ]
        read_only_fields = ['id']

    def validate_compact(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Shareholder compact')


class FundingTrancheSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingTranche
        fields = [
            'id', 'compact', 'tranche_number', 'description', 'amount',
            'due_date', 'received_date', 'is_received', 'notes',
        ]
        read_only_fields = ['id']

    def validate_compact(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Shareholder compact')


class ShareholderCompactSerializer(serializers.ModelSerializer):
    targets = CompactTargetSerializer(many=True, read_only=True)
    tranches = FundingTrancheSerializer(many=True, read_only=True)

    class Meta:
        model = ShareholderCompact
        fields = [
            'id', 'financial_year', 'status', 'executive_authority',
            'signed_date', 'review_date', 'total_grant_allocation', 'notes',
            'created_at', 'updated_at', 'targets', 'tranches',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── IUFW ─────────────────────────────────────────────────────────────────────

class IUFWIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IUFWIncident
        fields = [
            'id', 'reference_number', 'iufw_type', 'status', 'financial_year',
            'description', 'amount', 'discovered_date',
            'responsible_person', 'responsible_description', 'root_cause',
            'reported_to_board', 'reported_to_ag', 'agsa_reference',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at']

    def validate_responsible_person(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Responsible person')


class IUFWInvestigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IUFWInvestigation
        fields = [
            'id', 'incident', 'investigator', 'investigator_description',
            'commenced_date', 'completed_date', 'findings', 'recommendation',
            'disciplinary_recommended', 'criminal_referral_recommended', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_incident(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'IUFW incident')

    def validate_investigator(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Investigator')


class IUFWRecoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = IUFWRecovery
        fields = [
            'id', 'incident', 'amount_recovered', 'recovery_date',
            'recovery_method', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_incident(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'IUFW incident')


# ── AG Audit ──────────────────────────────────────────────────────────────────

class AGAuditEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AGAuditEvidence
        fields = [
            'id', 'audit', 'category', 'description', 'document_reference',
            'provided_by', 'provided_date', 'is_provided', 'ag_query_ref',
            'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_audit(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'AG audit request')

    def validate_provided_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Provided by')


class AGAuditRequestSerializer(serializers.ModelSerializer):
    evidence_items = AGAuditEvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = AGAuditRequest
        fields = [
            'id', 'financial_year', 'audit_type', 'status',
            'audit_coordinator', 'notice_date', 'fieldwork_start', 'fieldwork_end',
            'draft_report_date', 'final_report_date', 'audit_outcome',
            'management_response', 'notes', 'created_at', 'updated_at', 'evidence_items',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_audit_coordinator(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Audit coordinator')


# ── Conflict of Interest ──────────────────────────────────────────────────────

class ConflictOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictOfInterest
        fields = [
            'id', 'declarant', 'declaration_date', 'financial_year',
            'status', 'category', 'description', 'entity_name',
            'matter_reference', 'recusal_details', 'is_annual_declaration',
            'witnessed_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_declarant(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Declarant')

    def validate_witnessed_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Witnessed by')


# ── Performance Report ────────────────────────────────────────────────────────

class PerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReport
        fields = [
            'id', 'compact', 'quarter', 'status',
            'reporting_period_start', 'reporting_period_end',
            'executive_summary', 'key_achievements', 'challenges',
            'corrective_actions', 'financial_narrative',
            'prepared_by', 'approved_by', 'submitted_date', 'approved_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'approved_by', 'submitted_date', 'approved_date',
            'created_at', 'updated_at',
        ]

    def validate_compact(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Shareholder compact')

    def validate_prepared_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Prepared by')
