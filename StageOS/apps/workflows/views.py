from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from apps.documents.models import Document
from apps.approvals.models import ApprovalRequest
from .models import (
    WorkflowTemplate, WorkflowStepTemplate,
    WorkflowInstance, WorkflowStepInstance,
)
from .serializers import (
    WorkflowTemplateSerializer, WorkflowStepTemplateSerializer,
    WorkflowInstanceSerializer, WorkflowStepInstanceSerializer,
    AdvanceStepSerializer,
)
from .services import instantiate_workflow, advance_step


class WorkflowTemplateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    filterset_fields = ['context_type', 'is_active']
    search_fields = ['name']
    ordering = ['name']


class WorkflowStepTemplateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = WorkflowStepTemplate.objects.select_related('template', 'owner_department')
    serializer_class = WorkflowStepTemplateSerializer
    filterset_fields = ['template']
    ordering = ['template', 'step_number']


class WorkflowInstanceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.select_related('template', 'operating_context')
    serializer_class = WorkflowInstanceSerializer
    filterset_fields = ['operating_context', 'template', 'status']
    ordering = ['-started_at']

    def perform_create(self, serializer):
        vd = serializer.validated_data
        instance = instantiate_workflow(
            context=vd['operating_context'],
            template=vd['template'],
            user=self.request.user,
        )
        serializer.instance = instance


class WorkflowStepInstanceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = WorkflowStepInstance.objects.select_related(
        'workflow_instance', 'step_template', 'assigned_to',
        'completed_by', 'evidence_document',
    )
    serializer_class = WorkflowStepInstanceSerializer
    filterset_fields = ['workflow_instance', 'status', 'assigned_to']
    ordering = ['workflow_instance', 'step_number']

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        step = self.get_object()
        input_ser = AdvanceStepSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)

        evidence_document = None
        evidence_id = input_ser.validated_data.get('evidence_document')
        if evidence_id:
            try:
                evidence_document = Document.objects.get(
                    id=evidence_id,
                    organisation=request.user.organisation,
                )
            except Document.DoesNotExist:
                return Response(
                    {'evidence_document': 'Document not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        approval_request = None
        approval_id = input_ser.validated_data.get('approval_request')
        if approval_id:
            try:
                approval_request = ApprovalRequest.objects.get(
                    id=approval_id,
                    organisation=request.user.organisation,
                )
            except ApprovalRequest.DoesNotExist:
                return Response(
                    {'approval_request': 'Approval not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        updated = advance_step(
            step_instance=step,
            user=request.user,
            notes=input_ser.validated_data.get('notes', ''),
            evidence_document=evidence_document,
            approval_request=approval_request,
        )
        return Response(WorkflowStepInstanceSerializer(updated, context={'request': request}).data)
