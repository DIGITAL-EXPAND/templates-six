import uuid
from django.db import models
from common.models import TenantOwnedModel


class IntakeRequestType(models.TextChoices):
    VENUE_BOOKING = 'venue_booking', 'Venue Booking Request'
    PRODUCTION_PROPOSAL = 'production_proposal', 'Production Proposal'
    CO_PRODUCTION_PROPOSAL = 'co_production_proposal', 'Co-Production Proposal'
    YOUTH_PROGRAMME_PROPOSAL = 'youth_programme_proposal', 'Youth Programme Proposal'
    FESTIVAL_REQUEST = 'festival_request', 'Festival Request'
    WORKSHOP_SERIES_REQUEST = 'workshop_series_request', 'Workshop Series Request'
    TRAINING_PROGRAMME_REQUEST = 'training_programme_request', 'Training Programme Request'
    CIVIC_EVENT_REQUEST = 'civic_event_request', 'Civic Event Request'
    GOVERNANCE_ITEM_REQUEST = 'governance_item_request', 'Governance Item Request'
    INTERNAL_PROGRAMMING_REQUEST = 'internal_programming_request', 'Internal Programming Request'


class IntakeRequestStatus(models.TextChoices):
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'
    DEFERRED = 'deferred', 'Deferred'
    APPROVED = 'approved', 'Approved'
    DECLINED = 'declined', 'Declined'
    CONVERTED = 'converted', 'Converted'
    ARCHIVED = 'archived', 'Archived'


class RecommendationChoice(models.TextChoices):
    APPROVE = 'approve', 'Approve'
    REJECT = 'reject', 'Reject'
    DEFER = 'defer', 'Defer'
    REQUEST_CHANGES = 'request_changes', 'Request Changes'


class IntakeStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    REVIEWED = 'reviewed', 'Reviewed'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class HoldType(models.TextChoices):
    PROVISIONAL = 'provisional', 'Provisional'
    CONFIRMED = 'confirmed', 'Confirmed'
    BLOCKED = 'blocked', 'Blocked'


class HoldPurpose(models.TextChoices):
    PERFORMANCE = 'performance', 'Performance'
    REHEARSAL = 'rehearsal', 'Rehearsal'
    LOAD_IN = 'load_in', 'Load In'
    STRIKE = 'strike', 'Strike'
    SETUP = 'setup', 'Setup'
    CLASS = 'class', 'Class'
    WORKSHOP = 'workshop', 'Workshop'
    MEETING = 'meeting', 'Meeting'
    OTHER = 'other', 'Other'


class SlotType(models.TextChoices):
    PERFORMANCE = 'performance', 'Performance'
    REHEARSAL = 'rehearsal', 'Rehearsal'
    DARK_DAY = 'dark_day', 'Dark Day'
    MAINTENANCE = 'maintenance', 'Maintenance'
    BLACKOUT = 'blackout', 'Blackout'
    VENUE_UNAVAILABLE = 'venue_unavailable', 'Venue Unavailable'
    LOAD_IN = 'load_in', 'Load In'
    STRIKE = 'strike', 'Strike'
    CHANGEOVER = 'changeover', 'Changeover'


class CalendarIssueSeverity(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class CalendarIssueStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CANCELLED = 'cancelled', 'Cancelled'


class IntakeRequest(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=40, choices=IntakeRequestType.choices)
    status = models.CharField(
        max_length=30, choices=IntakeRequestStatus.choices, default=IntakeRequestStatus.SUBMITTED,
    )
    event_title = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    client_organisation = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    requested_start_date = models.DateField(null=True, blank=True)
    requested_end_date = models.DateField(null=True, blank=True)
    preferred_venue = models.ForeignKey(
        'structure.Venue', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='intake_requests',
    )
    expected_audience = models.PositiveIntegerField(null=True, blank=True)
    ticketing_required = models.BooleanField(default=False)
    technical_summary = models.TextField(blank=True)
    foh_notes = models.TextField(blank=True)
    accessibility_requirements = models.TextField(blank=True)
    attachments_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    submitted_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='submitted_intake_requests',
    )
    reviewed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_intake_requests',
    )
    decided_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='decided_intake_requests',
    )
    decision_comment = models.TextField(blank=True)
    decision_at = models.DateTimeField(null=True, blank=True)
    converted_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='source_intake_request',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_title} [{self.status}]'


class IntakeReview(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='intake_review',
    )
    reviewed_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='intake_reviews',
    )
    review_date = models.DateField()
    recommendation = models.CharField(max_length=20, choices=RecommendationChoice.choices)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=IntakeStatus.choices, default=IntakeStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Intake: {self.operating_context} [{self.status}]'


class ProducerAssignment(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='producer_assignments',
    )
    producer = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='producer_assignments',
    )
    assigned_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='producer_assignments_made',
    )
    assigned_date = models.DateField(auto_now_add=True)
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = [('operating_context', 'producer')]
        ordering = ['-assigned_date']

    def __str__(self):
        return f'{self.producer} on {self.operating_context}'


