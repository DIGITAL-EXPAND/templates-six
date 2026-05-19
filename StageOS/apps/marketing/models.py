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


class SocialPlatform(models.TextChoices):
    FACEBOOK = 'facebook', 'Facebook'
    INSTAGRAM = 'instagram', 'Instagram'
    TWITTER = 'twitter', 'X / Twitter'
    LINKEDIN = 'linkedin', 'LinkedIn'
    TIKTOK = 'tiktok', 'TikTok'
    YOUTUBE = 'youtube', 'YouTube'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    EMAIL = 'email', 'Email Newsletter'


class SocialPostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    PUBLISHED = 'published', 'Published'
    CANCELLED = 'cancelled', 'Cancelled'


class SocialPost(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='social_posts',
    )
    platform = models.CharField(max_length=20, choices=SocialPlatform.choices)
    content = models.TextField()
    media_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=SocialPostStatus.choices, default=SocialPostStatus.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    reach = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    engagements = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='social_posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_at', '-created_at']

    def __str__(self):
        return f'{self.platform}: {self.content[:50]} [{self.status}]'


class AudienceReport(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.CASCADE,
        related_name='audience_report',
    )
    total_attendance = models.PositiveIntegerField(default=0)
    capacity_total = models.PositiveIntegerField(default=0)
    comps_issued = models.PositiveIntegerField(default=0)
    school_groups = models.PositiveIntegerField(default=0)
    average_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    demographics_notes = models.TextField(blank=True)
    feedback_summary = models.TextField(blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_finalised = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def occupancy_rate(self):
        if not self.capacity_total:
            return 0
        return round(self.total_attendance / self.capacity_total * 100, 1)

    def __str__(self):
        return f'Audience Report: {self.operating_context}'
