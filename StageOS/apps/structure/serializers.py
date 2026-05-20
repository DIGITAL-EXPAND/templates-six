from rest_framework import serializers
from common.serializers import check_tenant_fk
from .models import (
    ApprovalPolicy,
    Department,
    EvidenceRule,
    ModuleActivation,
    OrganisationOperatingModel,
    Position,
    Site,
    SOPTemplate,
    Space,
    UserDepartmentMembership,
    Venue,
    VenueCapacityConfig,
    VenueRentalEnquiry,
    VenueRentalQuote,
)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'code', 'address', 'city', 'province', 'country', 'is_active']
        read_only_fields = ['id']


class VenueSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = Venue
        fields = ['id', 'name', 'site', 'site_name', 'venue_type', 'capacity', 'description', 'is_active']
        read_only_fields = ['id', 'site_name']

    def validate_site(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Site')


class SpaceSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)

    class Meta:
        model = Space
        fields = ['id', 'name', 'venue', 'venue_name', 'space_type', 'capacity', 'is_bookable']
        read_only_fields = ['id', 'venue_name']

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')


class DepartmentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True, default=None)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'site', 'site_name', 'department_type', 'is_active']
        read_only_fields = ['id', 'site_name']

    def validate_site(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Site')


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True, default=None)
    reports_to_title = serializers.CharField(source='reports_to.title', read_only=True, default=None)

    class Meta:
        model = Position
        fields = [
            'id', 'title', 'code', 'description', 'department', 'department_name',
            'site', 'site_name', 'level', 'authority_level',
            'reports_to', 'reports_to_title', 'is_active',
            'is_manager_position', 'is_specialist_position', 'is_external_position',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'department_name', 'site_name', 'reports_to_title', 'created_at', 'updated_at']

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate_site(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Site')

    def validate_reports_to(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Position')


class OrganisationOperatingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationOperatingModel
        fields = [
            'id', 'name', 'model_type', 'description', 'is_active',
            'is_default', 'configuration', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDepartmentMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True, default=None)

    class Meta:
        model = UserDepartmentMembership
        fields = [
            'id', 'user', 'user_email', 'site', 'site_name', 'department',
            'department_name', 'position', 'position_title', 'authority_level',
            'reports_to', 'is_primary', 'can_manage_department',
            'can_assign_work', 'can_approve_work',
            'can_view_department_summary', 'can_raise_department_issue',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_email', 'site_name', 'department_name', 'position_title', 'created_at', 'updated_at']

    def validate_user(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'User')

    def validate_site(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Site')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate_position(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Position')

    def validate_reports_to(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Membership')


class ModuleActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleActivation
        fields = ['id', 'module_key', 'label', 'is_enabled', 'configuration', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApprovalPolicySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = ApprovalPolicy
        fields = [
            'id', 'department', 'department_name', 'module_key', 'record_type',
            'approval_scope', 'required_authority_level',
            'allow_executive_override', 'override_requires_reason',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'department_name', 'created_at', 'updated_at']

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')


class EvidenceRuleSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = EvidenceRule
        fields = [
            'id', 'department', 'department_name', 'module_key', 'record_type',
            'work_type', 'evidence_required', 'accepted_mime_types',
            'requires_review', 'reviewer_authority_level',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'department_name', 'created_at', 'updated_at']

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')


class SOPTemplateSerializer(serializers.ModelSerializer):
    operating_model_name = serializers.CharField(source='operating_model.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = SOPTemplate
        fields = [
            'id', 'operating_model', 'operating_model_name', 'workspace_type',
            'department', 'department_name', 'title', 'description',
            'sequence', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'operating_model_name', 'department_name', 'created_at', 'updated_at']

    def validate_operating_model(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating model')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')


class VenueCapacityConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCapacityConfig
        fields = ['id', 'space', 'configuration', 'capacity', 'notes', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_space(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Space')


# ── Venue Rental ──────────────────────────────────────────────────────────────

class VenueRentalQuoteSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    vat_amount = serializers.SerializerMethodField()
    total_inc_vat = serializers.SerializerMethodField()
    deposit_amount = serializers.SerializerMethodField()

    class Meta:
        model = VenueRentalQuote
        fields = [
            'id', 'enquiry', 'quote_number',
            'venue_hire_fee', 'technical_fee', 'catering_fee', 'security_fee', 'other_fee',
            'vat_rate', 'deposit_percentage', 'valid_until', 'is_accepted', 'notes',
            'subtotal', 'vat_amount', 'total_inc_vat', 'deposit_amount',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_subtotal(self, obj):
        return str(obj.subtotal)

    def get_vat_amount(self, obj):
        return str(obj.vat_amount)

    def get_total_inc_vat(self, obj):
        return str(obj.total_inc_vat)

    def get_deposit_amount(self, obj):
        return str(obj.deposit_amount)

    def validate_enquiry(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Rental enquiry')


class VenueRentalEnquirySerializer(serializers.ModelSerializer):
    quotes = VenueRentalQuoteSerializer(many=True, read_only=True)

    class Meta:
        model = VenueRentalEnquiry
        fields = [
            'id', 'reference_number', 'venue', 'space',
            'client_name', 'client_email', 'client_phone', 'client_organisation',
            'event_type', 'event_name', 'event_date', 'event_end_date', 'setup_date',
            'expected_attendance', 'status', 'assigned_to',
            'special_requirements', 'internal_notes',
            'created_at', 'updated_at', 'quotes',
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at']

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_space(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Space')

    def validate_assigned_to(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Assigned to')
