import uuid
from django.db import models
from common.models import TenantOwnedModel


class PatronSegment(models.TextChoices):
    GENERAL = 'general', 'General Audience'
    SUBSCRIBER = 'subscriber', 'Subscriber'
    VIP = 'vip', 'VIP'
    YOUTH = 'youth', 'Youth'
    EDUCATOR = 'educator', 'Educator'
    CORPORATE = 'corporate', 'Corporate'
    MEDIA = 'media', 'Media'
    DONOR = 'donor', 'Donor / Sponsor'


class PatronSource(models.TextChoices):
    WALK_IN = 'walk_in', 'Walk-In'
    ONLINE = 'online', 'Online Booking'
    PHONE = 'phone', 'Phone Booking'
    MAILING_LIST = 'mailing_list', 'Mailing List Sign-Up'
    SCHOOLS = 'schools', 'Schools Programme'
    CORPORATE = 'corporate', 'Corporate Partnership'
    REFERRAL = 'referral', 'Referral'


class Patron(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    segment = models.CharField(max_length=20, choices=PatronSegment.choices, default=PatronSegment.GENERAL)
    source = models.CharField(max_length=20, choices=PatronSource.choices, default=PatronSource.ONLINE)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=50, blank=True)
    marketing_opt_in = models.BooleanField(default=False)
    popia_consent_given = models.BooleanField(default=False)
    popia_consent_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_bookings = models.PositiveIntegerField(default=0)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    first_visit_date = models.DateField(null=True, blank=True)
    last_visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return f'{self.full_name} ({self.email or self.phone})'


class PatronAttendance(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE, related_name='attendances')
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patron_attendances',
    )
    performance = models.ForeignKey(
        'programming.Performance', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patron_attendances',
    )
    attendance_date = models.DateField()
    tickets_count = models.PositiveIntegerField(default=1)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    channel = models.CharField(max_length=20, blank=True)
    is_comp = models.BooleanField(default=False)
    feedback_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    feedback_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attendance_date']

    def __str__(self):
        return f'{self.patron} @ {self.operating_context} on {self.attendance_date}'


class PatronCommunication(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE, related_name='communications')
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    channel = models.CharField(max_length=20, default='email')  # email/sms/phone
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patron_communications',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patron_communications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.subject} → {self.patron}'


# ── Donors / Sponsors ─────────────────────────────────────────────────────────

class DonorCategory(models.TextChoices):
    INDIVIDUAL = 'individual', 'Individual Donor'
    CORPORATE = 'corporate', 'Corporate Sponsor'
    FOUNDATION = 'foundation', 'Foundation / Trust'
    GOVERNMENT = 'government', 'Government Grant'
    ARTS_COUNCIL = 'arts_council', 'Arts Council'
    OTHER = 'other', 'Other'

class DonationStatus(models.TextChoices):
    PROSPECT = 'prospect', 'Prospect'
    PLEDGED = 'pledged', 'Pledged'
    INVOICED = 'invoiced', 'Invoiced'
    RECEIVED = 'received', 'Received'
    ACKNOWLEDGED = 'acknowledged', 'Acknowledged / Receipted'
    LAPSED = 'lapsed', 'Lapsed'

class Donor(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=DonorCategory.choices)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    tax_exempt_number = models.CharField(max_length=100, blank=True, help_text='Section 18A PBO number')
    is_section_18a = models.BooleanField(default=False, help_text='Eligible for Section 18A tax deduction receipts')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Donation(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', help_text='Production or project this donation supports')
    financial_year = models.CharField(max_length=9)
    status = models.CharField(max_length=20, choices=DonationStatus.choices, default=DonationStatus.PLEDGED)
    amount_pledged = models.DecimalField(max_digits=12, decimal_places=2)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pledge_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    section_18a_issued = models.BooleanField(default=False)
    section_18a_date = models.DateField(null=True, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
