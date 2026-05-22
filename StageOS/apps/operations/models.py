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


# ── Maintenance & Facilities ──────────────────────────────────────────────────

class MaintenancePriority(models.TextChoices):
    CRITICAL = 'critical', 'Critical — Production Impacting'
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'

class MaintenanceStatus(models.TextChoices):
    LOGGED = 'logged', 'Logged'
    ASSIGNED = 'assigned', 'Assigned'
    IN_PROGRESS = 'in_progress', 'In Progress'
    AWAITING_PARTS = 'awaiting_parts', 'Awaiting Parts / Contractor'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'
    ESCALATED = 'escalated', 'Escalated to Management'

class MaintenanceCategory(models.TextChoices):
    ELECTRICAL = 'electrical', 'Electrical'
    PLUMBING = 'plumbing', 'Plumbing'
    STRUCTURAL = 'structural', 'Structural'
    HVAC = 'hvac', 'HVAC / Air Conditioning'
    STAGE_EQUIPMENT = 'stage_equipment', 'Stage Equipment'
    LIGHTING_INFRA = 'lighting_infra', 'Lighting Infrastructure'
    SOUND_INFRA = 'sound_infra', 'Sound Infrastructure'
    IT_SYSTEMS = 'it_systems', 'IT / AV Systems'
    SAFETY = 'safety', 'Safety / Fire'
    GROUNDS = 'grounds', 'Grounds / Exterior'
    CLEANING = 'cleaning', 'Cleaning / Hygiene'
    OTHER = 'other', 'Other'

class MaintenanceTicket(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=MaintenanceCategory.choices)
    priority = models.CharField(max_length=10, choices=MaintenancePriority.choices, default=MaintenancePriority.MEDIUM)
    status = models.CharField(max_length=20, choices=MaintenanceStatus.choices, default=MaintenanceStatus.LOGGED)
    venue = models.ForeignKey('structure.Venue', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_tickets')
    location_detail = models.CharField(max_length=255, blank=True, help_text='Specific location e.g. Stage Left, Dressing Room 2')
    is_production_impacting = models.BooleanField(default=False)
    affected_production = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_tickets')
    reported_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_maintenance')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    target_resolution_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contractor_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import datetime
            year = datetime.date.today().year
            count = MaintenanceTicket.objects.filter(organisation=self.organisation).count() + 1
            self.ticket_number = f'MNT-{year}-{count:04d}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class MaintenanceSchedule(TenantOwnedModel):
    """Recurring maintenance tasks — e.g. monthly fire system check."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=MaintenanceCategory.choices)
    venue = models.ForeignKey('structure.Venue', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_schedules')
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'), ('biannual', 'Bi-Annual'), ('annual', 'Annual'),
    ])
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_schedules')
    last_completed_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class InspectionRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection_type = models.CharField(max_length=50, choices=[
        ('fire_safety', 'Fire Safety'), ('electrical_coc', 'Electrical CoC'),
        ('structural', 'Structural'), ('ohs', 'OHS'), ('lift', 'Lift / Elevator'),
        ('pressure_vessel', 'Pressure Vessel'), ('general', 'General'),
    ])
    venue = models.ForeignKey('structure.Venue', on_delete=models.PROTECT, related_name='inspection_records')
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=255)
    inspector_company = models.CharField(max_length=255, blank=True)
    passed = models.BooleanField(default=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)
    corrective_actions_required = models.TextField(blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class VenueDowntime(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey('structure.Venue', on_delete=models.CASCADE, related_name='downtime_records')
    reason = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    production_impact = models.TextField(blank=True)
    ticket = models.ForeignKey(MaintenanceTicket, on_delete=models.SET_NULL, null=True, blank=True, related_name='downtime_records')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def downtime_hours(self):
        if self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return round(delta.total_seconds() / 3600, 1)
        return None


# ── FOH Audience Complaints & Accessibility ───────────────────────────────────

class ComplaintStatus(models.TextChoices):
    RECEIVED = 'received', 'Received'
    ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
    UNDER_REVIEW = 'under_review', 'Under Review'
    RESOLVED = 'resolved', 'Resolved'
    ESCALATED = 'escalated', 'Escalated'
    CLOSED = 'closed', 'Closed'

class AudienceComplaint(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=50, blank=True)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True, related_name='audience_complaints')
    complaint_date = models.DateField()
    complainant_name = models.CharField(max_length=255, blank=True)
    complainant_email = models.EmailField(blank=True)
    complainant_phone = models.CharField(max_length=30, blank=True)
    is_anonymous = models.BooleanField(default=False)
    category = models.CharField(max_length=30, choices=[
        ('service', 'Customer Service'), ('facility', 'Facility / Venue'),
        ('technical', 'Technical / Show Quality'), ('safety', 'Safety Concern'),
        ('accessibility', 'Accessibility'), ('staff', 'Staff Conduct'),
        ('ticketing', 'Ticketing / Pricing'), ('other', 'Other'),
    ])
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ComplaintStatus.choices, default=ComplaintStatus.RECEIVED)
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='complaint_assignments')
    resolution = models.TextField(blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    requires_follow_up = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import datetime
            year = datetime.date.today().year
            count = AudienceComplaint.objects.filter(organisation=self.organisation).count() + 1
            self.reference_number = f'COMP-{year}-{count:04d}'
        super().save(*args, **kwargs)

class AccessibilityRequirement(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.CASCADE, related_name='accessibility_requirements')
    performance_date = models.DateField(null=True, blank=True)
    requirement_type = models.CharField(max_length=30, choices=[
        ('wheelchair', 'Wheelchair Access'), ('hearing_loop', 'Hearing Loop'),
        ('audio_description', 'Audio Description'), ('sign_language', 'Sign Language Interpretation'),
        ('large_print', 'Large Print Programme'), ('braille', 'Braille Programme'),
        ('relaxed', 'Relaxed Performance'), ('carer', 'Carer Admission'),
        ('parking', 'Accessible Parking'), ('other', 'Other'),
    ])
    patron_name = models.CharField(max_length=255, blank=True)
    patron_contact = models.CharField(max_length=255, blank=True)
    details = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='accessibility_assignments')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class LateSeatingPolicy(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey('contexts.OperatingContext', on_delete=models.CASCADE, related_name='late_seating_policies')
    cutoff_minutes = models.PositiveSmallIntegerField(default=15, help_text='Minutes after start time when late seating is no longer permitted')
    holding_area = models.CharField(max_length=255, blank=True)
    policy_description = models.TextField()
    exceptions_allowed = models.BooleanField(default=True)
    exception_approval_role = models.CharField(max_length=50, blank=True, help_text='Role that can approve exceptions e.g. House Manager')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
