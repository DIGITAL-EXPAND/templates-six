from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
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
