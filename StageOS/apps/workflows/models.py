import uuid
from django.db import models
from common.models import TenantOwnedModel
from common.enums import ContextType


class WorkflowInstanceStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class WorkflowStepStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    SKIPPED = 'skipped', 'Skipped'
    BLOCKED = 'blocked', 'Blocked'


class WorkflowTemplate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    context_type = models.CharField(max_length=50, choices=ContextType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkflowStepTemplate(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        WorkflowTemplate, on_delete=models.CASCADE, related_name='steps',
    )
    step_number = models.IntegerField()
    name = models.CharField(max_length=255)
    owner_department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workflow_step_templates',
    )
    owner_role_description = models.CharField(max_length=255, blank=True)
    requires_approval = models.BooleanField(default=False)
    requires_evidence = models.BooleanField(default=False)
    sla_days = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [('template', 'step_number')]
        ordering = ['template', 'step_number']

    def __str__(self):
        return f'{self.template.name} – Step {self.step_number}: {self.name}'


class WorkflowInstance(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        WorkflowTemplate, on_delete=models.PROTECT, related_name='instances',
    )
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='workflow_instances',
    )
    status = models.CharField(
        max_length=20, choices=WorkflowInstanceStatus.choices,
        default=WorkflowInstanceStatus.ACTIVE,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.template.name} for {self.operating_context}'


class WorkflowStepInstance(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_instance = models.ForeignKey(
        WorkflowInstance, on_delete=models.CASCADE, related_name='step_instances',
    )
    step_template = models.ForeignKey(
        WorkflowStepTemplate, on_delete=models.PROTECT,
        related_name='step_instances',
    )
    step_number = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=WorkflowStepStatus.choices,
        default=WorkflowStepStatus.PENDING,
    )
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_workflow_steps',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='completed_workflow_steps',
    )
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workflow_step_evidence',
    )
    approval_request = models.ForeignKey(
        'approvals.ApprovalRequest', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workflow_steps',
    )
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['workflow_instance', 'step_number']

    def __str__(self):
        return f'{self.workflow_instance} – Step {self.step_number}'
