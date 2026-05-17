from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import CanCreateExecutiveIntervention
from common.views import TenantScopedMixin
from apps.contexts.models import OperatingContext
from apps.documents.models import Document
from .models import KPI, KPIEvidence, Risk, CorrectiveAction, ExecutiveAction
from .serializers import (
    ExecutiveActionSerializer, ExecutiveActionStatusSerializer,
    KPISerializer, KPIEvidenceSerializer, ReportKPISerializer,
    RiskSerializer, CloseRiskSerializer,
    CorrectiveActionSerializer,
)
from .services import (
    acknowledge_executive_action, cancel_executive_action,
    complete_executive_action, create_executive_action,
    report_kpi, close_risk, complete_corrective_action,
)


class KPIViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = KPI.objects.select_related('owner_department')
    serializer_class = KPISerializer
    filterset_fields = ['owner_department', 'reporting_period', 'is_active']
    search_fields = ['name', 'owner_description']
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        kpi = self.get_object()
        input_ser = ReportKPISerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        vd = input_ser.validated_data

        context_obj = None
        context_id = vd.get('context')
        if context_id:
            try:
                context_obj = OperatingContext.objects.get(
                    id=context_id, organisation=request.user.organisation,
                )
            except OperatingContext.DoesNotExist:
                return Response(
                    {'context': 'Operating context not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        evidence_doc = None
        doc_id = vd.get('evidence_document')
        if doc_id:
            try:
                evidence_doc = Document.objects.get(
                    id=doc_id, organisation=request.user.organisation,
                )
            except Document.DoesNotExist:
                return Response(
                    {'evidence_document': 'Document not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        evidence = report_kpi(
            kpi=kpi,
            user=request.user,
            value=vd['value'],
            evidence_doc=evidence_doc,
            context=context_obj,
            notes=vd.get('notes', ''),
        )
        return Response(KPIEvidenceSerializer(evidence, context={'request': request}).data)


class KPIEvidenceViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = KPIEvidence.objects.select_related('kpi', 'operating_context', 'reported_by', 'evidence_document')
    serializer_class = KPIEvidenceSerializer
    http_method_names = ['get', 'head', 'options']
    filterset_fields = ['kpi', 'operating_context']
    ordering = ['-reported_date']


class RiskViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Risk.objects.select_related('operating_context', 'owner', 'closed_by')
    serializer_class = RiskSerializer
    filterset_fields = ['operating_context', 'risk_level', 'status', 'owner']
    search_fields = ['title', 'description']
    ordering_fields = ['raised_date', 'risk_level']
    ordering = ['-raised_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        risk = self.get_object()
        input_ser = CloseRiskSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        updated = close_risk(risk, request.user, input_ser.validated_data.get('comment', ''))
        return Response(RiskSerializer(updated, context={'request': request}).data)


class CorrectiveActionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.select_related('risk', 'owner', 'completed_by', 'evidence_document')
    serializer_class = CorrectiveActionSerializer
    filterset_fields = ['risk', 'status', 'owner']
    ordering = ['due_date', 'status']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        action_obj = self.get_object()
        updated = complete_corrective_action(action_obj, request.user)
        return Response(CorrectiveActionSerializer(updated, context={'request': request}).data)


class ExecutiveActionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ExecutiveAction.objects.select_related(
        'operating_context', 'department', 'assigned_to', 'created_by',
        'acknowledged_by', 'completed_by', 'linked_task',
        'linked_risk', 'linked_corrective_action',
    )
    serializer_class = ExecutiveActionSerializer
    permission_classes = TenantScopedMixin.permission_classes + [CanCreateExecutiveIntervention]
    filterset_fields = [
        'action_type', 'status', 'operating_context', 'department',
        'assigned_to', 'target_type', 'target_id',
    ]
    search_fields = ['title', 'reason', 'instruction', 'target_type', 'target_id']
    ordering_fields = ['created_at', 'due_date', 'status']
    ordering = ['status', '-created_at']

    def perform_create(self, serializer):
        action_obj = create_executive_action(
            organisation=self.request.user.organisation,
            user=self.request.user,
            data=serializer.validated_data,
        )
        serializer.instance = action_obj

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        return self._status_action(request, acknowledge_executive_action)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        return self._status_action(request, complete_executive_action)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        return self._status_action(request, cancel_executive_action)

    def _status_action(self, request, service):
        action_obj = self.get_object()
        input_ser = ExecutiveActionStatusSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        updated = service(action_obj, request.user, input_ser.validated_data.get('comment', ''))
        return Response(ExecutiveActionSerializer(updated, context={'request': request}).data)
