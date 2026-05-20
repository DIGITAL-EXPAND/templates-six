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


class BudgetStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted for Approval'
    APPROVED = 'approved', 'Approved'
    ACTIVE = 'active', 'Active'
    CLOSED = 'closed', 'Closed'
    REVISED = 'revised', 'Revised'


class BudgetLineCategory(models.TextChoices):
    INCOME = 'income', 'Income'
    PERSONNEL = 'personnel', 'Personnel'
    PRODUCTION = 'production', 'Production'
    MARKETING = 'marketing', 'Marketing'
    TECHNICAL = 'technical', 'Technical'
    VENUE = 'venue', 'Venue & Facilities'
    TRAVEL = 'travel', 'Travel & Accommodation'
    ADMIN = 'admin', 'Administration'
    CONTINGENCY = 'contingency', 'Contingency'
    OTHER = 'other', 'Other'


class Budget(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='governance_budget',
    )
    name = models.CharField(max_length=255)
    financial_year = models.CharField(max_length=9, blank=True)  # e.g. "2026/27"
    status = models.CharField(max_length=20, choices=BudgetStatus.choices, default=BudgetStatus.DRAFT)
    total_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_expenditure = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_budgets',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Budget: {self.operating_context} [{self.status}]'

    def recalculate_totals(self):
        lines = self.lines.all()
        self.total_income = sum(l.amount for l in lines if l.category == BudgetLineCategory.INCOME)
        self.total_expenditure = sum(l.amount for l in lines if l.category != BudgetLineCategory.INCOME)
        self.save(update_fields=['total_income', 'total_expenditure'])

    @property
    def net_position(self):
        return self.total_income - self.total_expenditure


class BudgetLine(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='lines')
    category = models.CharField(max_length=20, choices=BudgetLineCategory.choices)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'sort_order', 'description']

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_cost
        self.variance = self.amount - self.actual_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.category}: {self.description} R{self.amount}'


class BoardMeetingType(models.TextChoices):
    ORDINARY = 'ordinary', 'Ordinary Board Meeting'
    SPECIAL = 'special', 'Special Board Meeting'
    COMMITTEE = 'committee', 'Committee Meeting'
    AGM = 'agm', 'Annual General Meeting'
    AUDIT_COMMITTEE = 'audit_committee', 'Audit Committee'
    RISK_COMMITTEE = 'risk_committee', 'Risk & Governance Committee'


class BoardMeetingStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    CONCLUDED = 'concluded', 'Concluded'
    CANCELLED = 'cancelled', 'Cancelled'
    POSTPONED = 'postponed', 'Postponed'


class ResolutionStatus(models.TextChoices):
    PASSED = 'passed', 'Passed'
    REJECTED = 'rejected', 'Rejected'
    DEFERRED = 'deferred', 'Deferred'
    WITHDRAWN = 'withdrawn', 'Withdrawn'


class BoardMeeting(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting_type = models.CharField(max_length=20, choices=BoardMeetingType.choices, default=BoardMeetingType.ORDINARY)
    title = models.CharField(max_length=255)
    meeting_date = models.DateField()
    venue = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=BoardMeetingStatus.choices, default=BoardMeetingStatus.SCHEDULED)
    quorum_required = models.PositiveIntegerField(default=0)
    quorum_achieved = models.BooleanField(default=False)
    members_present = models.PositiveIntegerField(default=0)
    apologies = models.TextField(blank=True)
    agenda_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agenda_meetings',
    )
    minutes_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='minutes_meetings',
    )
    chaired_by = models.CharField(max_length=255, blank=True)
    minuted_by = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-meeting_date']

    def __str__(self):
        return f'{self.title} — {self.meeting_date}'


class BoardResolution(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(BoardMeeting, on_delete=models.CASCADE, related_name='resolutions')
    resolution_number = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ResolutionStatus.choices, default=ResolutionStatus.PASSED)
    proposed_by = models.CharField(max_length=255, blank=True)
    seconded_by = models.CharField(max_length=255, blank=True)
    votes_for = models.PositiveIntegerField(default=0)
    votes_against = models.PositiveIntegerField(default=0)
    votes_abstained = models.PositiveIntegerField(default=0)
    action_required = models.TextField(blank=True)
    action_owner = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolution_actions',
    )
    action_due_date = models.DateField(null=True, blank=True)
    action_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['resolution_number', 'created_at']

    def __str__(self):
        return f'{self.resolution_number}: {self.title} [{self.status}]'


# ── Delegation Framework ──────────────────────────────────────────────────────

class DelegationLevel(models.TextChoices):
    BOARD = 'board', 'Board'
    CEO = 'ceo', 'CEO / Executive Director'
    CFO = 'cfo', 'CFO'
    GM = 'gm', 'General Manager'
    DEPARTMENT_MANAGER = 'department_manager', 'Department Manager'
    STAFF = 'staff', 'Staff Member'


class DelegationCategory(models.TextChoices):
    PROCUREMENT = 'procurement', 'Procurement'
    CONTRACTS = 'contracts', 'Contracts'
    HUMAN_RESOURCES = 'human_resources', 'Human Resources'
    FINANCE = 'finance', 'Finance'
    OPERATIONS = 'operations', 'Operations'
    LEGAL = 'legal', 'Legal'


