import uuid
from django.db import models
from common.models import TenantOwnedModel


class ArtistStatus(models.TextChoices):
    DOCUMENTS_INCOMPLETE = 'documents_incomplete', 'Documents Incomplete'
    CONTRACT_READY = 'contract_ready', 'Contract Ready'
    CONTRACTED = 'contracted', 'Contracted'
    PAYMENT_READY = 'payment_ready', 'Payment Ready'


class ArtistDocumentType(models.TextChoices):
    ID_COPY = 'id_copy', 'ID Copy'
    BANK_CONFIRMATION = 'bank_confirmation', 'Bank Confirmation'
    TAX_NUMBER = 'tax_number', 'Tax Number'
    CONTRACT = 'contract', 'Contract'
    RIDER = 'rider', 'Rider'
    OTHER = 'other', 'Other'


class ArtistDocumentStatus(models.TextChoices):
    MISSING = 'missing', 'Missing'
    UPLOADED = 'uploaded', 'Uploaded'
    VERIFIED = 'verified', 'Verified'
    REJECTED = 'rejected', 'Rejected'


class ArtistEngagementStatus(models.TextChoices):
    PROPOSED = 'proposed', 'Proposed'
    CONFIRMED = 'confirmed', 'Confirmed'
    CONTRACTED = 'contracted', 'Contracted'
    PERFORMED = 'performed', 'Performed'
    CANCELLED = 'cancelled', 'Cancelled'


class Artist(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legal_name = models.CharField(max_length=255)
    professional_name = models.CharField(max_length=255, blank=True)
    discipline = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    standard_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=30, choices=ArtistStatus.choices,
        default=ArtistStatus.DOCUMENTS_INCOMPLETE,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['legal_name']

    def __str__(self):
        return self.professional_name or self.legal_name


class ArtistDocument(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='artist_documents',
    )
    document_type = models.CharField(max_length=30, choices=ArtistDocumentType.choices)
    document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='artist_documents',
    )
    file_name = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=ArtistDocumentStatus.choices,
        default=ArtistDocumentStatus.MISSING,
    )
    verified_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_artist_docs',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['document_type']

    def __str__(self):
        return f'{self.artist} — {self.get_document_type_display()} [{self.status}]'


class ArtistEngagement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(
        Artist, on_delete=models.PROTECT, related_name='engagements',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='artist_engagements',
    )
    role = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contract = models.ForeignKey(
        'contracts.ContractRecord', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='artist_engagements',
    )
    status = models.CharField(
        max_length=20, choices=ArtistEngagementStatus.choices,
        default=ArtistEngagementStatus.PROPOSED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('artist', 'operating_context')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.artist} as {self.role} on {self.operating_context}'


class PaymentMilestone(models.TextChoices):
    DEPOSIT = 'deposit', 'Deposit (50% on signing)'
    BALANCE = 'balance', 'Balance (before performance)'
    FINAL = 'final', 'Final (post-performance)'
    FULL = 'full', 'Full (single payment)'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    INVOICE_RECEIVED = 'invoice_received', 'Invoice Received'
    APPROVED = 'approved', 'Approved for Payment'
    PAID = 'paid', 'Paid'
    DISPUTED = 'disputed', 'Disputed'


class ArtistPayment(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    engagement = models.ForeignKey(
        ArtistEngagement, on_delete=models.CASCADE, related_name='payments',
    )
    milestone = models.CharField(max_length=20, choices=PaymentMilestone.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING,
    )
    due_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_artist_payments',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f'{self.engagement} — {self.get_milestone_display()} [{self.status}]'
