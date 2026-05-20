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

    @action(detail=False, methods=['post'])
    def launch(self, request):
        """Start a workflow template for an operating context."""
        template_id = request.data.get('template')
        context_id = request.data.get('operating_context')
        if not template_id or not context_id:
            return Response(
                {'detail': 'template and operating_context are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            template = WorkflowTemplate.objects.get(id=template_id, organisation=request.user.organisation)
            context = __import__('apps.contexts.models', fromlist=['OperatingContext']).OperatingContext.objects.get(
                id=context_id, organisation=request.user.organisation,
            )
        except (WorkflowTemplate.DoesNotExist, Exception):
            return Response({'detail': 'Template or context not found.'}, status=status.HTTP_404_NOT_FOUND)
        instance = instantiate_workflow(context=context, template=template, user=request.user)
        return Response(
            WorkflowInstanceSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


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

    @action(detail=True, methods=['post'])
    def skip(self, request, pk=None):
        """Admin-only override to skip a step."""
        step = self.get_object()
        step.status = 'skipped'
        from django.utils import timezone as tz
        step.completed_at = tz.now()
        step.completed_by = request.user
        step.notes = request.data.get('notes', 'Skipped by admin override.')
        step.save(update_fields=['status', 'completed_at', 'completed_by', 'notes'])
        return Response(WorkflowStepInstanceSerializer(step, context={'request': request}).data)
