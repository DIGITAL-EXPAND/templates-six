import uuid
from django.db import models
from common.models import TenantOwnedModel


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    information_officer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='information_officer_for',
    )
    popia_privacy_notice_url = models.URLField(blank=True)
    default_retention_days = models.PositiveIntegerField(default=365)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EntityType(models.TextChoices):
    PFMA_SCHEDULE_3A = 'pfma_schedule_3a', 'PFMA Schedule 3A Public Entity'
    MFMA_MUNICIPAL = 'mfma_municipal', 'MFMA Municipal Entity'
    SECTION_21_NPO = 'section_21_npo', 'Section 21 NPO'
    PRIVATE_COMPANY = 'private_company', 'Private Company'


class TenantEntityConfig(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=30, choices=EntityType.choices, default=EntityType.PFMA_SCHEDULE_3A)
    executive_authority = models.CharField(max_length=255, blank=True, help_text='Shareholder/executive authority name')
    accounting_authority = models.CharField(max_length=255, blank=True, help_text='Board/accounting authority name')
    auditor_general_client = models.BooleanField(default=True)
    pfma_applicable = models.BooleanField(default=True)
    mfma_applicable = models.BooleanField(default=False)
    grap_reporting = models.BooleanField(default=True)
    treasury_reporting_required = models.BooleanField(default=True)
    shareholder_compact_required = models.BooleanField(default=True)
    delegation_framework_required = models.BooleanField(default=True)
    financial_year_end = models.CharField(max_length=5, default='03-31', help_text='MM-DD format')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('organisation',)]
        verbose_name = 'Entity Configuration'
