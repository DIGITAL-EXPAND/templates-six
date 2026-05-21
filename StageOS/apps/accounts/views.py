import uuid as uuid_lib
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from common.views import TenantScopedMixin
from common.permissions import IsTenantMember, is_internal_user, is_manager_or_admin
from apps.audit.services import AuditService
from .models import User
from .serializers import OperatingProfileSerializer, UserSerializer, UserCreateSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MyOperatingProfileView(generics.RetrieveAPIView):
    serializer_class = OperatingProfileSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_object(self):
        return self.request.user


class MyPermissionsView(generics.RetrieveAPIView):
    serializer_class = OperatingProfileSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_object(self):
        return self.request.user


class MyNavigationView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        profile = OperatingProfileSerializer().to_representation(request.user)
        authority = (profile.get('primary_position') or {}).get('authority_level')
        department = (profile.get('primary_department') or {}).get('name', '')
        user_type = request.user.user_type

        if user_type == 'internal_admin':
            items = [
                'Dashboard', 'Calendar', 'Workspaces', 'Programming', 'Marketing',
                'Technical', 'FOH / Operations', 'Contracts', 'Suppliers / SCM',
                'Artists', 'Ticketing', 'Youth Development', 'Governance',
                'Hospitality', 'Documents & Evidence', 'Reports', 'Audit Trail', 'Settings',
            ]
        elif user_type == 'executive':
            items = ['Dashboard', 'Calendar', 'Workspaces', 'Departments', 'Reports', 'Governance', 'Audit Trail', 'Notifications']
        elif authority == 'gm':
            items = ['Dashboard', 'Calendar', 'Workspaces', 'Department Readiness', 'Reports', 'Notifications']
        elif user_type == 'read_only':
            items = ['Dashboard', 'Reports', 'Board Summary', 'Risk Register', 'KPI Summary', 'Notifications']
        elif user_type == 'client_external':
            items = ['Dashboard', 'Submit Request', 'My Requests', 'Notifications']
        elif user_type == 'supplier_external':
            items = ['Dashboard', 'My Supplier Profile', 'My Documents', 'Notifications']
        elif user_type == 'artist_external':
            items = ['Dashboard', 'My Artist Profile', 'My Engagements', 'My Documents', 'Notifications']
        elif authority == 'department_manager':
            items = ['Dashboard', 'Calendar', 'Workspaces', department, 'My Work', 'Documents & Evidence', 'Reports', 'Notifications']
        else:
            items = ['Dashboard', 'My Work', 'Documents & Evidence', 'Notifications']
        return Response({'items': items, 'profile': profile})


class MyDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        profile = OperatingProfileSerializer().to_representation(request.user)
        authority = (profile.get('primary_position') or {}).get('authority_level')
        department = (profile.get('primary_department') or {}).get('name', '')
        user_type = request.user.user_type
        if user_type == 'internal_admin':
            kind = 'admin'
        elif user_type == 'executive':
            kind = 'executive'
        elif authority == 'gm':
            kind = 'gm'
        elif user_type == 'read_only':
            kind = 'board'
        elif user_type == 'client_external':
            kind = 'client'
        elif user_type == 'supplier_external':
            kind = 'supplier'
        elif user_type == 'artist_external':
            kind = 'artist'
        elif 'Programming' in department:
            kind = 'programming'
        elif 'Marketing' in department:
            kind = 'marketing'
        elif 'Technical' in department:
            kind = 'technical'
        elif 'FOH' in department:
            kind = 'foh'
        elif 'Contracts' in department:
            kind = 'contracts'
        elif 'SCM' in department:
            kind = 'scm'
        elif 'Ticketing' in department:
            kind = 'ticketing'
        elif 'Youth' in department:
            kind = 'youth'
        elif 'Governance' in department:
            kind = 'governance'
        elif 'Hospitality' in department:
            kind = 'hospitality'
        else:
            kind = 'generic'
        return Response({'dashboard_kind': kind, 'profile': profile})


class MyScorecardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        thirty_days = today + timedelta(days=30)

        # Get user's department memberships
        from apps.structure.models import UserDepartmentMembership
        memberships = UserDepartmentMembership.objects.filter(user=user).select_related('department')
        dept_ids = list(memberships.values_list('department_id', flat=True))
        org_id = user.organisation_id

        # Tasks metrics
        from apps.tasks.models import Task
        my_tasks = Task.objects.filter(organisation_id=org_id, assigned_to=user)
        dept_tasks = Task.objects.filter(organisation_id=org_id, department__in=dept_ids)

        tasks_data = {
            'my_open': my_tasks.filter(status='open').count(),
            'my_in_progress': my_tasks.filter(status='in_progress').count(),
            'my_overdue': my_tasks.filter(status__in=['open', 'in_progress'], due_date__lt=today).count(),
            'dept_open': dept_tasks.filter(status='open').count(),
            'dept_in_progress': dept_tasks.filter(status='in_progress').count(),
            'dept_overdue': dept_tasks.filter(status__in=['open', 'in_progress'], due_date__lt=today).count(),
        }

        # Approvals pending (submitted by user, not yet decided)
        from apps.approvals.models import ApprovalRequest
        pending_approvals = ApprovalRequest.objects.filter(
            organisation_id=org_id,
            decision='pending',
            requested_by=user,
        ).count()

        # Contracts expiring in 30 days
        from apps.contracts.models import ContractRecord
        contracts_expiring = ContractRecord.objects.filter(
            organisation_id=org_id,
            expiry_date__lte=thirty_days,
            expiry_date__gte=today,
            status__in=['signed', 'counter_signed'],
        ).count()

        # Upcoming shows (from programming if available)
        upcoming_shows = []
        try:
            from apps.programming.models import Show
            shows_qs = Show.objects.filter(
                organisation_id=org_id,
                status__in=['confirmed', 'on_sale', 'running'],
            ).select_related('operating_context').order_by('created_at')[:5]
            upcoming_shows = [
                {
                    'id': str(s.id),
                    'title': s.title,
                    'status': s.status,
                    'operating_context': str(s.operating_context_id),
                }
                for s in shows_qs
            ]
        except Exception:
            pass

        # Active operating contexts
        from apps.contexts.models import OperatingContext
        active_contexts = OperatingContext.objects.filter(
            organisation_id=org_id,
            status__in=['confirmed', 'in_production', 'in_delivery'],
        ).count()

        # Notifications unread (read_at is null means unread)
        unread_notifications = 0
        try:
            from apps.tasks.models import Notification
            unread_notifications = Notification.objects.filter(
                organisation_id=org_id,
                recipient=user,
                read_at__isnull=True,
            ).count()
        except Exception:
            pass

        return Response({
            'tasks': tasks_data,
            'pending_approvals': pending_approvals,
            'contracts_expiring_30d': contracts_expiring,
            'active_contexts': active_contexts,
            'upcoming_shows': upcoming_shows,
            'unread_notifications': unread_notifications,
            'departments': [
                {
                    'id': str(m.department_id),
                    'name': m.department.name,
                    'is_manager': m.can_manage_department,
                }
                for m in memberships
            ],
        })


