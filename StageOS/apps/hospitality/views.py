from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from .models import HospitalityNote, HospitalityRequest
from .serializers import HospitalityNoteSerializer, HospitalityRequestSerializer


class HospitalityRequestViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = HospitalityRequest.objects.select_related(
        'operating_context', 'assigned_to', 'created_by',
    ).prefetch_related('notes__created_by')
    serializer_class = HospitalityRequestSerializer
    filterset_fields = ['status', 'request_type', 'operating_context']
    ordering = ['-event_date']

    def perform_create(self, serializer):
        serializer.save(
            organisation=self.request.user.organisation,
            created_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'submitted'
        obj.save(update_fields=['status', 'updated_at'])
        return Response(HospitalityRequestSerializer(obj, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'confirmed'
        obj.save(update_fields=['status', 'updated_at'])
        return Response(HospitalityRequestSerializer(obj, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'declined'
        obj.save(update_fields=['status', 'updated_at'])
        return Response(HospitalityRequestSerializer(obj, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'completed'
        obj.save(update_fields=['status', 'updated_at'])
        return Response(HospitalityRequestSerializer(obj, context={'request': request}).data)


class HospitalityNoteViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = HospitalityNote.objects.select_related('hospitality_request', 'created_by')
    serializer_class = HospitalityNoteSerializer
    filterset_fields = ['hospitality_request', 'note_type']

    def get_queryset(self):
        qs = super().get_queryset()
        req_id = self.request.query_params.get('hospitality_request')
        if req_id:
            qs = qs.filter(hospitality_request_id=req_id)
        user = self.request.user
        external_types = {'supplier_external', 'artist_external', 'client_external', 'youth_external'}
        if user.user_type in external_types:
            qs = qs.filter(note_type='client_facing')
        return qs

    def perform_create(self, serializer):
        serializer.save(
            organisation=self.request.user.organisation,
            created_by=self.request.user,
        )
