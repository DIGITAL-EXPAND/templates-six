from rest_framework import serializers
from common.enums import ContextStatus
from common.serializers import (
    check_tenant_fk, ProtectedFieldsMixin, require_non_negative, require_ordered_dates,
)
from apps.structure.models import Site, Venue
from apps.accounts.models import User
from .models import OperatingContext

_VALID_STATUS_VALUES = [s.value for s in ContextStatus]


class SiteInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'city']


class VenueInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'venue_type']


class OwnerInlineSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']


class OperatingContextSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    site_detail = SiteInlineSerializer(source='site', read_only=True)
    venue_detail = VenueInlineSerializer(source='venue', read_only=True)
    owner_detail = OwnerInlineSerializer(source='owner', read_only=True)

    class Meta:
        model = OperatingContext
        fields = [
            'id', 'title', 'context_type', 'status', 'priority', 'risk_level',
            'synopsis',
            'site', 'site_detail',
            'venue', 'venue_detail',
            'primary_space', 'department',
            'owner', 'owner_detail',
            'start_date', 'end_date', 'opening_date', 'closing_date',
            'budget', 'actual_spend',
            'ticketing_provider', 'campaign_level', 'kpi_link',
            'readiness_score', 'is_public', 'parent_context',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at',
            'site_detail', 'venue_detail', 'owner_detail',
        ]

    def validate_site(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Site')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_primary_space(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Space')

    def validate_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Department')

    def validate_owner(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner')

    def validate_parent_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Parent context')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['budget', 'actual_spend'])
        require_ordered_dates(attrs, 'start_date', 'end_date')
        require_ordered_dates(attrs, 'opening_date', 'closing_date')
        return attrs


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    comment = serializers.CharField(required=False, default='', allow_blank=True)

    def validate_status(self, value):
        normalised = value.lower()
        if normalised not in _VALID_STATUS_VALUES:
            raise serializers.ValidationError(
                f"'{value}' is not a valid status. Valid values: {', '.join(_VALID_STATUS_VALUES)}."
            )
        return normalised
