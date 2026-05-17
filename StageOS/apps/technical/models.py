import uuid
from django.db import models
from common.models import TenantOwnedModel


class RiderStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class EquipmentSource(models.TextChoices):
    IN_HOUSE = 'in_house', 'In House'
    HIRED = 'hired', 'Hired'
    ARTIST_PROVIDED = 'artist_provided', 'Artist Provided'
    SPONSOR = 'sponsor', 'Sponsor'


class TechnicalRider(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='technical_rider',
    )
    lighting = models.TextField(blank=True)
    sound = models.TextField(blank=True)
    av = models.TextField(blank=True)
    crew_size = models.IntegerField(default=0)
    load_in_date = models.DateField(null=True, blank=True)
    strike_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=RiderStatus.choices, default=RiderStatus.DRAFT,
    )
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_riders',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    special_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Rider for {self.operating_context} [{self.status}]'


class CrewRequirement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(
        TechnicalRider, on_delete=models.CASCADE, related_name='crew_requirements',
    )
    role = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['role']

    def __str__(self):
        return f'{self.quantity}x {self.role}'


class EquipmentRequirement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(
        TechnicalRider, on_delete=models.CASCADE, related_name='equipment_requirements',
    )
    item = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    source = models.CharField(max_length=20, choices=EquipmentSource.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item']

    def __str__(self):
        return f'{self.quantity}x {self.item} ({self.source})'