class VenueHold(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='venue_holds',
    )
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.PROTECT, related_name='holds',
    )
    space = models.ForeignKey(
        'structure.Space', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='holds',
    )
    hold_date = models.DateField()
    hold_type = models.CharField(max_length=20, choices=HoldType.choices)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    setup_buffer_minutes = models.PositiveIntegerField(default=0)
    strike_buffer_minutes = models.PositiveIntegerField(default=0)
    expected_audience = models.PositiveIntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=20, choices=HoldPurpose.choices)
    notes = models.TextField(blank=True)
    held_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='venue_holds',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hold_date', 'start_time']

    def __str__(self):
        return f'{self.venue} on {self.hold_date} ({self.hold_type})'


class CalendarSlot(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='calendar_slots',
    )
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.PROTECT, related_name='calendar_slots',
    )
    date = models.DateField()
    slot_type = models.CharField(max_length=20, choices=SlotType.choices)
    is_confirmed = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    setup_buffer_minutes = models.PositiveIntegerField(default=0)
    strike_buffer_minutes = models.PositiveIntegerField(default=0)
    expected_audience = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.slot_type} at {self.venue} on {self.date}'


class CalendarIssue(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='calendar_issues',
    )
    venue_hold = models.ForeignKey(
        VenueHold, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='issues',
    )
    calendar_slot = models.ForeignKey(
        CalendarSlot, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='issues',
    )
    department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='calendar_issues',
    )
    severity = models.CharField(
        max_length=10, choices=CalendarIssueSeverity.choices,
        default=CalendarIssueSeverity.MEDIUM,
    )
    status = models.CharField(
        max_length=20, choices=CalendarIssueStatus.choices,
        default=CalendarIssueStatus.OPEN,
    )
    due_date = models.DateField(null=True, blank=True)
    raised_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='raised_calendar_issues',
    )
    resolved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_calendar_issues',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-created_at']

    def __str__(self):
        return f'{self.title} [{self.status}]'


class ShowStatus(models.TextChoices):
    PROGRAMMING = 'programming', 'In Programming'
    CONFIRMED = 'confirmed', 'Confirmed'
    ON_SALE = 'on_sale', 'On Sale'
    RUNNING = 'running', 'Running'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'


class Season(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        'organisations.Organisation', on_delete=models.CASCADE, related_name='seasons',
    )
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'name']
        unique_together = [('organisation', 'name', 'year')]

    def __str__(self):
        return f'{self.name} ({self.year})'


class Show(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='show',
    )
    season = models.ForeignKey(
        Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='shows',
    )
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=ShowStatus.choices, default=ShowStatus.PROGRAMMING)
    genre = models.CharField(max_length=100, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    interval_count = models.PositiveIntegerField(default=0)
    age_restriction = models.CharField(max_length=50, blank=True)
    content_advisory = models.TextField(blank=True)
    synopsis = models.TextField(blank=True)
    producer_name = models.CharField(max_length=255, blank=True)
    is_own_production = models.BooleanField(default=False)
    is_co_production = models.BooleanField(default=False)
    budget_approved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.status}]'


class Performance(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='performances')
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.PROTECT, related_name='performances',
    )
    space = models.ForeignKey(
        'structure.Space', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='performances',
    )
    performance_date = models.DateField()
    start_time = models.TimeField()
    doors_time = models.TimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['performance_date', 'start_time']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk is None:  # only on create
            overlapping = Performance.objects.filter(
                venue=self.venue,
                performance_date=self.performance_date,
                is_cancelled=False,
            ).exclude(pk=self.pk)
            if self.space:
                overlapping = overlapping.filter(space=self.space)
            for other in overlapping:
                # simple time overlap check
                if not (self.start_time >= other.start_time and
                        self.start_time >= other.start_time):
                    raise ValidationError(
                        f'Double-booking conflict with {other.show.title} at {other.start_time}'
                    )

    def __str__(self):
        return f'{self.show.title} — {self.performance_date} {self.start_time}'


# ── Production Licences ───────────────────────────────────────────────────────

class LicensingBody(models.TextChoices):
    SAMRO = 'samro', 'SAMRO (Performing Rights)'
    RISA = 'risa', 'RISA (Recording Rights)'
    CAPASSO = 'capasso', 'CAPASSO (Composers & Authors)'
    DALRO = 'dalro', 'DALRO (Dramatic/Literary)'
    FILMSA = 'filmsa', 'FILMSA (Film)'
    OTHER = 'other', 'Other Licensing Body'

class LicenceStatus(models.TextChoices):
    NOT_REQUIRED = 'not_required', 'Not Required'
    REQUIRED = 'required', 'Required — Not Applied'
    APPLIED = 'applied', 'Application Submitted'
    APPROVED = 'approved', 'Licence Approved'
    PAID = 'paid', 'Licence Fee Paid'
    RECEIVED = 'received', 'Licence Certificate Received'
    EXPIRED = 'expired', 'Expired'
    REJECTED = 'rejected', 'Rejected / Refused'

