import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from common.models import TenantOwnedModel
from common.enums import ContextType, ContextStatus, Priority, RiskLevel


class TicketingProvider(models.TextChoices):
    WEBTICKETS = 'webtickets', 'Webtickets'
    COMPUTICKET = 'computicket', 'Computicket'
    TICKETPRO = 'ticketpro', 'Ticketpro'
    INTERNAL_RSVP = 'internal_rsvp', 'Internal RSVP'
    NOT_TICKETED = 'not_ticketed', 'Not Ticketed'
    TO_CONFIRM = 'to_confirm', 'To Confirm'


class CampaignLevel(models.TextChoices):
    LISTING_ONLY = 'listing_only', 'Listing Only'
    BASIC = 'basic', 'Basic'
    STANDARD = 'standard', 'Standard'
    FULL = 'full', 'Full'
    STRATEGIC = 'strategic', 'Strategic'
    SCHOOLS_OUTREACH = 'schools_outreach', 'Schools Outreach'


class OperatingContext(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    context_type = models.CharField(
        max_length=20, choices=ContextType.choices, default=ContextType.PRODUCTION,
    )
    status = models.CharField(
        max_length=20, choices=ContextStatus.choices, default=ContextStatus.DRAFT,
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM,
    )
    risk_level = models.CharField(
        max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW,
    )
    synopsis = models.TextField(blank=True)

    # Location
    site = models.ForeignKey(
        'structure.Site', on_delete=models.PROTECT, related_name='operating_contexts',
    )
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.PROTECT,
        null=True, blank=True, related_name='operating_contexts',
    )
    primary_space = models.ForeignKey(
        'structure.Space', on_delete=models.PROTECT,
        null=True, blank=True, related_name='operating_contexts',
    )
    department = models.ForeignKey(
        'structure.Department', on_delete=models.PROTECT,
        null=True, blank=True, related_name='operating_contexts',
    )
    owner = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='owned_contexts',
    )

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    opening_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)

    # Financial
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Marketing & ticketing
    ticketing_provider = models.CharField(
        max_length=20, choices=TicketingProvider.choices, blank=True,
    )
    campaign_level = models.CharField(
        max_length=20, choices=CampaignLevel.choices, blank=True,
    )

    # Governance
    kpi_link = models.CharField(max_length=255, blank=True)
    readiness_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_public = models.BooleanField(default=False)

    # Sub-events (festivals, youth showcases, etc.)
    parent_context = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sub_contexts',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.get_status_display()}]'
