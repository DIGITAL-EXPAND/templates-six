from apps.accounts.models import User
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from common import department_permissions
from common.permissions import UserRoles, is_admin_user, is_internal_user, user_type
from .models import Notification, Task, TaskComment
from .serializers import (
    AssignTaskSerializer,
    CompleteTaskSerializer,
    NotificationSerializer,
    TaskActionCommentSerializer,
    TaskCommentSerializer,
    TaskSerializer,
)
from .services import assign_task, block_task, cancel_task, complete_task, create_task, mark_notification_read, reopen_task, start_task


class TaskViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        'operating_context', 'department', 'assigned_to', 'completed_by',
    )
    serializer_class = TaskSerializer
    filterset_fields = ['operating_context', 'department', 'assigned_to', 'status', 'priority']
    search_fields = ['title']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['due_date', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE, UserRoles.READ_ONLY}:
            return qs
        memberships = department_permissions.user_department_memberships(user)
        if not memberships.exists():
            return qs
        manageable_departments = [
            membership.department_id
            for membership in memberships
            if membership.can_manage_department or membership.can_view_department_summary
        ]
        return qs.filter(
            models.Q(assigned_to=user) | models.Q(department_id__in=manageable_departments)
        ).distinct()

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        vd = dict(serializer.validated_data)
        user = self.request.user
        dept = vd.get('department')
        assigned_to = vd.get('assigned_to')

        # Non-admin/executive must only create tasks in their own departments
        if not is_admin_user(user) and user_type(user) not in {UserRoles.EXECUTIVE}:
            manageable = [
                m.department_id
                for m in department_permissions.user_department_memberships(user)
                if m.can_assign_work or m.can_manage_department
            ]
            if dept and dept.id not in manageable:
                raise PermissionDenied('You can only assign work within your own department.')
            # If assignee provided, verify they are in the task's department
            if assigned_to and dept:
                from apps.structure.models import UserDepartmentMembership
                is_member = UserDepartmentMembership.objects.filter(
                    user=assigned_to, department=dept
                ).exists()
                if not is_member:
                    raise PermissionDenied('The selected person is not a member of this department.')

        context_obj = vd.pop('operating_context')
        task = create_task(context=context_obj, user=user, data=vd)
        serializer.instance = task

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        input_ser = CompleteTaskSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        updated = complete_task(task, request.user, input_ser.validated_data.get('has_evidence', False))
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        task = self.get_object()
        updated = cancel_task(task, request.user, request.data.get('comment', ''))
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        input_ser = TaskActionCommentSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        updated = start_task(task, request.user, input_ser.validated_data.get('comment', ''))
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        from rest_framework.exceptions import PermissionDenied
        task = self.get_object()
        input_ser = AssignTaskSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        assignee_id = input_ser.validated_data.get('assigned_to')
        assignee = None
        if assignee_id:
            assignee = User.objects.get(id=assignee_id, organisation_id=request.user.organisation_id)
            # Verify that the assignee is a member of the task's department
            if task.department and not is_admin_user(request.user) and user_type(request.user) not in {UserRoles.EXECUTIVE}:
                from apps.structure.models import UserDepartmentMembership
                is_member = UserDepartmentMembership.objects.filter(
                    user=assignee, department=task.department
                ).exists()
                if not is_member:
                    raise PermissionDenied('The selected person is not a member of this department.')
        updated = assign_task(
            task,
            request.user,
            assigned_to=assignee,
            due_date=input_ser.validated_data.get('due_date'),
            comment=input_ser.validated_data.get('comment', ''),
        )
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        task = self.get_object()
        updated = reopen_task(task, request.user, request.data.get('comment', ''))
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        task = self.get_object()
        updated = block_task(task, request.user, request.data.get('comment', ''))
        return Response(TaskSerializer(updated, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def overdue_summary(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        qs = self.get_queryset().filter(due_date__lt=today, status__in=['pending', 'in_progress'])
        data = []
        for task in qs:
            data.append({
                'id': str(task.id),
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (today - task.due_date).days,
                'assigned_to': str(task.assigned_to_id) if hasattr(task, 'assigned_to_id') else None,
                'status': task.status,
            })
        data.sort(key=lambda x: x['days_overdue'], reverse=True)
        return Response({'overdue_tasks': data, 'total': len(data)})


class TaskCommentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = TaskComment.objects.select_related('task', 'author')
    serializer_class = TaskCommentSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get('task')
        if task_id:
            qs = qs.filter(task_id=task_id)
        user = self.request.user
        if is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE, UserRoles.READ_ONLY}:
            return qs
        memberships = department_permissions.user_department_memberships(user)
        manageable_departments = [
            m.department_id for m in memberships if m.can_manage_department
        ]
        return qs.filter(
            models.Q(task__assigned_to=user)
            | models.Q(task__assigned_by=user)
            | models.Q(task__department_id__in=manageable_departments)
        ).distinct()

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('task'):
            return Response({'detail': 'task query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not is_internal_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only internal users can create task comments.')
        task = serializer.validated_data['task']
        serializer.save(
            author=self.request.user,
            organisation=task.organisation,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author_id != request.user.id and not is_admin_user(request.user):
            return Response({'detail': 'You can only delete your own comments.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class NotificationViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.select_related('recipient', 'actor', 'task', 'department')
    serializer_class = NotificationSerializer
    filterset_fields = ['read_at', 'notification_type', 'department']

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        updated = mark_notification_read(notification, request.user)
        return Response(NotificationSerializer(updated, context={'request': request}).data)
