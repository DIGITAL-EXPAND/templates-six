from django.utils import timezone
from rest_framework.exceptions import APIException
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService
from common import department_permissions
from common.permissions import UserRoles, is_admin_user, user_type


class EvidenceRequired(APIException):
    status_code = 422
    default_detail = 'Evidence is required before this task can be completed'
    default_code = 'evidence_required'


class DepartmentAuthorityRequired(APIException):
    status_code = 403
    default_detail = 'This action requires department authority.'
    default_code = 'department_authority_required'


def _notify(recipient, actor, notification_type, title, message='', task=None, department=None):
    from .models import Notification
    if not recipient or not getattr(recipient, 'organisation_id', None):
        return None
    return Notification.objects.create(
        organisation_id=recipient.organisation_id,
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        title=title,
        message=message,
        task=task,
        department=department,
    )


def _require_assign_authority(user, department):
    if _uses_legacy_internal_authority(user):
        return
    if department and not department_permissions.can_assign_department_work(user, department):
        raise DepartmentAuthorityRequired('You cannot assign work for this department.')


def _uses_legacy_internal_authority(user):
    return bool(
        user
        and getattr(user, 'is_authenticated', False)
        and not department_permissions.has_department_membership(user)
        and (is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE, UserRoles.MANAGER, UserRoles.STAFF})
    )


def _require_task_actor(user, task):
    if _uses_legacy_internal_authority(user):
        return
    if department_permissions.can_manage_department(user, task.department):
        return
    if task.assigned_to_id == user.id:
        return
    raise DepartmentAuthorityRequired('You can only update work assigned to you or your department.')


def create_task(context, user, data):
    from .models import Task
    department = data.get('department')
    _require_assign_authority(user, department)
    # Validate assignee is a member of the task's department
    assigned_to = data.get('assigned_to')
    if assigned_to and department and not is_admin_user(user) and user_type(user) not in {UserRoles.EXECUTIVE}:
        from apps.structure.models import UserDepartmentMembership
        is_member = UserDepartmentMembership.objects.filter(
            user=assigned_to, department=department
        ).exists()
        if not is_member:
            raise DepartmentAuthorityRequired('The assignee must be a member of the specified department.')
    task = Task.objects.create(
        operating_context=context,
        organisation=context.organisation,
        assigned_by=user,
        **data,
    )
    _notify(
        recipient=task.assigned_to,
        actor=user,
        notification_type='task_assigned',
        title='Task assigned',
        message=task.title,
        task=task,
        department=task.department,
    )
    if task.assigned_to and task.assigned_to.email:
        from django.core.mail import send_mail
        from django.conf import settings
        assignee = task.assigned_to
        send_mail(
            subject=f'StageOS — Task assigned: {task.title}',
            message=(
                f"Hello {assignee.first_name or assignee.email},\n\n"
                f"A task has been assigned to you:\n\n"
                f"{task.title}\n"
                f"Due: {task.due_date or 'No due date'}\n\n"
                f"Log in to view: {settings.FRONTEND_BASE_URL}/tasks\n\n"
                f"StageOS"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[assignee.email],
            fail_silently=True,
        )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='task.created',
        payload={
            'task_id': str(task.id),
            'title': task.title,
            'context_id': str(context.id),
        },
    )
    return task


def complete_task(task, user, has_evidence=False):
    _require_task_actor(user, task)
    accepted_evidence_exists = task.evidence_submissions.filter(accepted=True).exists()
    if task.evidence_required and not (task.evidence_provided or accepted_evidence_exists):
        raise EvidenceRequired()
    task.status = 'done'
    task.completed_at = timezone.now()
    task.completed_by = user
    task.evidence_provided = bool(task.evidence_provided or accepted_evidence_exists or has_evidence)
    task.save(update_fields=['status', 'completed_at', 'completed_by', 'evidence_provided', 'updated_at'])
    _notify(
        recipient=task.assigned_by,
        actor=user,
        notification_type='task_completed',
        title='Task completed',
        message=task.title,
        task=task,
        department=task.department,
    )
    AuditEvent.objects.create(
        organisation=task.organisation,
        actor=user,
        event_type='task.completed',
        payload={
            'task_id': str(task.id),
            'title': task.title,
            'has_evidence': has_evidence,
        },
    )
    return task


