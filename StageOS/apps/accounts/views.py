from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
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
