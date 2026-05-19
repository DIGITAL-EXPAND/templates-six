import uuid
from django.db import models
from common.models import TenantOwnedModel


class SubjectType(models.TextChoices):
    USER = 'user', 'User'
    SUPPLIER = 'supplier', 'Supplier'
    ARTIST = 'artist', 'Artist'
    CLIENT = 'client', 'Client'
    YOUTH_LEARNER = 'youth_learner', 'Youth Learner'


class LawfulBasis(models.TextChoices):
    CONSENT = 'consent', 'Consent'
    LEGITIMATE_INTEREST = 'legitimate_interest', 'Legitimate Interest'
    LEGAL_OBLIGATION = 'legal_obligation', 'Legal Obligation'
    VITAL_INTEREST = 'vital_interest', 'Vital Interest'
    PUBLIC_TASK = 'public_task', 'Public Task'


class DataConsent(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_type = models.CharField(max_length=20, choices=SubjectType.choices)
    subject_id = models.UUIDField()
    lawful_basis = models.CharField(max_length=30, choices=LawfulBasis.choices)
    purpose = models.TextField()
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    consent_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='popia_consent_records',
    )
    withdrawal_date = models.DateTimeField(null=True, blank=True)
    retention_until = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT,
        related_name='recorded_consents',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Consent: {self.subject_type} {self.subject_id}'