class UserListCreateView(TenantScopedMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        if not is_internal_user(self.request.user):
            return User.objects.none()
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        if not is_manager_or_admin(request.user):
            raise PermissionDenied('You are not allowed to create users.')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save(organisation_id=self.request.user.organisation_id)
        AuditService.record(
            organisation=self.request.user.organisation,
            actor=self.request.user,
            event_type='user.created',
            target_type='User',
            target_id=user.id,
            new_value=user.user_type,
            payload={'email': user.email, 'user_type': user.user_type},
        )


class InviteUserView(APIView):
    """POST /api/v1/invite/ — internal_admin creates a user with an invite token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'internal_admin':
            raise PermissionDenied('Only system administrators can invite users.')
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
        token = uuid_lib.uuid4()
        user = User(
            email=email,
            first_name=request.data.get('first_name', ''),
            last_name=request.data.get('last_name', ''),
            user_type=request.data.get('user_type', 'staff'),
            organisation=request.user.organisation,
            invite_token=token,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()
        AuditService.record(
            organisation=request.user.organisation,
            actor=request.user,
            event_type='user.invited',
            target_type='User',
            target_id=user.id,
            payload={'email': user.email},
        )
        return Response(
            {'id': str(user.id), 'email': user.email, 'invite_token': str(token)},
            status=status.HTTP_201_CREATED,
        )


class AcceptInviteView(APIView):
    """POST /api/v1/invite/accept/ — set password from invite token."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('invite_token')
        password = request.data.get('password')
        if not token or not password:
            return Response(
                {'detail': 'invite_token and password are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(invite_token=uuid_lib.UUID(str(token)))
        except (User.DoesNotExist, ValueError):
            return Response(
                {'detail': 'Invalid or expired invite token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.is_active = True
        user.invite_token = None
        user.save(update_fields=['password', 'is_active', 'invite_token'])
        return Response({'detail': 'Password set. You can now log in.'})


class PasswordResetRequestView(APIView):
    """POST /api/v1/password-reset/ — request a password reset email."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email, is_active=True)
            token = uuid_lib.uuid4()
            user.invite_token = token
            user.save(update_fields=['invite_token'])
        except User.DoesNotExist:
            pass
        return Response({'detail': 'If this email is registered, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    """POST /api/v1/password-reset/confirm/ — confirm reset with token."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        if not token or not password:
            return Response(
                {'detail': 'token and password are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(invite_token=uuid_lib.UUID(str(token)), is_active=True)
        except (User.DoesNotExist, ValueError):
            return Response(
                {'detail': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.invite_token = None
        user.save(update_fields=['password', 'invite_token'])
        return Response({'detail': 'Password reset successfully. You can now log in.'})


class POPIAConsentView(APIView):
    """POST /api/v1/popia/consent/ — record data processing consent."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        from .popia_models import DataConsent
        consent = DataConsent.objects.create(
            organisation=request.user.organisation,
            subject_type=request.data.get('subject_type', 'user'),
            subject_id=request.data.get('subject_id', request.user.id),
            lawful_basis=request.data.get('lawful_basis', 'consent'),
            purpose=request.data.get('purpose', ''),
            consent_given=True,
            consent_date=timezone.now(),
            recorded_by=request.user,
        )
        AuditService.record(
            organisation=request.user.organisation,
            actor=request.user,
            event_type='popia.consent_recorded',
            target_type='DataConsent',
            target_id=consent.id,
            payload={'subject_type': consent.subject_type, 'lawful_basis': consent.lawful_basis},
        )
        return Response(
            {
                'id': str(consent.id),
                'consent_given': consent.consent_given,
                'consent_date': consent.consent_date.isoformat(),
                'purpose': consent.purpose,
            },
            status=status.HTTP_201_CREATED,
        )


class POPIAMyDataView(APIView):
    """GET /api/v1/popia/my-data/ — data subject sees their own consent records."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .popia_models import DataConsent
        consents = list(
            DataConsent.objects.filter(
                organisation=request.user.organisation,
                subject_type='user',
                subject_id=request.user.id,
            ).values(
                'id', 'subject_type', 'lawful_basis', 'purpose',
                'consent_given', 'consent_date', 'withdrawal_date',
                'retention_until', 'created_at',
            )
        )
        return Response(consents)


class POPIAErasureRequestView(APIView):
    """POST /api/v1/popia/erasure-request/ — submit an erasure request."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reason = request.data.get('reason', '')
        AuditService.record(
            organisation=request.user.organisation,
            actor=request.user,
            event_type='popia.erasure_requested',
            target_type='User',
            target_id=request.user.id,
            payload={'reason': reason},
        )
        return Response(
            {'detail': 'Your erasure request has been submitted. The Information Officer will be notified.'}
        )


# ── Leave Requests ────────────────────────────────────────────────────────────

from django.utils import timezone as _tz
from rest_framework import viewsets as _vsets
from rest_framework.decorators import action as _action
from rest_framework.response import Response as _Response
from rest_framework.permissions import IsAuthenticated as _IsAuthenticated
from common.views import TenantScopedMixin as _TenantScopedMixin
from .models import LeaveRequest, LeaveStatus
from .serializers import LeaveRequestSerializer


class LeaveRequestViewSet(_TenantScopedMixin, _vsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee', 'approved_by')
    serializer_class = LeaveRequestSerializer
    permission_classes = [_IsAuthenticated]
    filterset_fields = ['employee', 'leave_type', 'status', 'start_date', 'end_date']
    ordering = ['-start_date']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @_action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = request.user
        leave_request.approved_at = _tz.now()
        leave_request.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        return _Response(LeaveRequestSerializer(leave_request, context={'request': request}).data)

    @_action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        leave_request = self.get_object()
        reason = request.data.get('reason', '')
        leave_request.status = LeaveStatus.DECLINED
        leave_request.declined_reason = reason
        leave_request.save(update_fields=['status', 'declined_reason', 'updated_at'])
        return _Response(LeaveRequestSerializer(leave_request, context={'request': request}).data)
