import uuid
from django.db import models
from django.utils import timezone
from common.models import TenantOwnedModel


class VenueType(models.TextChoices):
    PERFORMANCE = 'performance', 'Performance'
    REHEARSAL = 'rehearsal', 'Rehearsal'
    WORKSHOP = 'workshop', 'Workshop'
    CONFERENCE = 'conference', 'Conference'
    OUTDOOR = 'outdoor', 'Outdoor'
    MULTIPURPOSE = 'multipurpose', 'Multipurpose'
    OTHER = 'other', 'Other'


class SpaceType(models.TextChoices):
    STAGE = 'stage', 'Stage'
    AUDITORIUM = 'auditorium', 'Auditorium'
    FOYER = 'foyer', 'Foyer'
    DRESSING_ROOM = 'dressing_room', 'Dressing Room'
    LOADING_BAY = 'loading_bay', 'Loading Bay'
    CONTROL_BOOTH = 'control_booth', 'Control Booth'
    WORKSHOP = 'workshop', 'Workshop'
    STUDIO = 'studio', 'Studio'
    RESTAURANT = 'restaurant', 'Restaurant'
    VIP_ROOM = 'vip_room', 'VIP Room'
    OTHER = 'other', 'Other'


class DepartmentType(models.TextChoices):
    PROGRAMMING = 'programming', 'Programming'
    MARKETING = 'marketing', 'Marketing'
    TECHNICAL = 'technical', 'Technical'
    OPERATIONS = 'operations', 'Operations'
    FINANCE = 'finance', 'Finance'
    CONTRACTS = 'contracts', 'Contracts'
    TICKETING = 'ticketing', 'Ticketing'
    YOUTH = 'youth', 'Youth'
    GOVERNANCE = 'governance', 'Governance'
    EXECUTIVE = 'executive', 'Executive'
    ICT = 'ict', 'ICT'


class PositionLevel(models.TextChoices):
    EXECUTIVE = 'executive', 'Executive'
    SENIOR_MANAGER = 'senior_manager', 'Senior Manager'
    MANAGER = 'manager', 'Manager'
    OFFICER = 'officer', 'Officer'
    COORDINATOR = 'coordinator', 'Coordinator'
    ASSISTANT = 'assistant', 'Assistant'
    INTERN = 'intern', 'Intern'
    EXTERNAL = 'external', 'External'


class OperatingModelType(models.TextChoices):
    SINGLE_VENUE = 'single_venue', 'Single Venue'
    MULTI_VENUE = 'multi_venue', 'Multi Venue'
    MULTI_THEATRE = 'multi_theatre', 'Multi Theatre'
    INSTITUTIONAL = 'institutional', 'Institutional'
    FESTIVAL = 'festival', 'Festival'
    CUSTOM = 'custom', 'Custom'


class AuthorityLevel(models.TextChoices):
    EXECUTIVE = 'executive', 'Executive'
    GM = 'gm', 'General Manager'
    DEPARTMENT_MANAGER = 'department_manager', 'Department Manager'
    DEPARTMENT_USER = 'department_user', 'Department User'
    SPECIALIST = 'specialist', 'Specialist'
    READ_ONLY = 'read_only', 'Read Only'
    EXTERNAL = 'external', 'External'


class ApprovalScope(models.TextChoices):
    DEPARTMENT_WORK = 'department_work', 'Department Work'
    DEPARTMENT_READINESS = 'department_readiness', 'Department Readiness'
    WORKSPACE_CONVERSION = 'workspace_conversion', 'Workspace Conversion'
    CONTRACT_REVIEW = 'contract_review', 'Contract Review'
    SUPPLIER_READINESS = 'supplier_readiness', 'Supplier Readiness'
    YOUTH_SENSITIVE = 'youth_sensitive', 'Youth Sensitive'
    TECHNICAL_READINESS = 'technical_readiness', 'Technical Readiness'
    MARKETING_READINESS = 'marketing_readiness', 'Marketing Readiness'
    FOH_READINESS = 'foh_readiness', 'FOH Readiness'
    GOVERNANCE_ACTION = 'governance_action', 'Governance Action'