def cancel_task(task, user, comment=''):
    if _uses_legacy_internal_authority(user):
        pass
    elif not department_permissions.can_manage_department(user, task.department):
        raise DepartmentAuthorityRequired('You cannot cancel work for this department.')
    old_status = task.status
    task.status = 'cancelled'
    task.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=task.organisation,
        actor=user,
        event_type='task.cancelled',
        target_type='Task',
        target_id=task.id,
        old_value=old_status,
        new_value=task.status,
        reason=comment,
        payload={'task_id': str(task.id), 'title': task.title},
    )
    return task


def reopen_task(task, user, comment=''):
    if not _uses_legacy_internal_authority(user) and not department_permissions.can_manage_department(user, task.department):
        raise DepartmentAuthorityRequired('You cannot reopen work for this department.')
    old_status = task.status
    task.status = 'open'
    task.completed_at = None
    task.completed_by = None
    task.save(update_fields=['status', 'completed_at', 'completed_by', 'updated_at'])
    AuditService.record(
        organisation=task.organisation,
        actor=user,
        event_type='task.reopened',
        target_type='Task',
        target_id=task.id,
        old_value=old_status,
        new_value=task.status,
        reason=comment,
    )
    return task


def block_task(task, user, comment=''):
    _require_task_actor(user, task)
    old_status = task.status
    task.status = 'blocked'
    task.blocked_reason = comment
    task.save(update_fields=['status', 'blocked_reason', 'updated_at'])
    _notify(
        recipient=task.assigned_by,
        actor=user,
        notification_type='task_blocked',
        title='Task blocked',
        message=comment or task.title,
        task=task,
        department=task.department,
    )
    AuditService.record(
        organisation=task.organisation,
        actor=user,
        event_type='task.blocked',
        target_type='Task',
        target_id=task.id,
        old_value=old_status,
        new_value=task.status,
        reason=comment,
    )
    return task


def start_task(task, user, comment=''):
    _require_task_actor(user, task)
    old_status = task.status
    task.status = 'in_progress'
    task.started_at = task.started_at or timezone.now()
    task.save(update_fields=['status', 'started_at', 'updated_at'])
    AuditService.record(
        organisation=task.organisation,
        actor=user,
        event_type='task.started',
        target_type='Task',
        target_id=task.id,
        old_value=old_status,
        new_value=task.status,
        reason=comment,
    )
    return task


def assign_task(task, user, assigned_to=None, due_date=None, comment=''):
    if not _uses_legacy_internal_authority(user) and not department_permissions.can_assign_department_work(user, task.department):
        raise DepartmentAuthorityRequired('You cannot assign work for this department.')
    # Validate new assignee is a member of the task's department
    if assigned_to and task.department and not is_admin_user(user) and user_type(user) not in {UserRoles.EXECUTIVE}:
        from apps.structure.models import UserDepartmentMembership
        is_member = UserDepartmentMembership.objects.filter(
            user=assigned_to, department=task.department
        ).exists()
        if not is_member:
            raise DepartmentAuthorityRequired('The assignee must be a member of the task\'s department.')
    old_assignee = str(task.assigned_to_id) if task.assigned_to_id else ''
    task.assigned_to = assigned_to
    if due_date is not None:
        task.due_date = due_date
    task.assigned_by = user
    task.save(update_fields=['assigned_to', 'assigned_by', 'due_date', 'updated_at'])
    _notify(
        recipient=assigned_to,
        actor=user,
        notification_type='task_assigned',
        title='Task assigned',
        message=comment or task.title,
        task=task,
        department=task.department,
    )
    if task.assigned_to and task.assigned_to.email:
        from django.core.mail import send_mail
        from django.conf import settings
        assignee = task.assigned_to
        send_mail(
            subject=f'StageOS — Task assigned: {task.title}',
            message=(
                f"Hello {assignee.first_name or assignee.email},\n\n"
                f"A task has been assigned to you:\n\n"
                f"{task.title}\n"
                f"Due: {task.due_date or 'No due date'}\n\n"
                f"Log in to view: {settings.FRONTEND_BASE_URL}/tasks\n\n"
                f"StageOS"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[assignee.email],
            fail_silently=True,
        )
    AuditService.record(
        organisation=task.organisation,
        actor=user,
        event_type='task.assigned',
        target_type='Task',
        target_id=task.id,
        old_value=old_assignee,
        new_value=str(task.assigned_to_id) if task.assigned_to_id else '',
        reason=comment,
    )
    return task


def mark_notification_read(notification, user):
    if notification.recipient_id != user.id:
        raise DepartmentAuthorityRequired('You cannot update another user notification.')
    notification.read_at = timezone.now()
    notification.save(update_fields=['read_at'])
    return notification
