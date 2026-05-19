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
