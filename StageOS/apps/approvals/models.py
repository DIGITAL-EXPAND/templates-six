import uuid
from django.db import models
from common.models import TenantOwnedModel
from common.enums import ContextType


class ApprovalDecision(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'
    ESCALATED = 'escalated', 'Escalated'
    EXCEPTION_APPROVED = 'exception_approved', 'Exception Approved'
    CANCELLED = 'cancelled', 'Cancelled'


class ApprovalRoute(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    context_type = models.CharField(
        max_length=50, choices=ContextType.choices, null=True, blank=True,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ApprovalStep(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        ApprovalRoute, on_delete=models.CASCADE, related_name='steps',
    )
    step_number = models.IntegerField()
    name = models.CharField(max_length=255)
    approver_department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_steps',
    )
    approver_role_description = models.CharField(max_length=255, blank=True)
    can_delegate = models.BooleanField(default=False)

    class Meta:
        unique_together = [('route', 'step_number')]
        ordering = ['route', 'step_number']

    def __str__(self):
        return f'{self.route.name} – Step {self.step_number}: {self.name}'


class ApprovalRequest(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='approval_requests',
    )
    approval_step = models.ForeignKey(
        ApprovalStep, on_delete=models.PROTECT, related_name='requests',
    )
    requested_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='submitted_approval_requests',
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(
        max_length=20, choices=ApprovalDecision.choices,
        default=ApprovalDecision.PENDING,
    )
    decided_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='decided_approval_requests',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_comment = models.TextField(blank=True)
    evidence_reviewed = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_evidence',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f'Approval for {self.operating_context} – {self.decision}'