class DelegationMatrix(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    version = models.PositiveIntegerField(default=1)
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_delegation_matrices')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DelegationRule(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matrix = models.ForeignKey(DelegationMatrix, on_delete=models.CASCADE, related_name='rules')
    category = models.CharField(max_length=30, choices=DelegationCategory.choices)
    action_description = models.CharField(max_length=255)
    delegated_to = models.CharField(max_length=30, choices=DelegationLevel.choices)
    threshold_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, help_text='ZAR threshold — null means no financial limit')
    requires_countersign = models.BooleanField(default=False)
    countersign_level = models.CharField(max_length=30, choices=DelegationLevel.choices, blank=True)
    requires_board_approval = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'threshold_amount']


# ── Shareholder Compact ───────────────────────────────────────────────────────

class CompactStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted to Shareholder'
    AGREED = 'agreed', 'Agreed & Signed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    UNDER_REVIEW = 'under_review', 'Under Review'
    CLOSED = 'closed', 'Closed / Evaluated'


class TargetCategory(models.TextChoices):
    FINANCIAL = 'financial', 'Financial Performance'
    ARTISTIC = 'artistic', 'Artistic Mandate'
    GOVERNANCE = 'governance', 'Governance & Compliance'
    SOCIAL = 'social', 'Social Impact'
    OPERATIONAL = 'operational', 'Operational Efficiency'


class ShareholderCompact(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    financial_year = models.CharField(max_length=9, help_text='e.g. 2025/2026')
    status = models.CharField(max_length=20, choices=CompactStatus.choices, default=CompactStatus.DRAFT)
    executive_authority = models.CharField(max_length=255, blank=True)
    signed_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    total_grant_allocation = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('organisation', 'financial_year')]


class CompactTarget(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compact = models.ForeignKey(ShareholderCompact, on_delete=models.CASCADE, related_name='targets')
    category = models.CharField(max_length=20, choices=TargetCategory.choices)
    indicator_name = models.CharField(max_length=255)
    baseline_value = models.CharField(max_length=100, blank=True)
    target_value = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    q1_target = models.CharField(max_length=100, blank=True)
    q2_target = models.CharField(max_length=100, blank=True)
    q3_target = models.CharField(max_length=100, blank=True)
    q4_target = models.CharField(max_length=100, blank=True)


class CompactActual(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(CompactTarget, on_delete=models.CASCADE, related_name='actuals')
    quarter = models.PositiveSmallIntegerField(choices=[(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4')])
    actual_value = models.CharField(max_length=100)
    variance_notes = models.TextField(blank=True)
    reported_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='compact_actuals')
    reported_at = models.DateTimeField(auto_now_add=True)
    evidence_reference = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [('organisation', 'target', 'quarter')]


class FundingTranche(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compact = models.ForeignKey(ShareholderCompact, on_delete=models.CASCADE, related_name='tranches')
    tranche_number = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    is_received = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['tranche_number']


# ── IUFW (Irregular, Unauthorised, Fruitless & Wasteful Expenditure) ──────────

class IUFWType(models.TextChoices):
    IRREGULAR = 'irregular', 'Irregular Expenditure'
    UNAUTHORISED = 'unauthorised', 'Unauthorised Expenditure'
    FRUITLESS = 'fruitless', 'Fruitless & Wasteful Expenditure'
    WASTEFUL = 'wasteful', 'Wasteful Expenditure'


class IUFWStatus(models.TextChoices):
    IDENTIFIED = 'identified', 'Identified'
    UNDER_INVESTIGATION = 'under_investigation', 'Under Investigation'
    REFERRED_DISCIPLINE = 'referred_discipline', 'Referred for Disciplinary Action'
    REFERRED_CRIMINAL = 'referred_criminal', 'Referred to Law Enforcement'
    CONDONED = 'condoned', 'Condoned by Authority'
    RECOVERED = 'recovered', 'Recovered'
    WRITTEN_OFF = 'written_off', 'Written Off (Board Approved)'
    CLOSED = 'closed', 'Closed'


class IUFWIncident(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=50, blank=True)
    iufw_type = models.CharField(max_length=20, choices=IUFWType.choices)
    status = models.CharField(max_length=25, choices=IUFWStatus.choices, default=IUFWStatus.IDENTIFIED)
    financial_year = models.CharField(max_length=9)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    discovered_date = models.DateField()
    responsible_person = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='iufw_incidents')
    responsible_description = models.CharField(max_length=255, blank=True)
    root_cause = models.TextField(blank=True)
    reported_to_board = models.BooleanField(default=False)
    reported_to_ag = models.BooleanField(default=False)
    agsa_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            year = self.financial_year.replace('/', '-') if self.financial_year else 'UNK'
            count = IUFWIncident.objects.filter(organisation=self.organisation).count() + 1
            self.reference_number = f'IUFW-{year}-{count:04d}'
        super().save(*args, **kwargs)


class IUFWInvestigation(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.OneToOneField(IUFWIncident, on_delete=models.CASCADE, related_name='investigation')
    investigator = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='iufw_investigations')
    investigator_description = models.CharField(max_length=255, blank=True)
    commenced_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    disciplinary_recommended = models.BooleanField(default=False)
    criminal_referral_recommended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class IUFWRecovery(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(IUFWIncident, on_delete=models.CASCADE, related_name='recoveries')
    amount_recovered = models.DecimalField(max_digits=14, decimal_places=2)
    recovery_date = models.DateField()
    recovery_method = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
