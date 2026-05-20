from rest_framework import serializers
from .models import Organisation, TenantEntityConfig


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['id', 'name', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantEntityConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantEntityConfig
        fields = [
            'id', 'entity_type', 'executive_authority', 'accounting_authority',
            'auditor_general_client', 'pfma_applicable', 'mfma_applicable',
            'grap_reporting', 'treasury_reporting_required',
            'shareholder_compact_required', 'delegation_framework_required',
            'financial_year_end', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
