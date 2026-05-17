from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from apps.documents.models import Document
from .models import ApprovalRoute, ApprovalStep, ApprovalRequest, ApprovalDecision
from .serializers import (
    ApprovalRouteSerializer, ApprovalStepSerializer,
    ApprovalRequestSerializer, ApprovalDecisionSerializer,
)
from .services import submit_for_approval, decide_approval


class ApprovalRouteViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ApprovalRoute.objects.all()
    serializer_class = ApprovalRouteSerializer
    filterset_fields = ['context_type', 'is_active']
    search_fields = ['name']
    ordering = ['name']


class ApprovalStepViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ApprovalStep.objects.select_related('route', 'approver_department')
    serializer_class = ApprovalStepSerializer
    filterset_fields = ['route']
    ordering = ['route', 'step_number']


class ApprovalRequestViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.select_related(
        'operating_context', 'approval_step', 'requested_by',
        'decided_by', 'evidence_reviewed',
    )
    serializer_class = ApprovalRequestSerializer
    permission_classes = [*TenantScopedMixin.permission_classes]
    filterset_fields = ['operating_context', 'approval_step', 'decision', 'requested_by']
    ordering = ['-requested_at']

    def perform_create(self, serializer):
        vd = serializer.validated_data
        req = submit_for_approval(
            context=vd['operating_context'],
            approval_step=vd['approval_step'],
            user=self.request.user,
            comment=vd.get('decision_comment', ''),
        )
        serializer.instance = req

    def _decide(self, request, pk, decision):
        approval_request = self.get_object()
        input_ser = ApprovalDecisionSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)

        evidence = None
        evidence_id = input_ser.validated_data.get('evidence')
        if evidence_id:
            try:
                evidence = Document.objects.get(
                    id=evidence_id,
                    organisation=request.user.organisation,
                )
            except Document.DoesNotExist:
                return Response(
                    {'evidence': 'Document not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        updated = decide_approval(
            approval_request=approval_request,
            user=request.user,
            decision=decision,
            comment=input_ser.validated_data.get('comment', ''),
            evidence=evidence,
        )
        return Response(ApprovalRequestSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.APPROVED)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.REJECTED)

    @action(detail=True, methods=['post'], url_path='request-changes')
    def request_changes(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.CHANGES_REQUESTED)

    @action(detail=True, methods=['post'], url_path='request-more-information')
    def request_more_information(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.CHANGES_REQUESTED)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.ESCALATED)

    @action(detail=True, methods=['post'], url_path='exception-approve')
    def exception_approve(self, request, pk=None):
        return self._decide(request, pk, ApprovalDecision.EXCEPTION_APPROVED)
