import uuid
from django.db import models
from common.models import TenantOwnedModel


class CampaignLevel(models.TextChoices):
    LISTING_ONLY = 'listing_only', 'Listing Only'
    BASIC = 'basic', 'Basic'
    STANDARD = 'standard', 'Standard'
    FULL = 'full', 'Full'
    STRATEGIC = 'strategic', 'Strategic'
    SCHOOLS_OUTREACH = 'schools_outreach', 'Schools Outreach'


class CampaignStatus(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'


class DeliverableType(models.TextChoices):
    PR_PLAN = 'pr_plan', 'PR Plan'
    POSTER_DESIGN = 'poster_design', 'Poster Design'
    SOCIAL_MEDIA_PLAN = 'social_media_plan', 'Social Media Plan'
    WEBSITE_PAGE = 'website_page', 'Website Page'
    NEWSLETTER = 'newsletter', 'Newsletter'
    PHOTO_SHOOT = 'photo_shoot', 'Photo Shoot'
    VIDEO_SHOOT = 'video_shoot', 'Video Shoot'
    PROGRAMME_BOOKLET = 'programme_booklet', 'Programme Booklet'
    PRESS_RELEASE = 'press_release', 'Press Release'
    SCHOOL_MAILER = 'school_mailer', 'School Mailer'
    BRAND_TOOLKIT = 'brand_toolkit', 'Brand Toolkit'
    DESIGN_BRIEF = 'design_brief', 'Design Brief'
    ADVERTISING_PLAN = 'advertising_plan', 'Advertising Plan'
    OTHER = 'other', 'Other'


class DeliverableStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PLANNING = 'planning', 'Planning'
    IN_PROGRESS = 'in_progress', 'In Progress'
    REVIEW = 'review', 'Review'
    COMPLETE = 'complete', 'Complete'
    CANCELLED = 'cancelled', 'Cancelled'


class Campaign(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='campaign',
    )
    campaign_level = models.CharField(max_length=20, choices=CampaignLevel.choices)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.PLANNING,
    )
    owner = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='owned_campaigns',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Campaign for {self.operating_context}'


class CampaignDeliverable(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='deliverables',
    )
    deliverable_type = models.CharField(max_length=30, choices=DeliverableType.choices)
    title = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=DeliverableStatus.choices, default=DeliverableStatus.PENDING,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deliverable_evidence',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f'{self.title} ({self.get_deliverable_type_display()})'
