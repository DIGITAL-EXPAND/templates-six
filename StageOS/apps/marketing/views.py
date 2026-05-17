from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from apps.documents.models import Document
from .models import Campaign, CampaignDeliverable
from .serializers import CampaignSerializer, CampaignDeliverableSerializer
from .services import set_campaign_status, complete_deliverable


class CampaignViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related('operating_context', 'owner')
    serializer_class = CampaignSerializer
    filterset_fields = ['status', 'campaign_level']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        updated = set_campaign_status(self.get_object(), request.user, 'active', request.data.get('comment', ''))
        return Response(CampaignSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        updated = set_campaign_status(self.get_object(), request.user, 'paused', request.data.get('comment', ''))
        return Response(CampaignSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        updated = set_campaign_status(self.get_object(), request.user, 'closed', request.data.get('comment', ''))
        return Response(CampaignSerializer(updated, context={'request': request}).data)


class CampaignDeliverableViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CampaignDeliverable.objects.select_related('campaign', 'evidence_document')
    serializer_class = CampaignDeliverableSerializer
    filterset_fields = ['campaign', 'status', 'deliverable_type']
    ordering = ['due_date', 'created_at']

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        evidence = None
        evidence_id = request.data.get('evidence_document')
        if evidence_id:
            try:
                evidence = Document.objects.get(id=evidence_id, organisation=request.user.organisation)
            except Document.DoesNotExist:
                return Response(
                    {'evidence_document': 'Document not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        updated = complete_deliverable(
            self.get_object(), request.user, evidence, request.data.get('comment', ''),
        )
        return Response(CampaignDeliverableSerializer(updated, context={'request': request}).data)
