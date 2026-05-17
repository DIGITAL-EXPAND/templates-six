from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, validate_unique_context, ProtectedFieldsMixin, require_non_negative,
)
from .models import FOHPlan, ShowDayChecklist, Incident


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
