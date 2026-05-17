import uuid
from django.db import models
from common.models import TenantOwnedModel


class BeeLevel(models.TextChoices):
    LEVEL_1 = 'level_1', 'Level 1'
    LEVEL_2 = 'level_2', 'Level 2'
    LEVEL_3 = 'level_3', 'Level 3'
    LEVEL_4 = 'level_4', 'Level 4'
    NON_COMPLIANT = 'non_compliant', 'Non-Compliant'


class SupplierStatus(models.TextChoices):
    DOCUMENTS_INCOMPLETE = 'documents_incomplete', 'Documents Incomplete'
    PENDING_VERIFICATION = 'pending_verification', 'Pending Verification'
    READY = 'ready', 'Ready'
    SUSPENDED = 'suspended', 'Suspended'
    BLACKLISTED = 'blacklisted', 'Blacklisted'


class SupplierDocumentType(models.TextChoices):
    CSD_REPORT = 'csd_report', 'CSD Report'
    TAX_STATUS = 'tax_status', 'Tax Status'
    BANK_CONFIRMATION = 'bank_confirmation', 'Bank Confirmation'
    COMPANY_PROFILE = 'company_profile', 'Company Profile'
    BEE_CERTIFICATE = 'bee_certificate', 'BEE Certificate'
    INSURANCE = 'insurance', 'Insurance'
    OTHER = 'other', 'Other'


class DocumentStatus(models.TextChoices):
    MISSING = 'missing', 'Missing'
    UPLOADED = 'uploaded', 'Uploaded'
    VERIFIED = 'verified', 'Verified'
    REJECTED = 'rejected', 'Rejected'


class EngagementStatus(models.TextChoices):
    PROPOSED = 'proposed', 'Proposed'
    CONFIRMED = 'confirmed', 'Confirmed'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class PaymentPackStatus(models.TextChoices):
    AWAITING_CSD = 'awaiting_csd', 'Awaiting CSD'
    READY_FOR_ERP = 'ready_for_erp', 'Ready for ERP'
    SENT_TO_ERP = 'sent_to_erp', 'Sent to ERP'
    PAID = 'paid', 'Paid'
    REJECTED = 'rejected', 'Rejected'


class Supplier(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    panel = models.CharField(max_length=255, blank=True)
    csd_number = models.CharField(max_length=50, blank=True)
    csd_verified = models.BooleanField(default=False)
    csd_verified_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_suppliers',
    )
    csd_verified_at = models.DateTimeField(null=True, blank=True)
    bee_level = models.CharField(max_length=20, choices=BeeLevel.choices, blank=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=30, choices=SupplierStatus.choices,
        default=SupplierStatus.DOCUMENTS_INCOMPLETE,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SupplierDocument(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='supplier_documents',
    )
    document_type = models.CharField(max_length=30, choices=SupplierDocumentType.choices)
    document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='supplier_documents',
    )
    file_name = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.MISSING,
    )
    verified_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_supplier_docs',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['document_type']

    def __str__(self):
        return f'{self.supplier.name} — {self.get_document_type_display()} [{self.status}]'


class SupplierEngagement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='engagements',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='supplier_engagements',
    )
    role = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=EngagementStatus.choices, default=EngagementStatus.PROPOSED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('supplier', 'operating_context')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.supplier.name} — {self.role} on {self.operating_context}'


class PaymentPack(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_engagement = models.ForeignKey(
        SupplierEngagement, on_delete=models.PROTECT, related_name='payment_packs',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='payment_packs',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentPackStatus.choices, default=PaymentPackStatus.AWAITING_CSD,
    )
    erp_reference = models.CharField(max_length=100, blank=True)
    submitted_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.erp_reference or self.id} [{self.status}]'
