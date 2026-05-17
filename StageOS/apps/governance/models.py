import uuid
from django.db import models
from common.models import TenantOwnedModel
from common.enums import RiskLevel


class ReportingPeriod(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly'
    QUARTERLY = 'quarterly', 'Quarterly'
    ANNUALLY = 'annually', 'Annually'


class RiskStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    MITIGATED = 'mitigated', 'Mitigated'
    CLOSED = 'closed', 'Closed'


class ActionStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    OVERDUE = 'overdue', 'Overdue'


class ExecutiveActionType(models.TextChoices):
    COMMENT = 'comment', 'Comment'
    REQUEST_CHANGE = 'request_change', 'Request Change'
    FLAG_ISSUE = 'flag_issue', 'Flag Issue'
    FLAG_RISK = 'flag_risk', 'Flag Risk'
    ASSIGN_CORRECTIVE_ACTION = 'assign_corrective_action', 'Assign Corrective Action'
    APPROVE = 'approve', 'Approve'
    DECLINE = 'decline', 'Decline'
    REQUEST_MORE_INFORMATION = 'request_more_information', 'Request More Information'
    OVERRIDE = 'override', 'Override With Reason'
    ESCALATE = 'escalate', 'Escalate'


class ExecutiveActionStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class KPI(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner_department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kpis',
    )
    owner_description = models.CharField(max_length=255, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50)
    evidence_description = models.TextField(blank=True)
    reporting_period = models.CharField(max_length=20, choices=ReportingPeriod.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class KPIEvidence(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kpi = models.ForeignKey(
        KPI, on_delete=models.CASCADE, related_name='evidence_records',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kpi_evidence',
    )
    value_reported = models.DecimalField(max_digits=10, decimal_places=2)
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kpi_evidence',
    )
    reported_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='kpi_evidence_reports',
    )
    reported_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-reported_date']

    def __str__(self):
        return f'{self.kpi.name}: {self.value_reported}'


class Risk(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    owner = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='owned_risks',
    )
    status = models.CharField(
        max_length=20, choices=RiskStatus.choices, default=RiskStatus.OPEN,
    )
    mitigation_plan = models.TextField(blank=True)
    raised_date = models.DateField(auto_now_add=True)
    closed_date = models.DateField(null=True, blank=True)
    closed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='closed_risks',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-raised_date', 'risk_level']

    def __str__(self):
        return self.title


class CorrectiveAction(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk = models.ForeignKey(
        Risk, on_delete=models.CASCADE, related_name='corrective_actions',
    )
    action = models.TextField()
    owner = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='corrective_actions',
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ActionStatus.choices, default=ActionStatus.OPEN,
    )
    completed_date = models.DateField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='completed_corrective_actions',
    )
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='corrective_action_evidence',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'status']

    def __str__(self):
        return f'Corrective action for {self.risk.title}'


class ExecutiveAction(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=40, choices=ExecutiveActionType.choices)
    status = models.CharField(
        max_length=20,
        choices=ExecutiveActionStatus.choices,
        default=ExecutiveActionStatus.OPEN,
    )
    title = models.CharField(max_length=255)
    reason = models.TextField(blank=True)
    instruction = models.TextField(blank=True)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executive_actions',
    )
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executive_actions',
    )
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_executive_actions',
    )
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='created_executive_actions',
    )
    acknowledged_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='acknowledged_executive_actions',
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='completed_executive_actions',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    linked_task = models.ForeignKey(
        'tasks.Task', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executive_actions',
    )
    linked_risk = models.ForeignKey(
        Risk, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executive_actions',
    )
    linked_corrective_action = models.ForeignKey(
        CorrectiveAction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='executive_actions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-created_at']

    def __str__(self):
        return f'{self.get_action_type_display()}: {self.title}'
