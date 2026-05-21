from rest_framework import serializers
from common.enums import ContextType
from common.serializers import check_tenant_fk, validate_unique_context, ProtectedFieldsMixin
from .models import (
    CalendarIssue, IntakeRequest, IntakeRequestStatus, IntakeRequestType,
    IntakeReview, ProducerAssignment, VenueHold, CalendarSlot,
    Season, Show, Performance, ProductionLicence,
)


REQUEST_TYPE_TO_CONTEXT_TYPE = {
    IntakeRequestType.VENUE_BOOKING: ContextType.VENUE_RENTAL,
    IntakeRequestType.PRODUCTION_PROPOSAL: ContextType.PRODUCTION,
    IntakeRequestType.CO_PRODUCTION_PROPOSAL: ContextType.CO_PRODUCTION,
    IntakeRequestType.YOUTH_PROGRAMME_PROPOSAL: ContextType.YOUTH_PROJECT,
    IntakeRequestType.FESTIVAL_REQUEST: ContextType.FESTIVAL,
    IntakeRequestType.WORKSHOP_SERIES_REQUEST: ContextType.WORKSHOP_SERIES,
    IntakeRequestType.TRAINING_PROGRAMME_REQUEST: ContextType.WORKSHOP_SERIES,
    IntakeRequestType.CIVIC_EVENT_REQUEST: ContextType.CIVIC_EVENT,
    IntakeRequestType.GOVERNANCE_ITEM_REQUEST: ContextType.GOVERNANCE_ITEM,
    IntakeRequestType.INTERNAL_PROGRAMMING_REQUEST: ContextType.PRODUCTION,
}


class IntakeRequestSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = (
        'status', 'submitted_by', 'reviewed_by', 'decided_by',
        'decision_comment', 'decision_at', 'converted_context',
    )

    class Meta:
        model = IntakeRequest
        fields = [
            'id', 'request_type', 'status', 'event_title',
            'client_name', 'client_organisation', 'contact_email', 'contact_phone',
            'requested_start_date', 'requested_end_date', 'preferred_venue',
            'expected_audience', 'ticketing_required', 'technical_summary',
            'foh_notes', 'accessibility_requirements', 'attachments_note', 'notes',
            'submitted_by', 'reviewed_by', 'decided_by', 'decision_comment',
            'decision_at', 'converted_context', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'submitted_by', 'reviewed_by', 'decided_by',
            'decision_comment', 'decision_at', 'converted_context',
            'created_at', 'updated_at',
        ]

    def validate_preferred_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Preferred venue')


class IntakeDecisionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class IntakeConvertSerializer(serializers.Serializer):
    site = serializers.PrimaryKeyRelatedField(queryset=[], required=False)
    venue = serializers.PrimaryKeyRelatedField(queryset=[], required=False, allow_null=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=[])
    department = serializers.PrimaryKeyRelatedField(queryset=[], required=False, allow_null=True)
    priority = serializers.CharField(required=False, default='medium')
    risk_level = serializers.CharField(required=False, default='low')
    budget = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.accounts.models import User
            from apps.structure.models import Department, Site, Venue
            org_id = request.user.organisation_id
            self.fields['site'].queryset = Site.objects.filter(organisation_id=org_id)
            self.fields['venue'].queryset = Venue.objects.filter(organisation_id=org_id)
            self.fields['owner'].queryset = User.objects.filter(organisation_id=org_id)
            self.fields['department'].queryset = Department.objects.filter(organisation_id=org_id)


class IntakeReviewSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = IntakeReview
        fields = [
            'id', 'operating_context', 'reviewed_by', 'review_date',
            'recommendation', 'notes', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)

    def validate_reviewed_by(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Reviewed by')


class ProducerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProducerAssignment
        fields = [
            'id', 'operating_context', 'producer', 'assigned_by',
            'assigned_date', 'is_primary',
        ]
        read_only_fields = ['id', 'assigned_by', 'assigned_date']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_producer(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Producer')


class VenueHoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueHold
        fields = [
            'id', 'operating_context', 'venue', 'space', 'hold_date',
            'hold_type', 'start_time', 'end_time', 'purpose', 'notes',
            'setup_buffer_minutes', 'strike_buffer_minutes', 'expected_audience',
            'held_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'held_by', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_space(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Space')


class CalendarSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarSlot
        fields = [
            'id', 'operating_context', 'venue', 'date',
            'slot_type', 'is_confirmed', 'start_time', 'end_time',
            'setup_buffer_minutes', 'strike_buffer_minutes', 'expected_audience',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')


class CalendarIssueSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'raised_by', 'resolved_by', 'resolved_at', 'resolution_note')

    class Meta:
        model = CalendarIssue
        fields = [
            'id', 'title', 'description', 'operating_context',
            'venue_hold', 'calendar_slot', 'department', 'severity',
            'status', 'due_date', 'raised_by', 'resolved_by',
            'resolved_at', 'resolution_note', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'raised_by', 'resolved_by', 'resolved_at',
            'resolution_note', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_venue_hold(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue hold')

    def validate_calendar_slot(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Calendar slot')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        venue_hold = attrs.get('venue_hold') or getattr(self.instance, 'venue_hold', None)
        calendar_slot = attrs.get('calendar_slot') or getattr(self.instance, 'calendar_slot', None)
        operating_context = attrs.get('operating_context') or getattr(self.instance, 'operating_context', None)
        if venue_hold and operating_context and venue_hold.operating_context_id != operating_context.id:
            raise serializers.ValidationError({'venue_hold': 'Venue hold must belong to the selected Workspace.'})
        if calendar_slot and operating_context and calendar_slot.operating_context_id != operating_context.id:
            raise serializers.ValidationError({'calendar_slot': 'Calendar slot must belong to the selected Workspace.'})
        return attrs


class CalendarIssueActionSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default='')


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'organisation', 'name', 'year', 'start_date', 'end_date',
            'is_active', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organisation', 'created_at', 'updated_at']


class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = [
            'id', 'operating_context', 'season', 'title', 'subtitle', 'status',
            'genre', 'duration_minutes', 'interval_count', 'age_restriction',
            'content_advisory', 'synopsis', 'producer_name', 'is_own_production',
            'is_co_production', 'budget_approved', 'revenue_target',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_season(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Season')


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = [
            'id', 'show', 'venue', 'space', 'performance_date', 'start_time',
            'doors_time', 'capacity', 'is_cancelled', 'cancellation_reason',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_show(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Show')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_space(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Space')


# ── Production Licences ───────────────────────────────────────────────────────

class ProductionLicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLicence
        fields = [
            'id', 'operating_context', 'licensing_body', 'status',
            'licence_number', 'application_date', 'approval_date', 'expiry_date',
            'fee_amount', 'fee_paid_date', 'certificate_reference',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')


# ── Production Journal ────────────────────────────────────────────────────────

from .models import ProductionJournalEntry  # noqa: E402


class ProductionJournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionJournalEntry
        fields = [
            'id', 'operating_context', 'entry_date', 'entry_type', 'title', 'body',
            'author', 'is_confidential', 'requires_follow_up', 'follow_up_by',
            'follow_up_completed', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_author(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Author')
