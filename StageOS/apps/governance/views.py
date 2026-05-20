from django.db import models
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import CanCreateExecutiveIntervention
from common.views import TenantScopedMixin
from apps.contexts.models import OperatingContext
from apps.documents.models import Document
from .models import (
    KPI, KPIEvidence, Risk, CorrectiveAction, ExecutiveAction,
    Budget, BudgetLine, BoardMeeting, BoardResolution,
    DelegationMatrix, DelegationRule,
    ShareholderCompact, CompactTarget, CompactActual, FundingTranche,
    IUFWIncident, IUFWInvestigation, IUFWRecovery,
    AGAuditRequest, AGAuditEvidence,
)
from .serializers import (
    ExecutiveActionSerializer, ExecutiveActionStatusSerializer,
    KPISerializer, KPIEvidenceSerializer, ReportKPISerializer,
    RiskSerializer, CloseRiskSerializer,
    CorrectiveActionSerializer,
    BudgetSerializer, BudgetLineSerializer,
    BoardMeetingSerializer, BoardResolutionSerializer,
    DelegationMatrixSerializer, DelegationRuleSerializer,
    ShareholderCompactSerializer, CompactTargetSerializer, CompactActualSerializer, FundingTrancheSerializer,
    IUFWIncidentSerializer, IUFWInvestigationSerializer, IUFWRecoverySerializer,
    AGAuditRequestSerializer, AGAuditEvidenceSerializer,
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


class BudgetViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('operating_context', 'approved_by').prefetch_related('lines')
    serializer_class = BudgetSerializer
    filterset_fields = ['status', 'operating_context', 'financial_year']
    search_fields = ['name', 'financial_year', 'notes']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        budget = self.get_object()
        budget.status = 'approved'
        budget.approved_by = request.user
        budget.approved_at = timezone.now()
        budget.save(update_fields=['status', 'approved_by', 'approved_at'])
        return Response(BudgetSerializer(budget, context={'request': request}).data)


class BudgetLineViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = BudgetLine.objects.select_related('budget')
    serializer_class = BudgetLineSerializer
    filterset_fields = ['budget', 'category']
    search_fields = ['description', 'notes']
    ordering = ['category', 'sort_order', 'description']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class BoardMeetingViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = BoardMeeting.objects.select_related('agenda_document', 'minutes_document').prefetch_related('resolutions')
    serializer_class = BoardMeetingSerializer
    filterset_fields = ['meeting_type', 'status', 'meeting_date']
    search_fields = ['title', 'venue', 'chaired_by', 'minuted_by']
    ordering = ['-meeting_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def conclude(self, request, pk=None):
        meeting = self.get_object()
        meeting.status = 'concluded'
        meeting.save(update_fields=['status'])
        return Response(BoardMeetingSerializer(meeting, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def pack(self, request, pk=None):
        """Aggregated board pack data for a meeting."""
        meeting = self.get_object()
        org = request.user.organisation

        kpis = KPI.objects.filter(organisation=org).order_by('name')
        risks = Risk.objects.filter(organisation=org, status='open').order_by('-likelihood')
        resolutions = meeting.resolutions.all()

        budget_data = None
        budget = Budget.objects.filter(organisation=org, status='approved').first()
        if budget:
            lines = BudgetLine.objects.filter(budget=budget)
            total_income = lines.filter(category='income').aggregate(
                t=models.Sum('amount'))['t'] or 0
            total_exp = lines.filter(category='expenditure').aggregate(
                t=models.Sum('amount'))['t'] or 0
            budget_data = {
                'id': str(budget.id),
                'title': budget.title,
                'total_income': str(total_income),
                'total_expenditure': str(total_exp),
                'net_position': str(total_income - total_exp),
            }

        return Response({
            'meeting': {
                'id': str(meeting.id),
                'title': meeting.title,
                'meeting_date': str(meeting.meeting_date),
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'quorum_achieved': meeting.quorum_achieved,
                'members_present': meeting.members_present,
            },
            'kpi_summary': [
                {
                    'name': k.name,
                    'target': str(k.target_value),
                    'actual': str(k.actual_value),
                    'unit': k.unit,
                    'period': k.period,
                }
                for k in kpis
            ],
            'open_risks': [
                {
                    'title': r.title,
                    'likelihood': r.likelihood,
                    'impact': r.impact,
                }
                for r in risks
            ],
            'resolutions': [
                {
                    'id': str(r.id),
                    'number': r.resolution_number,
                    'title': r.title,
                    'status': r.status,
                    'proposed_by': r.proposed_by,
                    'action_due_date': str(r.action_due_date) if r.action_due_date else None,
                    'action_completed': r.action_completed,
                }
                for r in resolutions
            ],
            'budget_summary': budget_data,
            'generated_at': timezone.now().isoformat(),
        })


class BoardResolutionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = BoardResolution.objects.select_related('meeting', 'action_owner')
    serializer_class = BoardResolutionSerializer
    filterset_fields = ['meeting', 'status', 'action_completed']
    search_fields = ['title', 'description', 'resolution_number', 'proposed_by']
    ordering = ['resolution_number', 'created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Delegation Framework ──────────────────────────────────────────────────────

class DelegationMatrixViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = DelegationMatrix.objects.select_related('approved_by').prefetch_related('rules')
    serializer_class = DelegationMatrixSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'notes']
    ordering = ['-effective_date']

    @action(detail=True, methods=['get'])
    def rules(self, request, pk=None):
        matrix = self.get_object()
        qs = DelegationRule.objects.filter(
            matrix=matrix,
            organisation_id=request.user.organisation_id,
        ).order_by('category', 'threshold_amount')
        return Response(DelegationRuleSerializer(qs, many=True, context={'request': request}).data)


class DelegationRuleViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = DelegationRule.objects.select_related('matrix')
    serializer_class = DelegationRuleSerializer
    filterset_fields = ['matrix', 'category', 'delegated_to']
    search_fields = ['action_description', 'notes']
    ordering = ['category', 'threshold_amount']


# ── Shareholder Compact ───────────────────────────────────────────────────────

class ShareholderCompactViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ShareholderCompact.objects.prefetch_related('targets__actuals', 'tranches')
    serializer_class = ShareholderCompactSerializer
    filterset_fields = ['status', 'financial_year']
    search_fields = ['financial_year', 'executive_authority', 'notes']
    ordering = ['-financial_year']

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        compact = self.get_object()
        targets = compact.targets.prefetch_related('actuals').all()
        result = []
        for target in targets:
            actuals = list(target.actuals.all())
            actuals_data = CompactActualSerializer(actuals, many=True, context={'request': request}).data
            # Compute simple % achievement: count quarters with actuals vs 4
            quarters_reported = len(actuals)
            achievement_pct = round((quarters_reported / 4) * 100, 1)
            result.append({
                'target': CompactTargetSerializer(target, context={'request': request}).data,
                'actuals': actuals_data,
                'quarters_reported': quarters_reported,
                'achievement_pct': achievement_pct,
            })
        return Response({
            'compact_id': str(compact.id),
            'financial_year': compact.financial_year,
            'status': compact.status,
            'targets': result,
        })


class CompactTargetViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CompactTarget.objects.select_related('compact').prefetch_related('actuals')
    serializer_class = CompactTargetSerializer
    filterset_fields = ['compact', 'category']
    search_fields = ['indicator_name']
    ordering = ['category', 'indicator_name']


class CompactActualViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CompactActual.objects.select_related('target', 'reported_by')
    serializer_class = CompactActualSerializer
    filterset_fields = ['target', 'quarter']
    ordering = ['target', 'quarter']


class FundingTrancheViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FundingTranche.objects.select_related('compact')
    serializer_class = FundingTrancheSerializer
    filterset_fields = ['compact', 'is_received']
    ordering = ['tranche_number']


# ── IUFW ─────────────────────────────────────────────────────────────────────

class IUFWIncidentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IUFWIncident.objects.select_related('responsible_person')
    serializer_class = IUFWIncidentSerializer
    filterset_fields = ['iufw_type', 'status', 'financial_year', 'reported_to_board', 'reported_to_ag']
    search_fields = ['description', 'reference_number', 'responsible_description', 'root_cause']
    ordering = ['-discovered_date']

    @action(detail=False, methods=['get'])
    def register(self, request):
        from django.db.models import Sum, Count
        # Default to current financial year based on today's date
        today = timezone.now().date()
        if today.month >= 4:
            fy = f'{today.year}/{today.year + 1}'
        else:
            fy = f'{today.year - 1}/{today.year}'

        financial_year = request.query_params.get('financial_year', fy)
        org_id = request.user.organisation_id

        incidents = IUFWIncident.objects.filter(
            organisation_id=org_id,
            financial_year=financial_year,
        ).order_by('iufw_type', '-discovered_date')

        # Group by type with totals
        from collections import defaultdict
        grouped = defaultdict(list)
        totals = defaultdict(lambda: {'count': 0, 'amount': 0})

        for incident in incidents:
            grouped[incident.iufw_type].append(
                IUFWIncidentSerializer(incident, context={'request': request}).data
            )
            totals[incident.iufw_type]['count'] += 1
            totals[incident.iufw_type]['amount'] += float(incident.amount)

        grand_total_amount = sum(t['amount'] for t in totals.values())
        grand_total_count = sum(t['count'] for t in totals.values())

        register_data = {}
        for iufw_type, incident_list in grouped.items():
            register_data[iufw_type] = {
                'incidents': incident_list,
                'count': totals[iufw_type]['count'],
                'total_amount': totals[iufw_type]['amount'],
            }

        return Response({
            'financial_year': financial_year,
            'grand_total_count': grand_total_count,
            'grand_total_amount': grand_total_amount,
            'by_type': register_data,
        })


class IUFWInvestigationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IUFWInvestigation.objects.select_related('incident', 'investigator')
    serializer_class = IUFWInvestigationSerializer
    filterset_fields = ['incident', 'disciplinary_recommended', 'criminal_referral_recommended']
    ordering = ['-commenced_date']


class IUFWRecoveryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IUFWRecovery.objects.select_related('incident')
    serializer_class = IUFWRecoverySerializer
    filterset_fields = ['incident']
    ordering = ['-recovery_date']


# ── AG Audit ──────────────────────────────────────────────────────────────────

class AGAuditRequestViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AGAuditRequest.objects.select_related('audit_coordinator').prefetch_related('evidence_items')
    serializer_class = AGAuditRequestSerializer
    filterset_fields = ['status', 'audit_type', 'financial_year']
    search_fields = ['financial_year', 'notes', 'management_response']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['get'])
    def evidence(self, request, pk=None):
        audit = self.get_object()
        qs = AGAuditEvidence.objects.filter(
            audit=audit,
            organisation_id=request.user.organisation_id,
        ).select_related('provided_by').order_by('category', 'description')
        return Response(AGAuditEvidenceSerializer(qs, many=True, context={'request': request}).data)


class AGAuditEvidenceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AGAuditEvidence.objects.select_related('audit', 'provided_by')
    serializer_class = AGAuditEvidenceSerializer
    filterset_fields = ['audit', 'category', 'is_provided']
    search_fields = ['description', 'document_reference', 'ag_query_ref']
    ordering = ['category', 'description']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
