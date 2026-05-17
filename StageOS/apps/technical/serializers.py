from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, validate_unique_context, ProtectedFieldsMixin,
    require_non_negative, require_ordered_dates,
)
from .models import TechnicalRider, CrewRequirement, EquipmentRequirement


class TechnicalRiderSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = TechnicalRider
        fields = [
            'id', 'operating_context', 'lighting', 'sound', 'av',
            'crew_size', 'load_in_date', 'strike_date', 'status',
            'approved_by', 'approved_at', 'special_requirements',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'approved_by', 'approved_at', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['crew_size'])
        require_ordered_dates(attrs, 'load_in_date', 'strike_date')
        return attrs


class CrewRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewRequirement
        fields = ['id', 'rider', 'role', 'quantity', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rider(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Rider')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['quantity'])
        return attrs


class EquipmentRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRequirement
        fields = [
            'id', 'rider', 'item', 'quantity', 'source', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rider(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Rider')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['quantity'])
        return attrs