class ProductionLicence(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.CASCADE, related_name='licences',
    )
    licensing_body = models.CharField(max_length=20, choices=LicensingBody.choices)
    status = models.CharField(max_length=20, choices=LicenceStatus.choices, default=LicenceStatus.REQUIRED)
    licence_number = models.CharField(max_length=100, blank=True)
    application_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_paid_date = models.DateField(null=True, blank=True)
    certificate_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('organisation', 'operating_context', 'licensing_body')]
        ordering = ['operating_context', 'licensing_body']


# ── Production Journal ────────────────────────────────────────────────────────

class JournalEntryType(models.TextChoices):
    GENERAL = 'general', 'General Note'
    INCIDENT = 'incident', 'Incident'
    DECISION = 'decision', 'Decision Made'
    CHANGE = 'change', 'Change / Deviation'
    ACHIEVEMENT = 'achievement', 'Achievement'
    CONCERN = 'concern', 'Concern Raised'
    ACTION = 'action', 'Action Required'

class ProductionJournalEntry(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.CASCADE, related_name='journal_entries',
    )
    entry_date = models.DateField()
    entry_type = models.CharField(max_length=20, choices=JournalEntryType.choices, default=JournalEntryType.GENERAL)
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries')
    is_confidential = models.BooleanField(default=False)
    requires_follow_up = models.BooleanField(default=False)
    follow_up_by = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_date', '-created_at']


# ── Setlist Works ─────────────────────────────────────────────────────────────

class SetlistWork(TenantOwnedModel):
    """Individual musical/dramatic work performed — for SAMRO/RISA/CAPASSO reporting."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    performance = models.ForeignKey('Performance', on_delete=models.CASCADE, related_name='setlist_works')
    title = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, blank=True)
    arranger = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    isrc_code = models.CharField(max_length=20, blank=True, help_text='International Standard Recording Code')
    iswc_code = models.CharField(max_length=20, blank=True, help_text='International Standard Musical Work Code')
    duration_minutes = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_original_work = models.BooleanField(default=False)
    is_public_domain = models.BooleanField(default=False)
    licensing_body = models.CharField(max_length=20, blank=True, choices=[
        ('samro', 'SAMRO'), ('risa', 'RISA'), ('capasso', 'CAPASSO'),
        ('dalro', 'DALRO'), ('none', 'None Required'),
    ])
    order = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order', 'title']


# ── Co-Production ─────────────────────────────────────────────────────────────

class CoProducerRole(models.TextChoices):
    LEAD_PRODUCER = 'lead_producer', 'Lead Producer'
    CO_PRODUCER = 'co_producer', 'Co-Producer'
    PRESENTING_PARTNER = 'presenting_partner', 'Presenting Partner'
    FUNDING_PARTNER = 'funding_partner', 'Funding Partner'
    TOURING_PARTNER = 'touring_partner', 'Touring Partner'

class CoProducer(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.CASCADE, related_name='co_producers')
    partner_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=CoProducerRole.choices)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    cost_share_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='% of total costs borne by this partner')
    revenue_share_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='% of net revenue due to this partner')
    upfront_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CoProductionSettlement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.CASCADE, related_name='coproduction_settlements')
    settlement_date = models.DateField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_position = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'), ('reviewed', 'Reviewed'), ('agreed', 'Agreed by All Partners'), ('paid', 'Settled / Paid'),
    ], default='draft')
    settlement_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CoProductionSettlementLine(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    settlement = models.ForeignKey(CoProductionSettlement, on_delete=models.CASCADE, related_name='lines')
    co_producer = models.ForeignKey(CoProducer, on_delete=models.CASCADE, related_name='settlement_lines')
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)


# ── Touring Productions ───────────────────────────────────────────────────────

class TouringProduction(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField('contexts.OperatingContext', on_delete=models.CASCADE, related_name='touring_info')
    is_outgoing = models.BooleanField(default=True, help_text='True = we are touring out; False = incoming touring production')
    tour_manager = models.CharField(max_length=255, blank=True)
    transport_provider = models.CharField(max_length=255, blank=True)
    accommodation_notes = models.TextField(blank=True)
    per_diem_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    technical_advance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TouringVenueDate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    touring_production = models.ForeignKey(TouringProduction, on_delete=models.CASCADE, related_name='venues')
    venue_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    performance_date = models.DateField()
    load_in_date = models.DateField(null=True, blank=True)
    load_out_date = models.DateField(null=True, blank=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'), ('tentative', 'Tentative'), ('cancelled', 'Cancelled'),
    ], default='tentative')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['performance_date']


# ── Recurring Productions ─────────────────────────────────────────────────────

class RecurrenceFrequency(models.TextChoices):
    WEEKLY = 'weekly', 'Weekly'
    FORTNIGHTLY = 'fortnightly', 'Fortnightly'
    MONTHLY = 'monthly', 'Monthly'
    ANNUALLY = 'annually', 'Annually (same season each year)'

class RecurringProduction(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=15, choices=RecurrenceFrequency.choices)
    base_operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='recurrence_template', help_text='The original production this recurs from')
    is_active = models.BooleanField(default=True)
    next_occurrence_date = models.DateField(null=True, blank=True)
    auto_create = models.BooleanField(default=False, help_text='Auto-create new OperatingContext on each cycle')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
