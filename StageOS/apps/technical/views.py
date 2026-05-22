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


# ── Cue Sheets ────────────────────────────────────────────────────────────────

from .models import CueSheet, CueLine, PropsItem, WardrobeItem  # noqa: E402
from .serializers import (  # noqa: E402
    CueSheetSerializer, CueLineSerializer, PropsItemSerializer, WardrobeItemSerializer,
)


class CueSheetViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CueSheet.objects.select_related(
        'operating_context', 'prepared_by', 'approved_by',
    ).prefetch_related('lines')
    serializer_class = CueSheetSerializer
    filterset_fields = ['operating_context', 'department', 'is_master']
    search_fields = ['title', 'notes']
    ordering = ['department', 'version']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class CueLineViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CueLine.objects.select_related('cue_sheet')
    serializer_class = CueLineSerializer
    filterset_fields = ['cue_sheet']
    ordering = ['order', 'cue_number']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Props & Wardrobe ──────────────────────────────────────────────────────────

class PropsItemViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PropsItem.objects.select_related('current_production')
    serializer_class = PropsItemSerializer
    filterset_fields = ['category', 'condition', 'is_available', 'is_hired', 'current_production']
    search_fields = ['name', 'description', 'storage_location', 'hire_company']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        item = self.get_object()
        item.is_available = True
        item.current_production = None
        item.save(update_fields=['is_available', 'current_production'])
        return Response(PropsItemSerializer(item, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        from rest_framework.exceptions import ValidationError
        from apps.contexts.models import OperatingContext
        item = self.get_object()
        production_id = request.data.get('current_production')
        if not production_id:
            raise ValidationError({'current_production': 'This field is required.'})
        production = OperatingContext.objects.filter(
            id=production_id,
            organisation_id=request.user.organisation_id,
        ).first()
        if not production:
            raise ValidationError({'current_production': 'Production not found in your organisation.'})
        item.is_available = False
        item.current_production = production
        item.save(update_fields=['is_available', 'current_production'])
        return Response(PropsItemSerializer(item, context={'request': request}).data)


class WardrobeItemViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = WardrobeItem.objects.select_related('current_production')
    serializer_class = WardrobeItemSerializer
    filterset_fields = ['category', 'condition', 'is_hired', 'current_production', 'cleaning_required']
    search_fields = ['name', 'character', 'assigned_to_performer', 'storage_location']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