class WorkspaceType(models.TextChoices):
    PRODUCTION = 'production', 'Production'
    VENUE_BOOKING = 'venue_booking', 'Venue Booking'
    YOUTH_PROJECT = 'youth_project', 'Youth Project'
    FESTIVAL = 'festival', 'Festival'
    WORKSHOP = 'workshop', 'Workshop'
    TRAINING_PROGRAMME = 'training_programme', 'Training Programme'
    CIVIC_EVENT = 'civic_event', 'Civic Event'
    GOVERNANCE_ITEM = 'governance_item', 'Governance Item'
    CUSTOM = 'custom', 'Custom'


class OrganisationOperatingModel(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=30, choices=OperatingModelType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organisation', '-is_default', 'name']
        constraints = [
            models.UniqueConstraint(fields=['organisation', 'name'], name='unique_operating_model_name_per_org'),
        ]

    def __str__(self):
        return self.name


class Site(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Venue(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='venues')
    venue_type = models.CharField(max_length=20, choices=VenueType.choices, default=VenueType.PERFORMANCE)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['site', 'name']

    def __str__(self):
        return f'{self.name} — {self.site.name}'


class Space(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='spaces')
    space_type = models.CharField(max_length=20, choices=SpaceType.choices, default=SpaceType.STAGE)
    capacity = models.PositiveIntegerField()
    is_bookable = models.BooleanField(default=True)

    class Meta:
        ordering = ['venue', 'name']

    def __str__(self):
        return f'{self.name} — {self.venue.name}'


class SeatingConfiguration(models.TextChoices):
    THEATRE = 'theatre', 'Theatre (fixed rows)'
    CABARET = 'cabaret', 'Cabaret (round tables)'
    STANDING = 'standing', 'Standing'
    THRUST = 'thrust', 'Thrust'
    TRAVERSE = 'traverse', 'Traverse'
    IN_THE_ROUND = 'in_the_round', 'In the Round'
    PROMENADE = 'promenade', 'Promenade'
    FLEXIBLE = 'flexible', 'Flexible'


class VenueCapacityConfig(TenantOwnedModel):
    """Named capacity configuration for a space (e.g. cabaret vs theatre seating)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='capacity_configs')
    configuration = models.CharField(max_length=20, choices=SeatingConfiguration.choices)
    capacity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['configuration']
        unique_together = [('space', 'configuration')]

    def __str__(self):
        return f'{self.space} — {self.get_configuration_display()} ({self.capacity})'


class Department(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT,
        null=True, blank=True, related_name='departments',
    )
    department_type = models.CharField(max_length=20, choices=DepartmentType.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Position(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    code = models.SlugField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='positions')
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT,
        null=True, blank=True, related_name='positions',
    )
    level = models.CharField(max_length=20, choices=PositionLevel.choices)
    authority_level = models.CharField(
        max_length=30,
        choices=AuthorityLevel.choices,
        default=AuthorityLevel.DEPARTMENT_USER,
    )
    reports_to = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='direct_reports',
    )
    is_manager_position = models.BooleanField(default=False)
    is_specialist_position = models.BooleanField(default=False)
    is_external_position = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'level', 'title']

    def __str__(self):
        return f'{self.title} — {self.department.name}'
 

class UserDepartmentMembership(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='department_memberships')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, blank=True, related_name='user_memberships')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='user_memberships')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='user_memberships')
    authority_level = models.CharField(max_length=30, choices=AuthorityLevel.choices)
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    is_primary = models.BooleanField(default=False)
    can_manage_department = models.BooleanField(default=False)
    can_assign_work = models.BooleanField(default=False)
    can_approve_work = models.BooleanField(default=False)
    can_view_department_summary = models.BooleanField(default=True)
    can_raise_department_issue = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__email', '-is_primary', 'department__name']
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'user', 'department', 'position'],
                name='unique_user_department_position_membership',
            ),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.position.title}'


class ModuleActivation(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_key = models.CharField(max_length=80)
    label = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['module_key']
        constraints = [
            models.UniqueConstraint(fields=['organisation', 'module_key'], name='unique_module_activation_per_org'),
        ]

    def __str__(self):
        return f'{self.label} ({self.module_key})'


class ApprovalPolicy(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name='approval_policies')
    module_key = models.CharField(max_length=80, blank=True)
    record_type = models.CharField(max_length=120, blank=True)
    approval_scope = models.CharField(max_length=40, choices=ApprovalScope.choices)
    required_authority_level = models.CharField(max_length=30, choices=AuthorityLevel.choices)
    allow_executive_override = models.BooleanField(default=True)
    override_requires_reason = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department__name', 'approval_scope']
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'department', 'module_key', 'record_type', 'approval_scope'],
                name='unique_approval_policy_scope',
            ),
        ]

    def __str__(self):
        department = self.department.name if self.department else 'Organisation'
        return f'{department} {self.approval_scope}'


class EvidenceRule(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name='evidence_rules')
    module_key = models.CharField(max_length=80)
    record_type = models.CharField(max_length=120, blank=True)
    work_type = models.CharField(max_length=120, blank=True)
    evidence_required = models.BooleanField(default=True)
    accepted_mime_types = models.JSONField(default=list, blank=True)
    requires_review = models.BooleanField(default=False)
    reviewer_authority_level = models.CharField(max_length=30, choices=AuthorityLevel.choices, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department__name', 'module_key', 'record_type']
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'department', 'module_key', 'record_type', 'work_type'],
                name='unique_evidence_rule_scope',
            ),
        ]

    def __str__(self):
        department = self.department.name if self.department else 'Organisation'
        return f'{department} {self.module_key} evidence'


class SOPTemplate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_model = models.ForeignKey(OrganisationOperatingModel, on_delete=models.PROTECT, related_name='sop_templates')
    workspace_type = models.CharField(max_length=40, choices=WorkspaceType.choices)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name='sop_templates')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['operating_model', 'workspace_type', 'sequence', 'title']
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'operating_model', 'workspace_type', 'department', 'title'],
                name='unique_sop_template_scope',
            ),
        ]

    def __str__(self):
        return self.title


# ── Venue Rental ──────────────────────────────────────────────────────────────

class RentalEnquiryStatus(models.TextChoices):
    NEW = 'new', 'New Enquiry'
    AVAILABILITY_CHECKED = 'availability_checked', 'Availability Checked'
    QUOTE_SENT = 'quote_sent', 'Quote Sent'
    QUOTE_ACCEPTED = 'quote_accepted', 'Quote Accepted'
    AGREEMENT_DRAFTED = 'agreement_drafted', 'Agreement Drafted'
    AGREEMENT_SIGNED = 'agreement_signed', 'Agreement Signed'
    DEPOSIT_RECEIVED = 'deposit_received', 'Deposit Received'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class VenueRentalEnquiry(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=50, blank=True)
    venue = models.ForeignKey('Venue', on_delete=models.PROTECT, related_name='rental_enquiries')
    space = models.ForeignKey('Space', on_delete=models.PROTECT, null=True, blank=True, related_name='rental_enquiries')
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=30, blank=True)
    client_organisation = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=100)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_end_date = models.DateField(null=True, blank=True)
    setup_date = models.DateField(null=True, blank=True)
    expected_attendance = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=25, choices=RentalEnquiryStatus.choices, default=RentalEnquiryStatus.NEW)
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rental_enquiries')
    special_requirements = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import datetime
            year = datetime.date.today().year
            count = VenueRentalEnquiry.objects.filter(organisation=self.organisation).count() + 1
            self.reference_number = f'VRE-{year}-{count:04d}'
        super().save(*args, **kwargs)

class VenueRentalQuote(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enquiry = models.ForeignKey(VenueRentalEnquiry, on_delete=models.CASCADE, related_name='quotes')
    quote_number = models.CharField(max_length=50, blank=True)
    venue_hire_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    technical_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    catering_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    valid_until = models.DateField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.venue_hire_fee + self.technical_fee + self.catering_fee + self.security_fee + self.other_fee

    @property
    def vat_amount(self):
        return self.subtotal * (self.vat_rate / 100)

    @property
    def total_inc_vat(self):
        return self.subtotal + self.vat_amount

    @property
    def deposit_amount(self):
        return self.total_inc_vat * (self.deposit_percentage / 100)


class RentalBooking(TenantOwnedModel):
    """Confirmed rental booking — created when a quote is accepted."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enquiry = models.OneToOneField(VenueRentalEnquiry, on_delete=models.CASCADE, related_name='booking')
    quote = models.OneToOneField(VenueRentalQuote, on_delete=models.CASCADE, related_name='booking')
    booking_number = models.CharField(max_length=50, blank=True)
    confirmed_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'),
        ('setup_in_progress', 'Setup in Progress'),
        ('event_in_progress', 'Event in Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='confirmed')
    contract_signed = models.BooleanField(default=False)
    contract_signed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_number:
            import datetime
            year = datetime.date.today().year
            count = RentalBooking.objects.filter(organisation=self.organisation).count() + 1
            self.booking_number = f'BK-{year}-{count:04d}'
        super().save(*args, **kwargs)


class RentalInvoice(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(RentalBooking, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_type = models.CharField(max_length=20, choices=[
        ('deposit', 'Deposit Invoice'),
        ('balance', 'Balance Invoice'),
        ('full', 'Full Invoice'),
        ('credit_note', 'Credit Note'),
    ])
    invoice_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import datetime
            year = datetime.date.today().year
            count = RentalInvoice.objects.filter(organisation=self.organisation).count() + 1
            self.invoice_number = f'INV-{year}-{count:04d}'
        super().save(*args, **kwargs)


# ── Resident Companies ────────────────────────────────────────────────────────

class ResidencyStatus(models.TextChoices):
    ACTIVE = 'active', 'Active Residency'
    COMPLETED = 'completed', 'Completed'
    SUSPENDED = 'suspended', 'Suspended'
    TERMINATED = 'terminated', 'Terminated'
    PROSPECTIVE = 'prospective', 'Prospective / Negotiating'

class ResidentCompany(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=50, blank=True, choices=[
        ('theatre_company', 'Theatre Company'),
        ('dance_company', 'Dance Company'),
        ('music_ensemble', 'Music Ensemble'),
        ('opera_company', 'Opera Company'),
        ('youth_company', 'Youth Company'),
        ('community_company', 'Community Company'),
        ('other', 'Other'),
    ])
    status = models.CharField(max_length=20, choices=ResidencyStatus.choices, default=ResidencyStatus.ACTIVE)
    venue = models.ForeignKey('Venue', on_delete=models.PROTECT, related_name='resident_companies')
    artistic_director = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    residency_start_date = models.DateField()
    residency_end_date = models.DateField(null=True, blank=True)
    rehearsal_space_allocation = models.TextField(blank=True, help_text='Spaces and hours allocated per week')
    performance_slots_per_year = models.PositiveIntegerField(default=0)
    annual_subsidy = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rental_rate_discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    agreement_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ── Venue Hold Expiry ─────────────────────────────────────────────────────────

class VenueHoldExpiry(TenantOwnedModel):
    """Tracks tentative holds with auto-expiry dates."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enquiry = models.OneToOneField(VenueRentalEnquiry, on_delete=models.CASCADE, related_name='hold_expiry')
    hold_expiry_date = models.DateField()
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
