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


# ── Cue Sheets ────────────────────────────────────────────────────────────────

class CueType(models.TextChoices):
    LIGHTING = 'lx', 'Lighting (LX)'
    SOUND = 'sq', 'Sound (SQ)'
    FLY = 'fly', 'Fly / Flying'
    AUTOMATION = 'auto', 'Automation'
    PROJECTION = 'proj', 'Projection / Video'
    PYRO = 'pyro', 'Pyrotechnics / SFX'
    STAGE_MANAGEMENT = 'sm', 'Stage Management'
    GENERAL = 'general', 'General'

class CueSheet(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.CASCADE, related_name='cue_sheets')
    version = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=20, choices=CueType.choices)
    is_master = models.BooleanField(default=False)
    prepared_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='prepared_cue_sheets')
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_cue_sheets')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'version']

class CueLine(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cue_sheet = models.ForeignKey(CueSheet, on_delete=models.CASCADE, related_name='lines')
    cue_number = models.CharField(max_length=20, help_text='e.g. Q1, LX-01, SQ-003')
    page_ref = models.CharField(max_length=20, blank=True)
    action = models.TextField()
    standby_note = models.CharField(max_length=255, blank=True)
    follow_on = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'cue_number']


# ── Props & Wardrobe ──────────────────────────────────────────────────────────

class PropCondition(models.TextChoices):
    EXCELLENT = 'excellent', 'Excellent'
    GOOD = 'good', 'Good'
    FAIR = 'fair', 'Fair — Minor Repairs Needed'
    POOR = 'poor', 'Poor — Repair Required'
    WRITTEN_OFF = 'written_off', 'Written Off'

class PropsItem(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True, choices=[
        ('furniture', 'Furniture'), ('hand_prop', 'Hand Prop'), ('set_dressing', 'Set Dressing'),
        ('weapon', 'Weapon / Replica'), ('food', 'Food / Edible'), ('electrical', 'Electrical Prop'), ('other', 'Other'),
    ])
    condition = models.CharField(max_length=15, choices=PropCondition.choices, default=PropCondition.GOOD)
    storage_location = models.CharField(max_length=255, blank=True)
    is_hired = models.BooleanField(default=False)
    hire_company = models.CharField(max_length=255, blank=True)
    hire_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hire_return_date = models.DateField(null=True, blank=True)
    current_production = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='props')
    is_available = models.BooleanField(default=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WardrobeItem(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=[
        ('costume', 'Costume'), ('accessory', 'Accessory'), ('footwear', 'Footwear'),
        ('headwear', 'Headwear'), ('wig', 'Wig / Hair'), ('makeup', 'Makeup'), ('other', 'Other'),
    ])
    character = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=50, blank=True)
    condition = models.CharField(max_length=15, choices=PropCondition.choices, default=PropCondition.GOOD)
    is_hired = models.BooleanField(default=False)
    hire_company = models.CharField(max_length=255, blank=True)
    hire_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hire_return_date = models.DateField(null=True, blank=True)
    current_production = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='wardrobe_items')
    assigned_to_performer = models.CharField(max_length=255, blank=True)
    storage_location = models.CharField(max_length=255, blank=True)
    cleaning_required = models.BooleanField(default=False)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
