import uuid
from django.db import models
from common.models import TenantOwnedModel
from common.enums import Priority


class TaskStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    BLOCKED = 'blocked', 'Blocked'
    DONE = 'done', 'Done'
    CANCELLED = 'cancelled', 'Cancelled'


class DepartmentWorkType(models.TextChoices):
    GENERAL = 'general', 'General'
    READINESS = 'readiness', 'Readiness'
    EVIDENCE = 'evidence', 'Evidence'
    APPROVAL_PREP = 'approval_prep', 'Approval Preparation'
    ISSUE_RESPONSE = 'issue_response', 'Issue Response'
    FOLLOW_UP = 'follow_up', 'Follow Up'


class NotificationType(models.TextChoices):
    TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
    TASK_UPDATED = 'task_updated', 'Task Updated'
    TASK_BLOCKED = 'task_blocked', 'Task Blocked'
    TASK_COMPLETED = 'task_completed', 'Task Completed'
    DEPARTMENT_ISSUE = 'department_issue', 'Department Issue'
    EVIDENCE_REJECTED = 'evidence_rejected', 'Evidence Rejected'
    APPROVAL_DECIDED = 'approval_decided', 'Approval Decision'


class Task(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.PROTECT, related_name='tasks',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tasks',
    )
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tasks',
    )
    assigned_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_department_tasks',
    )
    work_type = models.CharField(max_length=30, choices=DepartmentWorkType.choices, default=DepartmentWorkType.GENERAL)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.OPEN)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='completed_tasks',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    blocked_reason = models.TextField(blank=True)
    evidence_required = models.BooleanField(default=False)
    evidence_provided = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return self.title


class TaskComment(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='task_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.task.title}"


class Notification(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=40, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    department = models.ForeignKey(
        'structure.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications',
    )
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
