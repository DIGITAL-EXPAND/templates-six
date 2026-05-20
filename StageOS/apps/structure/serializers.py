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
