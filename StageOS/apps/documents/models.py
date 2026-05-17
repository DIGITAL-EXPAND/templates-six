import uuid
from django.db import models
from common.models import TenantOwnedModel


class DocumentType(models.TextChoices):
    BRIEF = 'brief', 'Brief'
    PLAN = 'plan', 'Plan'
    PROPOSAL = 'proposal', 'Proposal'
    CONTRACT = 'contract', 'Contract'
    RIDER = 'rider', 'Rider'
    REPORT = 'report', 'Report'
    EVIDENCE = 'evidence', 'Evidence'
    CSD_PACK = 'csd_pack', 'CSD Pack'
    SHOW_REPORT = 'show_report', 'Show Report'
    CLOSEOUT = 'closeout', 'Closeout'
    MARKETING_ASSET = 'marketing_asset', 'Marketing Asset'
    CONSENT_FORM = 'consent_form', 'Consent Form'
    ATTENDANCE_REGISTER = 'attendance_register', 'Attendance Register'
    ASSESSMENT = 'assessment', 'Assessment'
    OTHER = 'other', 'Other'


class Document(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='documents',
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file_name = models.CharField(max_length=500)
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    storage_ref = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True)
    version = models.IntegerField(default=1)
    uploaded_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='uploaded_documents',
    )
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_document_type_display()})'


class EvidenceSubmission(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='evidence_submissions',
    )
    task = models.ForeignKey(
        'tasks.Task', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='evidence_submissions',
    )
    document = models.ForeignKey(
        'documents.Document', on_delete=models.PROTECT, related_name='evidence_submissions',
    )
    submitted_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='submitted_evidence',
    )
    submission_note = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='accepted_evidence',
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected = models.BooleanField(default=False)
    rejected_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='rejected_evidence',
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Evidence: {self.document} for {self.task}'
