from django.db import models as db_models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from common.permissions import UserRoles, is_admin_user, user_type
from apps.structure.models import UserDepartmentMembership
from .models import TechnicalRider, CrewRequirement, EquipmentRequirement
from .serializers import (
    TechnicalRiderSerializer, CrewRequirementSerializer, EquipmentRequirementSerializer,
)
from .services import approve_rider, set_rider_status


class TechnicalRiderViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = TechnicalRider.objects.select_related(
        'operating_context', 'approved_by',
    )
    serializer_class = TechnicalRiderSerializer
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE}:
            return qs
        dept_ids = list(
            UserDepartmentMembership.objects.filter(user=user).values_list('department_id', flat=True)
        )
        return qs.filter(
            db_models.Q(operating_context__department_id__in=dept_ids)
            | db_models.Q(operating_context__department__isnull=True)
        )

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        user = self.request.user
        if not is_admin_user(user) and user_type(user) not in {UserRoles.EXECUTIVE}:
            context = serializer.validated_data.get('operating_context')
            if context and context.department_id:
                is_member = UserDepartmentMembership.objects.filter(
                    user=user, department_id=context.department_id
                ).exists()
                if not is_member:
                    raise PermissionDenied('You can only create technical riders for your own department.')
        serializer.save(organisation_id=user.organisation_id)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        rider = self.get_object()
        updated = approve_rider(rider, request.user)
        return Response(TechnicalRiderSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        updated = set_rider_status(
            self.get_object(), request.user, 'submitted', request.data.get('comment', ''),
        )
        return Response(TechnicalRiderSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        updated = set_rider_status(
            self.get_object(), request.user, 'rejected', request.data.get('comment', ''),
        )
        return Response(TechnicalRiderSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='request-revision')
    def request_revision(self, request, pk=None):
        updated = set_rider_status(
            self.get_object(), request.user, 'under_review', request.data.get('comment', ''),
        )
        return Response(TechnicalRiderSerializer(updated, context={'request': request}).data)


class CrewRequirementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CrewRequirement.objects.select_related('rider')
    serializer_class = CrewRequirementSerializer
    filterset_fields = ['rider']
    ordering = ['role']


class EquipmentRequirementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = EquipmentRequirement.objects.select_related('rider')
    serializer_class = EquipmentRequirementSerializer
    filterset_fields = ['rider', 'source']
    ordering = ['item']
