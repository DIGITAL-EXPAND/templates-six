from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin, require_non_negative
from .models import Artist, ArtistDocument, ArtistEngagement, ArtistPayment, PaymentStatus


class ArtistSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = Artist
        fields = [
            'id', 'legal_name', 'professional_name', 'discipline',
            'contact_email', 'contact_phone', 'standard_fee',
            'status', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['standard_fee'])
        return attrs


class ArtistDocumentSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'verified_by', 'verified_at')
    class Meta:
        model = ArtistDocument
        fields = [
            'id', 'artist', 'document_type', 'document', 'file_name',
            'status', 'verified_by', 'verified_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'verified_by', 'verified_at', 'created_at', 'updated_at']

    def validate_artist(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Artist')

    def validate_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Document')


class ArtistEngagementSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = ArtistEngagement
        fields = [
            'id', 'artist', 'operating_context', 'role', 'fee',
            'contract', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_artist(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Artist')

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_contract(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Contract')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        artist = attrs.get('artist', getattr(self.instance, 'artist', None))
        context = attrs.get('operating_context', getattr(self.instance, 'operating_context', None))
        if artist and context:
            qs = ArtistEngagement.objects.filter(artist=artist, operating_context=context)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    'This artist is already engaged for this operating context.'
                )
        require_non_negative(attrs, ['fee'])
        return attrs


class ArtistPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistPayment
        fields = [
            'id', 'engagement', 'milestone', 'amount', 'status',
            'due_date', 'invoice_number', 'paid_date', 'approved_by',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'approved_by', 'created_at', 'updated_at']

    def validate_engagement(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Engagement')
