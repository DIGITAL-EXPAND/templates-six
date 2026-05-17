import uuid
from django.db import models
from common.models import TenantOwnedModel


class ContractType(models.TextChoices):
    ARTIST_PERFORMANCE = 'artist_performance', 'Artist Performance'
    CO_PRODUCTION = 'co_production', 'Co-Production'
    VENUE_HIRE = 'venue_hire', 'Venue Hire'
    SUPPLIER_SERVICE = 'supplier_service', 'Supplier Service'
    SPONSORSHIP = 'sponsorship', 'Sponsorship'
    FACILITATOR = 'facilitator', 'Facilitator'
    PARTNERSHIP = 'partnership', 'Partnership'
    OTHER = 'other', 'Other'


class CounterpartyType(models.TextChoices):
    ARTIST = 'artist', 'Artist'
    SUPPLIER = 'supplier', 'Supplier'
    PARTNER = 'partner', 'Partner'
    CLIENT = 'client', 'Client'
    GOVERNMENT = 'government', 'Government'
    OTHER = 'other', 'Other'


class ContractStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    LEGAL_REVIEW = 'legal_review', 'Legal Review'
    FINANCE_REVIEW = 'finance_review', 'Finance Review'
    SCM_REVIEW = 'scm_review', 'SCM Review'
    ISSUED = 'issued', 'Issued'
    COUNTER_SIGNED = 'counter_signed', 'Counter Signed'
    SIGNED = 'signed', 'Signed'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'


class SignatureType(models.TextChoices):
    WET = 'wet', 'Wet'
    ELECTRONIC = 'electronic', 'Electronic'
    DIGITAL = 'digital', 'Digital'


class ContractTemplate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=30, choices=ContractType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    template_fields = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} v{self.version}'


class ContractRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='contracts',
    )
    template = models.ForeignKey(
        ContractTemplate, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='records',
    )
    contract_type = models.CharField(max_length=30, choices=ContractType.choices)
    counterparty_name = models.CharField(max_length=255)
    counterparty_type = models.CharField(max_length=20, choices=CounterpartyType.choices)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ZAR')
    status = models.CharField(
        max_length=20, choices=ContractStatus.choices, default=ContractStatus.DRAFT,
    )
    issued_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    signatures_required = models.IntegerField(default=2)
    signatures_received = models.IntegerField(default=0)
    signed_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='signed_contracts',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.counterparty_name} [{self.status}]'


class SignatureRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        ContractRecord, on_delete=models.CASCADE, related_name='signatures',
    )
    signatory_name = models.CharField(max_length=255)
    signatory_role = models.CharField(max_length=255)
    signature_type = models.CharField(max_length=20, choices=SignatureType.choices)
    signed_at = models.DateTimeField(null=True, blank=True)
    is_signed = models.BooleanField(default=False)
    signature_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['signature_order', 'created_at']

    def __str__(self):
        return f'{self.signatory_name} ({self.signatory_role}) — {"signed" if self.is_signed else "pending"}'
