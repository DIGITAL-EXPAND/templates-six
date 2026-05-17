from rest_framework import serializers
from .models import IntegrationProvider, ExternalReference


class IntegrationProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProvider
        fields = [
            'id', 'name', 'provider_type', 'is_enabled',
            'config', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExternalReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalReference
        fields = [
            'id', 'provider', 'operating_context',
            'reference_type', 'external_id', 'metadata', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
