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
    IUFWDisciplinaryReferral, IUFWCondonement,
    AGAuditRequest, AGAuditEvidence,
    ConflictOfInterest, PerformanceReport,
    Section32Report, AnnualReport, AnnualReportSection,
    ExpiryAlert,
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
    IUFWDisciplinaryReferralSerializer, IUFWCondonementSerializer,
    AGAuditRequestSerializer, AGAuditEvidenceSerializer,
    ConflictOfInterestSerializer, PerformanceReportSerializer,
    Section32ReportSerializer, AnnualReportSerializer, AnnualReportSectionSerializer,
    ExpiryAlertSerializer,
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


    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="iufw_register.csv"'
        writer = csv.writer(response)
        writer.writerow(['Reference', 'Type', 'Status', 'Financial Year', 'Description', 'Amount', 'Discovered Date', 'Reported to Board', 'Reported to AG'])
        for incident in qs:
            writer.writerow([
                incident.reference_number, incident.iufw_type, incident.status,
                incident.financial_year, incident.description, str(incident.amount),
                str(incident.discovered_date), incident.reported_to_board, incident.reported_to_ag,
            ])
        return response


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

    @action(detail=True, methods=['get'])
    def generate_package(self, request, pk=None):
        """Generate a complete audit evidence package summary."""
        audit = self.get_object()
        evidence = audit.evidence_items.all()
        total = evidence.count()
        provided = evidence.filter(is_provided=True).count()
        outstanding = evidence.filter(is_provided=False)

        by_category = {}
        for item in evidence:
            cat = item.category
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'provided': 0, 'items': []}
            by_category[cat]['total'] += 1
            if item.is_provided:
                by_category[cat]['provided'] += 1
            if not item.is_provided:
                by_category[cat]['items'].append({
                    'id': str(item.id),
                    'description': item.description,
                    'ag_query_ref': item.ag_query_ref,
                    'document_reference': item.document_reference,
                })

        return Response({
            'audit_id': str(audit.id),
            'financial_year': audit.financial_year,
            'audit_type': audit.audit_type,
            'status': audit.status,
            'completeness_pct': round((provided / total * 100) if total else 0, 1),
            'total_evidence_items': total,
            'provided': provided,
            'outstanding_count': total - provided,
            'by_category': by_category,
            'generated_at': timezone.now().isoformat(),
        })


class AGAuditEvidenceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AGAuditEvidence.objects.select_related('audit', 'provided_by')
    serializer_class = AGAuditEvidenceSerializer
    filterset_fields = ['audit', 'category', 'is_provided']
    search_fields = ['description', 'document_reference', 'ag_query_ref']
    ordering = ['category', 'description']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Conflict of Interest ──────────────────────────────────────────────────────

class ConflictOfInterestViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ConflictOfInterest.objects.select_related('declarant', 'witnessed_by')
    serializer_class = ConflictOfInterestSerializer
    filterset_fields = ['status', 'category', 'financial_year', 'declarant', 'is_annual_declaration']
    search_fields = ['description', 'entity_name', 'matter_reference']
    ordering = ['-declaration_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=False, methods=['get'])
    def register(self, request):
        """All declarations for current FY grouped by declarant, with annual declaration status."""
        today = timezone.now().date()
        if today.month >= 4:
            fy = f'{today.year}/{today.year + 1}'
        else:
            fy = f'{today.year - 1}/{today.year}'

        financial_year = request.query_params.get('financial_year', fy)
        org_id = request.user.organisation_id

        declarations = ConflictOfInterest.objects.filter(
            organisation_id=org_id,
            financial_year=financial_year,
        ).select_related('declarant', 'witnessed_by').order_by('declarant__id', '-declaration_date')

        from collections import defaultdict
        grouped = defaultdict(list)
        annual_status = {}

        for declaration in declarations:
            declarant_id = str(declaration.declarant_id)
            grouped[declarant_id].append(
                ConflictOfInterestSerializer(declaration, context={'request': request}).data
            )
            if declaration.is_annual_declaration:
                annual_status[declarant_id] = declaration.status

        result = []
        for declarant_id, decls in grouped.items():
            first = decls[0]
            result.append({
                'declarant_id': declarant_id,
                'declarant_name': first.get('declarant'),
                'annual_declaration_status': annual_status.get(declarant_id, 'pending'),
                'declarations': decls,
                'total_declarations': len(decls),
            })

        return Response({
            'financial_year': financial_year,
            'declarants_count': len(result),
            'register': result,
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="conflict_of_interest_register.csv"'
        writer = csv.writer(response)
        writer.writerow(['Declarant', 'Category', 'Status', 'Financial Year', 'Entity Name', 'Description', 'Declaration Date', 'Is Annual Declaration'])
        for declaration in qs:
            writer.writerow([
                str(declaration.declarant_id), declaration.category, declaration.status,
                declaration.financial_year, declaration.entity_name, declaration.description,
                str(declaration.declaration_date), declaration.is_annual_declaration,
            ])
        return response


# ── Performance Report ────────────────────────────────────────────────────────

class PerformanceReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PerformanceReport.objects.select_related('compact', 'prepared_by', 'approved_by')
    serializer_class = PerformanceReportSerializer
    filterset_fields = ['compact', 'quarter', 'status']
    search_fields = ['executive_summary', 'key_achievements', 'challenges']
    ordering = ['compact__financial_year', 'quarter']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        report = self.get_object()
        report.status = 'submitted'
        report.submitted_date = timezone.now().date()
        report.save(update_fields=['status', 'submitted_date'])
        return Response(PerformanceReportSerializer(report, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        report = self.get_object()
        report.status = 'approved'
        report.approved_by = request.user
        report.approved_date = timezone.now().date()
        report.save(update_fields=['status', 'approved_by', 'approved_date'])
        return Response(PerformanceReportSerializer(report, context={'request': request}).data)


# ── Section 32 Reports ────────────────────────────────────────────────────────

class Section32ReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Section32Report.objects.prefetch_related('programme_lines')
    serializer_class = Section32ReportSerializer
    filterset_fields = ['status', 'financial_year', 'month']
    ordering = ['financial_year', 'month']

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit the Section 32 report to Treasury."""
        report = self.get_object()
        report.status = 'submitted'
        report.submitted_date = timezone.now().date()
        report.save(update_fields=['status', 'submitted_date'])
        return Response(Section32ReportSerializer(report, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="section32_reports.csv"'
        writer = csv.writer(response)
        writer.writerow(['Financial Year', 'Month', 'Status', 'Total Budget', 'Total Actual', 'Variance', 'Submitted Date'])
        for report in qs:
            writer.writerow([
                report.financial_year, report.month, report.status,
                str(getattr(report, 'total_budget', '')),
                str(getattr(report, 'total_actual', '')),
                str(getattr(report, 'variance', '')),
                str(report.submitted_date) if hasattr(report, 'submitted_date') and report.submitted_date else '',
            ])
        return response


# ── Annual Report ─────────────────────────────────────────────────────────────

class AnnualReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AnnualReport.objects.prefetch_related('sections')
    serializer_class = AnnualReportSerializer
    filterset_fields = ['status', 'financial_year']
    ordering = ['-financial_year']

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Returns section status counts for the annual report."""
        report = self.get_object()
        sections = report.sections.all()
        status_counts = {}
        for section in sections:
            status_counts[section.status] = status_counts.get(section.status, 0) + 1
        return Response({
            'report_id': str(report.id),
            'financial_year': report.financial_year,
            'status': report.status,
            'total_sections': sections.count(),
            'status_counts': status_counts,
            'sections': AnnualReportSectionSerializer(sections, many=True, context={'request': request}).data,
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve the annual report at board level."""
        report = self.get_object()
        report.status = 'approved'
        report.approved_by_board_date = timezone.now().date()
        report.save(update_fields=['status', 'approved_by_board_date'])
        return Response(AnnualReportSerializer(report, context={'request': request}).data)


# ── IUFW Disciplinary & Condonement ──────────────────────────────────────────

class IUFWDisciplinaryReferralViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IUFWDisciplinaryReferral.objects.select_related('incident', 'referred_by')
    serializer_class = IUFWDisciplinaryReferralSerializer
    filterset_fields = ['incident', 'outcome']
    search_fields = ['employee_name', 'charge_description']
    ordering = ['-referral_date']


class IUFWCondonementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IUFWCondonement.objects.select_related('incident')
    serializer_class = IUFWCondonementSerializer
    filterset_fields = ['incident', 'condoned_by_board', 'treasury_notification_required']
    ordering = ['-created_at']


# ── Board Member Profiles ─────────────────────────────────────────────────────

from .models import BoardMemberProfile, BoardMemberStatus  # noqa: E402
from .serializers import BoardMemberProfileSerializer  # noqa: E402


class BoardMemberProfileViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = BoardMemberProfile.objects.select_related('user')
    serializer_class = BoardMemberProfileSerializer
    filterset_fields = ['status', 'is_independent', 'annual_declaration_submitted']
    search_fields = ['full_name', 'role_title', 'expertise_areas', 'committee_memberships']
    ordering = ['status', 'appointment_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=False, methods=['get'])
    def active(self, request):
        today = timezone.now().date()
        qs = self.get_queryset().filter(status=BoardMemberStatus.ACTIVE)
        results = []
        for member in qs:
            days_until_term_end = None
            if member.term_end_date:
                days_until_term_end = (member.term_end_date - today).days
            data = BoardMemberProfileSerializer(member, context={'request': request}).data
            data['days_until_term_end'] = days_until_term_end
            results.append(data)
        return Response(results)


# ── Expiry Alerts ─────────────────────────────────────────────────────────────

class ExpiryAlertViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ExpiryAlert.objects.all()
    serializer_class = ExpiryAlertSerializer
    filterset_fields = ['alert_type', 'is_acknowledged', 'auto_created']
    search_fields = ['reference_description']
    ordering = ['expiry_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=['is_acknowledged', 'acknowledged_by', 'acknowledged_at'])
        return Response(ExpiryAlertSerializer(alert, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Returns alerts where expiry_date <= today + days_warning and not acknowledged."""
        import datetime
        from django.db.models import F, ExpressionWrapper, DateField
        today = timezone.now().date()
        # Filter: expiry_date <= today + days_warning AND not acknowledged
        # We compare per-record, so we iterate or use a subquery approach
        qs = self.get_queryset().filter(is_acknowledged=False)
        upcoming_alerts = [
            alert for alert in qs
            if alert.expiry_date <= today + datetime.timedelta(days=alert.days_warning)
        ]
        upcoming_alerts.sort(key=lambda a: a.expiry_date)
        data = ExpiryAlertSerializer(upcoming_alerts, many=True, context={'request': request}).data
        return Response({'upcoming_alerts': data, 'total': len(upcoming_alerts)})
