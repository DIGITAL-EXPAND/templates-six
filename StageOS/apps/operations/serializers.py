from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, validate_unique_context, ProtectedFieldsMixin, require_non_negative,
)
from .models import FOHPlan, ShowDayChecklist, Incident, ShowCall, PostShowReport, StaffCall


class FOHPlanSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = FOHPlan
        fields = [
            'id', 'operating_context', 'ushers', 'security', 'cleaning',
            'vip_count', 'accessibility_provisions', 'hospitality_notes',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['ushers', 'security', 'cleaning', 'vip_count'])
        return attrs


class ShowDayChecklistSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('is_checked', 'checked_by', 'checked_at')
    class Meta:
        model = ShowDayChecklist
        fields = [
            'id', 'foh_plan', 'item', 'is_checked',
            'checked_by', 'checked_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'is_checked', 'checked_by', 'checked_at', 'created_at', 'updated_at',
        ]

    def validate_foh_plan(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'FOH plan')

    def validate_checked_by(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Checked by')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            'id', 'operating_context', 'foh_plan', 'incident_type',
            'occurred_at', 'description', 'response', 'reported_by',
            'severity', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reported_by', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_foh_plan(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'FOH plan')


class ShowCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowCall
        fields = [
            'id', 'operating_context', 'performance', 'show_date', 'call_time',
            'house_open_time', 'show_start_time', 'expected_audience',
            'technical_notes', 'foh_notes', 'cast_notes', 'production_manager_notes',
            'status', 'distributed_at', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'distributed_at', 'created_by', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_performance(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Performance')


class PostShowReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostShowReport
        fields = [
            'id', 'operating_context', 'performance', 'show_date',
            'actual_start_time', 'actual_end_time', 'actual_audience',
            'walk_ins', 'comps_used', 'incidents_count',
            'technical_issues', 'foh_summary', 'audience_feedback',
            'overall_rating', 'cash_collected', 'card_collected',
            'submitted_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'submitted_by', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_performance(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Performance')


class StaffCallSerializer(serializers.ModelSerializer):
    staff_member_name = serializers.SerializerMethodField(read_only=True)

    def get_staff_member_name(self, obj):
        return obj.staff_member.get_full_name() or obj.staff_member.email

    class Meta:
        model = StaffCall
        fields = [
            'id', 'show_call', 'staff_member', 'staff_member_name',
            'role', 'call_time', 'finish_time', 'status',
            'confirmed_at', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'confirmed_at', 'created_at', 'updated_at']


# ── Liquor Licence & Safety Compliance ───────────────────────────────────────

from .models import LiquorLicence, SafetyComplianceRecord  # noqa: E402


class LiquorLicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquorLicence
        fields = [
            'id', 'venue', 'licence_number', 'licence_holder', 'status',
            'issue_date', 'expiry_date', 'annual_fee', 'last_paid_date',
            'issuing_authority', 'conditions', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')


class SafetyComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyComplianceRecord
        fields = [
            'id', 'compliance_type', 'venue', 'operating_context', 'is_compliant',
            'certificate_number', 'issue_date', 'expiry_date', 'issuing_body',
            'responsible_person', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_venue(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_operating_context(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_responsible_person(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Responsible person')


# ── Union Agreements ──────────────────────────────────────────────────────────

from .models import UnionAgreement, UnionCallRate, CrewCallUnionCheck  # noqa: E402


class UnionCallRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnionCallRate
        fields = [
            'id', 'agreement', 'role_category', 'rate_type', 'minimum_rate',
            'currency', 'effective_date', 'notes',
        ]
        read_only_fields = ['id']

    def validate_agreement(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Agreement')


class UnionAgreementSerializer(serializers.ModelSerializer):
    rates = UnionCallRateSerializer(many=True, read_only=True)

    class Meta:
        model = UnionAgreement
        fields = [
            'id', 'union', 'agreement_name', 'effective_date', 'expiry_date',
            'is_active', 'minimum_call_hours', 'overtime_threshold_hours',
            'overtime_multiplier', 'meal_break_provision_hours', 'turnaround_hours',
            'notes', 'created_at', 'rates',
        ]
        read_only_fields = ['id', 'created_at']


class CrewCallUnionCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewCallUnionCheck
        fields = [
            'id', 'staff_call', 'union_agreement', 'applicable_rate',
            'scheduled_hours', 'minimum_call_met', 'turnaround_met',
            'estimated_cost', 'compliance_notes', 'checked_at',
        ]
        read_only_fields = ['id', 'checked_at']

    def validate_staff_call(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Staff call')

    def validate_union_agreement(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Union agreement')

    def validate_applicable_rate(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Applicable rate')


# ── Maintenance & Facilities ──────────────────────────────────────────────────

from .models import (  # noqa: E402
    MaintenanceTicket, MaintenanceSchedule, InspectionRecord, VenueDowntime,
    AudienceComplaint, AccessibilityRequirement, LateSeatingPolicy,
)


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'category',
            'priority', 'status', 'venue', 'location_detail',
            'is_production_impacting', 'affected_production',
            'reported_by', 'assigned_to', 'target_resolution_date',
            'resolved_date', 'resolution_notes', 'cost_estimate',
            'actual_cost', 'contractor_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ticket_number', 'created_at', 'updated_at']

    def validate_venue(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_affected_production(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Affected production')

    def validate_reported_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Reported by')

    def validate_assigned_to(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Assigned to')


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'id', 'title', 'category', 'venue', 'frequency',
            'assigned_to', 'last_completed_date', 'next_due_date',
            'is_active', 'instructions', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_venue(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_assigned_to(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Assigned to')


class InspectionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionRecord
        fields = [
            'id', 'inspection_type', 'venue', 'inspection_date',
            'inspector_name', 'inspector_company', 'passed',
            'certificate_number', 'expiry_date', 'findings',
            'corrective_actions_required', 'next_inspection_date', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')


class VenueDowntimeSerializer(serializers.ModelSerializer):
    downtime_hours = serializers.ReadOnlyField()

    class Meta:
        model = VenueDowntime
        fields = [
            'id', 'venue', 'reason', 'start_datetime', 'end_datetime',
            'is_resolved', 'production_impact', 'ticket',
            'downtime_hours', 'created_at',
        ]
        read_only_fields = ['id', 'downtime_hours', 'created_at']

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_ticket(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Ticket')


# ── Audience Complaints & Accessibility ───────────────────────────────────────

class AudienceComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudienceComplaint
        fields = [
            'id', 'reference_number', 'operating_context', 'complaint_date',
            'complainant_name', 'complainant_email', 'complainant_phone',
            'is_anonymous', 'category', 'description', 'status',
            'assigned_to', 'resolution', 'resolved_date',
            'requires_follow_up', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_assigned_to(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Assigned to')


class AccessibilityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityRequirement
        fields = [
            'id', 'operating_context', 'performance_date', 'requirement_type',
            'patron_name', 'patron_contact', 'details', 'is_confirmed',
            'assigned_to', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_assigned_to(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Assigned to')


class LateSeatingPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LateSeatingPolicy
        fields = [
            'id', 'operating_context', 'cutoff_minutes', 'holding_area',
            'policy_description', 'exceptions_allowed',
            'exception_approval_role', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')
