from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, ProtectedFieldsMixin, require_non_negative, require_ordered_dates,
)
from .models import ContractTemplate, ContractRecord, SignatureRecord


class ContractTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractTemplate
        fields = [
            'id', 'name', 'contract_type', 'description',
            'is_active', 'version', 'template_fields',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContractRecordSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'issued_date', 'signatures_received')
    class Meta:
        model = ContractRecord
        fields = [
            'id', 'operating_context', 'template', 'contract_type',
            'counterparty_name', 'counterparty_type', 'value', 'currency',
            'status', 'issued_date', 'effective_date', 'expiry_date',
            'signatures_required', 'signatures_received', 'signed_document',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'issued_date', 'signatures_received', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_template(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Template')

    def validate_signed_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Signed document')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['value', 'signatures_required'])
        require_ordered_dates(attrs, 'effective_date', 'expiry_date')
        return attrs


class SignatureRecordSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('is_signed', 'signed_at')
    class Meta:
        model = SignatureRecord
        fields = [
            'id', 'contract', 'signatory_name', 'signatory_role',
            'signature_type', 'signed_at', 'is_signed', 'signature_order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'signed_at', 'is_signed', 'created_at', 'updated_at']

    def validate_contract(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Contract')
