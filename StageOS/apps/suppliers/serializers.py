from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin, require_non_negative
from .models import Supplier, SupplierDocument, SupplierEngagement, PaymentPack


class SupplierSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'csd_verified', 'csd_verified_by', 'csd_verified_at')
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'category', 'panel', 'csd_number',
            'csd_verified', 'csd_verified_by', 'csd_verified_at',
            'bee_level', 'contact_name', 'contact_email', 'contact_phone',
            'status', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'csd_verified', 'csd_verified_by', 'csd_verified_at',
            'created_at', 'updated_at',
        ]


class SupplierDocumentSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'verified_by', 'verified_at')
    class Meta:
        model = SupplierDocument
        fields = [
            'id', 'supplier', 'document_type', 'document', 'file_name',
            'status', 'verified_by', 'verified_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'verified_by', 'verified_at', 'created_at', 'updated_at']

    def validate_supplier(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Supplier')

    def validate_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Document')


class SupplierEngagementSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = SupplierEngagement
        fields = [
            'id', 'supplier', 'operating_context', 'role', 'value',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_supplier(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Supplier')

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        supplier = attrs.get('supplier', getattr(self.instance, 'supplier', None))
        context = attrs.get('operating_context', getattr(self.instance, 'operating_context', None))
        if supplier and context:
            qs = SupplierEngagement.objects.filter(supplier=supplier, operating_context=context)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    'This supplier is already engaged for this operating context.'
                )
        require_non_negative(attrs, ['value'])
        return attrs


class PaymentPackSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'erp_reference', 'submitted_date')
    class Meta:
        model = PaymentPack
        fields = [
            'id', 'supplier_engagement', 'operating_context', 'amount',
            'status', 'erp_reference', 'submitted_date', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'erp_reference', 'submitted_date', 'created_at', 'updated_at',
        ]

    def validate_supplier_engagement(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Supplier engagement')

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        engagement = attrs.get('supplier_engagement', getattr(self.instance, 'supplier_engagement', None))
        context = attrs.get('operating_context', getattr(self.instance, 'operating_context', None))
        if engagement and context and engagement.operating_context_id != context.id:
            raise serializers.ValidationError(
                'Payment pack operating context must match the supplier engagement context.'
            )
        require_non_negative(attrs, ['amount'])
        return attrs
