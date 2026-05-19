from django.db import models as db_models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from common.permissions import UserRoles, is_admin_user, user_type
from apps.documents.models import Document
from apps.structure.models import UserDepartmentMembership
from .models import Campaign, CampaignDeliverable, SocialPost, AudienceReport
from .serializers import (
    CampaignSerializer, CampaignDeliverableSerializer,
    SocialPostSerializer, AudienceReportSerializer,
)
from .services import set_campaign_status, complete_deliverable


class CampaignViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related('operating_context', 'owner')
    serializer_class = CampaignSerializer
    filterset_fields = ['status', 'campaign_level']
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
                    raise PermissionDenied('You can only create campaigns for your own department.')
        serializer.save(organisation_id=user.organisation_id)

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


class SocialPostViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SocialPost.objects.select_related('campaign', 'created_by')
    serializer_class = SocialPostSerializer
    filterset_fields = ['campaign', 'platform', 'status']
    ordering = ['-scheduled_at', '-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        from django.utils import timezone
        post = self.get_object()
        post.status = 'published'
        post.published_at = timezone.now()
        post.save(update_fields=['status', 'published_at', 'updated_at'])
        return Response(SocialPostSerializer(post, context={'request': request}).data)


class AudienceReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AudienceReport.objects.select_related('operating_context')
    serializer_class = AudienceReportSerializer
    filterset_fields = ['operating_context', 'is_finalised']
    ordering = ['-created_at']
