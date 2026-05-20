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


class RequisitionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    PO_ISSUED = 'po_issued', 'PO Issued'
    CANCELLED = 'cancelled', 'Cancelled'


class PurchaseOrderStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ISSUED = 'issued', 'Issued'
    PARTIALLY_DELIVERED = 'partially_delivered', 'Partially Delivered'
    DELIVERED = 'delivered', 'Delivered'
    INVOICED = 'invoiced', 'Invoiced'
    PAID = 'paid', 'Paid'
    CANCELLED = 'cancelled', 'Cancelled'
    DISPUTED = 'disputed', 'Disputed'


class PurchaseRequisition(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='purchase_requisitions',
    )
    requisition_number = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='purchase_requisitions',
    )
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ZAR')
    required_by_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=RequisitionStatus.choices, default=RequisitionStatus.DRAFT)
    requested_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='purchase_requisitions',
    )
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_requisitions',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PR-{self.requisition_number or self.id}: {self.title} [{self.status}]'


class PurchaseOrder(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisition = models.ForeignKey(
        PurchaseRequisition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='purchase_orders',
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='purchase_orders',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='purchase_orders',
    )
    po_number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ZAR')
    status = models.CharField(max_length=30, choices=PurchaseOrderStatus.choices, default=PurchaseOrderStatus.DRAFT)
    issued_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    three_quotes_obtained = models.BooleanField(default=False)
    csd_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PO-{self.po_number or self.id}: {self.supplier} [{self.status}]'


# ── CSD Verification ──────────────────────────────────────────────────────────

class CSDVerificationStatus(models.TextChoices):
    NOT_VERIFIED = 'not_verified', 'Not Verified'
    PENDING = 'pending', 'Verification Pending'
    VERIFIED = 'verified', 'Verified on CSD'
    FAILED = 'failed', 'Verification Failed'
    EXPIRED = 'expired', 'Verification Expired (>30 days)'
    EXCLUDED = 'excluded', 'Excluded / Blocked Supplier'

class SupplierCSDVerification(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='csd_verifications')
    csd_supplier_number = models.CharField(max_length=100, blank=True)
    verification_status = models.CharField(max_length=20, choices=CSDVerificationStatus.choices, default=CSDVerificationStatus.NOT_VERIFIED)
    verification_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='csd_verifications_performed')
    tax_compliance_status = models.CharField(max_length=20, blank=True, choices=[
        ('compliant', 'Tax Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('unknown', 'Unknown'),
    ])
    tax_clearance_pin = models.CharField(max_length=100, blank=True)
    tax_clearance_expiry = models.DateField(null=True, blank=True)
    bee_level = models.PositiveSmallIntegerField(null=True, blank=True)
    bee_certificate_expiry = models.DateField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    manual_override_notes = models.TextField(blank=True, help_text='Reason if PO approved despite failed CSD check')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-verification_date']
