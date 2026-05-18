import uuid as uuid_lib

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
