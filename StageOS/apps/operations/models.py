import uuid
from django.db import models
from common.models import TenantOwnedModel


class FOHStatus(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    CONFIRMED = 'confirmed', 'Confirmed'
    ACTIVE = 'active', 'Active'
    CLOSED = 'closed', 'Closed'


class IncidentType(models.TextChoices):
    PATRON_COMPLAINT = 'patron_complaint', 'Patron Complaint'
    ACCESSIBILITY_ISSUE = 'accessibility_issue', 'Accessibility Issue'
    SAFETY_INCIDENT = 'safety_incident', 'Safety Incident'
    EQUIPMENT_FAILURE = 'equipment_failure', 'Equipment Failure'
    LATE_START = 'late_start', 'Late Start'
    MEDICAL = 'medical', 'Medical'
    SECURITY_BREACH = 'security_breach', 'Security Breach'
    OTHER = 'other', 'Other'


class IncidentSeverity(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class FOHPlan(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='foh_plan',
    )
    ushers = models.IntegerField(default=0)
    security = models.IntegerField(default=0)
    cleaning = models.IntegerField(default=0)
    vip_count = models.IntegerField(default=0)
    accessibility_provisions = models.TextField(blank=True)
    hospitality_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=FOHStatus.choices, default=FOHStatus.PLANNING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'FOH Plan: {self.operating_context} [{self.status}]'


class ShowDayChecklist(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    foh_plan = models.ForeignKey(
        FOHPlan, on_delete=models.CASCADE, related_name='checklist_items',
    )
    item = models.CharField(max_length=255)
    is_checked = models.BooleanField(default=False)
    checked_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='checked_items',
    )
    checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item']

    def __str__(self):
        return f'[{"x" if self.is_checked else " "}] {self.item}'


class Incident(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='incidents',
    )
    foh_plan = models.ForeignKey(
        FOHPlan, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='incidents',
    )
    incident_type = models.CharField(max_length=30, choices=IncidentType.choices)
    occurred_at = models.DateTimeField()
    description = models.TextField()
    response = models.TextField(blank=True)
    reported_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='reported_incidents',
    )
    severity = models.CharField(max_length=10, choices=IncidentSeverity.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-occurred_at']

    def __str__(self):
        return f'{self.incident_type} at {self.operating_context} [{self.severity}]'


class ShowCallStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    DISTRIBUTED = 'distributed', 'Distributed'
    CONFIRMED = 'confirmed', 'Confirmed'


class ShowCall(TenantOwnedModel):
    """The daily show-day briefing document sent to all departments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='show_calls',
    )
    performance = models.ForeignKey(
        'programming.Performance', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='show_calls',
    )
    show_date = models.DateField()
    call_time = models.TimeField()
    house_open_time = models.TimeField(null=True, blank=True)
    show_start_time = models.TimeField(null=True, blank=True)
    expected_audience = models.PositiveIntegerField(null=True, blank=True)
    technical_notes = models.TextField(blank=True)
    foh_notes = models.TextField(blank=True)
    cast_notes = models.TextField(blank=True)
    production_manager_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ShowCallStatus.choices, default=ShowCallStatus.DRAFT)
    distributed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='show_calls',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-show_date', '-call_time']

    def __str__(self):
        return f'Show Call — {self.operating_context} on {self.show_date}'


class PostShowReport(TenantOwnedModel):
    """Completed after each performance: actuals vs plan."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='post_show_reports',
    )
    performance = models.ForeignKey(
        'programming.Performance', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='post_show_reports',
    )
    show_date = models.DateField()
    actual_start_time = models.TimeField(null=True, blank=True)
    actual_end_time = models.TimeField(null=True, blank=True)
    actual_audience = models.PositiveIntegerField(default=0)
    walk_ins = models.PositiveIntegerField(default=0)
    comps_used = models.PositiveIntegerField(default=0)
    incidents_count = models.PositiveIntegerField(default=0)
    technical_issues = models.TextField(blank=True)
    foh_summary = models.TextField(blank=True)
    audience_feedback = models.TextField(blank=True)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    submitted_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='post_show_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-show_date']

    def __str__(self):
        return f'Post-Show: {self.operating_context} on {self.show_date}'


class StaffCallRole(models.TextChoices):
    STAGE_MANAGER = 'stage_manager', 'Stage Manager'
    DEPUTY_SM = 'deputy_sm', 'Deputy Stage Manager'
    LIGHTING_OP = 'lighting_op', 'Lighting Operator'
    SOUND_OP = 'sound_op', 'Sound Operator'
    FOLLOW_SPOT = 'follow_spot', 'Follow Spot Operator'
    FLY_OP = 'fly_op', 'Fly Operator'
    HEAD_OF_WARDROBE = 'head_of_wardrobe', 'Head of Wardrobe'
    WARDROBE_ASSISTANT = 'wardrobe_assistant', 'Wardrobe Assistant'
    HEAD_USHER = 'head_usher', 'Head Usher'
    USHER = 'usher', 'Usher'
    BOX_OFFICE = 'box_office', 'Box Office'
    SECURITY = 'security', 'Security'
    FRONT_OF_HOUSE_MANAGER = 'foh_manager', 'Front of House Manager'
    PRODUCTION_MANAGER = 'production_manager', 'Production Manager'
    OTHER = 'other', 'Other'


class StaffCallStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'


class StaffCall(TenantOwnedModel):
    """Individual staff member assignment to a performance or show call."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    show_call = models.ForeignKey(
        ShowCall, on_delete=models.CASCADE, related_name='staff_calls',
    )
    staff_member = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='staff_calls',
    )
    role = models.CharField(max_length=30, choices=StaffCallRole.choices)
    call_time = models.TimeField()
    finish_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=StaffCallStatus.choices, default=StaffCallStatus.SCHEDULED,
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['call_time', 'role']
        unique_together = [('show_call', 'staff_member', 'role')]

    def __str__(self):
        return f'{self.staff_member} as {self.get_role_display()} @ {self.call_time}'


# ── Liquor Licence ────────────────────────────────────────────────────────────

class LiquorLicenceStatus(models.TextChoices):
    NOT_APPLICABLE = 'not_applicable', 'Not Applicable'
    REQUIRED = 'required', 'Required — Not Applied'
    APPLIED = 'applied', 'Application Submitted'
    APPROVED = 'approved', 'Approved'
    ACTIVE = 'active', 'Active / Paid'
    RENEWAL_DUE = 'renewal_due', 'Renewal Due'
    EXPIRED = 'expired', 'Expired'
    SUSPENDED = 'suspended', 'Suspended'

class LiquorLicence(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey('structure.Venue', on_delete=models.PROTECT, related_name='liquor_licences')
    licence_number = models.CharField(max_length=100, blank=True)
    licence_holder = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=LiquorLicenceStatus.choices, default=LiquorLicenceStatus.REQUIRED)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    annual_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_paid_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(max_length=255, blank=True)
    conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ── Safety Compliance ─────────────────────────────────────────────────────────

class SafetyComplianceType(models.TextChoices):
    FIRE_CERTIFICATE = 'fire_certificate', 'Fire Safety Certificate (CoC)'
    EVACUATION_PLAN = 'evacuation_plan', 'Evacuation Plan'
    CROWD_MANAGEMENT = 'crowd_management', 'Crowd Management Plan'
    FIRST_AID = 'first_aid', 'First Aid Compliance'
    OHS_INSPECTION = 'ohs_inspection', 'OHS Inspection'
    PUBLIC_LIABILITY = 'public_liability', 'Public Liability Insurance'
    STRUCTURAL_CERT = 'structural_cert', 'Structural Certificate'

class SafetyComplianceRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compliance_type = models.CharField(max_length=25, choices=SafetyComplianceType.choices)
    venue = models.ForeignKey('structure.Venue', on_delete=models.PROTECT, null=True, blank=True, related_name='safety_records')
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='safety_records')
    is_compliant = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_body = models.CharField(max_length=255, blank=True)
    responsible_person = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='safety_records')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['compliance_type', 'expiry_date']


# ── Union Agreements ──────────────────────────────────────────────────────────

class UnionBody(models.TextChoices):
    SAGA = 'saga', 'SAGA (S.A. Guild of Actors)'
    MUSA = 'musa', 'MUSA (Musicians Union of SA)'
    EQUITY = 'equity', 'Equity'
    SAEW = 'saew', 'SAEW (S.A. Entertainment Workers)'
    SATAWU = 'satawu', 'SATAWU (Transport & Allied Workers)'
    OTHER = 'other', 'Other Union'

class UnionAgreement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    union = models.CharField(max_length=20, choices=UnionBody.choices)
    agreement_name = models.CharField(max_length=255)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    minimum_call_hours = models.DecimalField(max_digits=4, decimal_places=1, default=4, help_text='Minimum call length in hours')
    overtime_threshold_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8)
    overtime_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.5)
    meal_break_provision_hours = models.DecimalField(max_digits=4, decimal_places=1, default=5, help_text='Meal break required after X hours')
    turnaround_hours = models.DecimalField(max_digits=4, decimal_places=1, default=10, help_text='Minimum rest between calls')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UnionCallRate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agreement = models.ForeignKey(UnionAgreement, on_delete=models.CASCADE, related_name='rates')
    role_category = models.CharField(max_length=100, help_text='e.g. Principal Actor, Swing, Ensemble, Stage Manager')
    rate_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily Rate'), ('weekly', 'Weekly Rate'), ('per_performance', 'Per Performance'),
        ('rehearsal', 'Rehearsal Rate'), ('recording', 'Recording Rate'),
    ])
    minimum_rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    effective_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['role_category', 'rate_type']

class CrewCallUnionCheck(TenantOwnedModel):
    """Records union compliance check result for a staff/crew call."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_call = models.ForeignKey('StaffCall', on_delete=models.CASCADE, related_name='union_checks')
    union_agreement = models.ForeignKey(UnionAgreement, on_delete=models.SET_NULL, null=True, blank=True)
    applicable_rate = models.ForeignKey(UnionCallRate, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_hours = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_call_met = models.BooleanField(default=True)
    turnaround_met = models.BooleanField(default=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compliance_notes = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
