import uuid
from django.db import models
from common.models import TenantOwnedModel


class ProviderType(models.TextChoices):
    SSO = 'sso', 'SSO'
    TICKETING = 'ticketing', 'Ticketing'
    ERP = 'erp', 'ERP'
    EMAIL = 'email', 'Email'
    WEBSITE = 'website', 'Website'
    SIGNATURE = 'signature', 'Signature'
    CRM = 'crm', 'CRM'
    STORAGE = 'storage', 'Storage'
    OTHER = 'other', 'Other'


class IntegrationProvider(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    is_enabled = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ExternalReference(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        IntegrationProvider, on_delete=models.CASCADE, related_name='references',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='external_references',
    )
    reference_type = models.CharField(max_length=100)
    external_id = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['provider', 'reference_type']

    def __str__(self):
        return f'{self.provider.name}: {self.reference_type}={self.external_id}'
