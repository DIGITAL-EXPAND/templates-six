from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Avg, Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import StandardPagination
from common.permissions import CanAccessReports, CanAccessAudit
from apps.audit.services import AuditService
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from apps.tasks.models import Task
from apps.documents.models import Document
from apps.contracts.models import ContractRecord
from apps.suppliers.models import Supplier, SupplierDocument, SupplierEngagement
from apps.artists.models import ArtistEngagement
from apps.approvals.models import ApprovalRequest
from apps.governance.models import ExecutiveAction, KPI, Risk
from apps.programming.models import CalendarIssue
from apps.structure.models import Department
from apps.workflows.models import WorkflowStepInstance


class ExecutiveSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        today = date.today()

        contexts = OperatingContext.objects.filter(
            organisation=org,
        ).exclude(status='cancelled')

        by_status = {}
        for row in contexts.values('status').annotate(n=Count('id')):
            by_status[row['status']] = row['n']

        by_type = {}
        for row in contexts.values('context_type').annotate(n=Count('id')):
            by_type[row['context_type']] = row['n']

        agg = contexts.aggregate(
            total_budget=Sum('budget'),
            total_spend=Sum('actual_spend'),
            avg_readiness=Avg('readiness_score'),
        )

        open_risks = Risk.objects.filter(organisation=org).exclude(status='closed').count()
        high_risks = Risk.objects.filter(
            organisation=org,
            risk_level__in=['high', 'critical'],
        ).exclude(status='closed').count()

        pending_approvals = ApprovalRequest.objects.filter(
            organisation=org, decision='pending',
        ).count()

        open_tasks = Task.objects.filter(organisation=org).exclude(
            status__in=['done', 'cancelled'],
        ).count()

        kpis = KPI.objects.filter(organisation=org, is_active=True)
        kpi_summary = []
        for kpi in kpis:
            target = kpi.target_value or Decimal('0')
            actual = kpi.actual_value or Decimal('0')
            pct = int((actual / target * 100).quantize(Decimal('1'))) if target else 0
            kpi_summary.append({
                'id': str(kpi.id),
                'name': kpi.name,
                'target': str(target),
                'actual': str(actual),
                'unit': kpi.unit,
                'percentage': pct,
            })

        window_end = today + timedelta(days=30)
        upcoming_qs = contexts.filter(
            opening_date__gte=today,
            opening_date__lte=window_end,
        ).order_by('opening_date')
        upcoming_openings = [
            {
                'id': str(c.id),
                'title': c.title,
                'opening_date': c.opening_date.isoformat(),
                'days_until': (c.opening_date - today).days,
            }
            for c in upcoming_qs
        ]

        return Response({
            'total_contexts': contexts.count(),
            'contexts_by_status': by_status,
            'contexts_by_type': by_type,
            'total_budget': str(agg['total_budget'] or Decimal('0')),
            'total_spend': str(agg['total_spend'] or Decimal('0')),
            'average_readiness': round(agg['avg_readiness'] or 0),
            'open_risks': open_risks,
            'high_risks': high_risks,
            'pending_approvals': pending_approvals,
            'open_tasks': open_tasks,
            'kpi_summary': kpi_summary,
            'upcoming_openings': upcoming_openings,
        })


class ContextReadinessView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request, context_id):
        org = request.user.organisation
        try:
            ctx = OperatingContext.objects.get(id=context_id, organisation=org)
        except OperatingContext.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Approvals
        approval_list = []
        for ar in ApprovalRequest.objects.filter(
            operating_context=ctx,
        ).select_related('approval_step', 'decided_by'):
            approval_list.append({
                'step_name': ar.approval_step.name,
                'decision': ar.decision,
                'decided_by': ar.decided_by.email if ar.decided_by else None,
                'decided_at': ar.decided_at.isoformat() if ar.decided_at else None,
            })

        # Tasks
        tasks_qs = Task.objects.filter(operating_context=ctx).select_related('assigned_to')
        task_counts = tasks_qs.aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status__in=['open', 'in_progress'])),
            done=Count('id', filter=Q(status='done')),
            blocked=Count('id', filter=Q(status='blocked')),
        )

        # Documents
        docs_count = Document.objects.filter(operating_context=ctx).count()

        # Contracts
        contract_list = []
        for c in ContractRecord.objects.filter(operating_context=ctx):
            signed = (
                c.signatures_required > 0
                and c.signatures_received >= c.signatures_required
            )
            contract_list.append({
                'id': str(c.id),
                'type': c.contract_type,
                'counterparty': c.counterparty_name,
                'status': c.status,
                'signed': signed,
            })

        # Suppliers
        supplier_list = []
        for eng in SupplierEngagement.objects.filter(
            operating_context=ctx,
        ).select_related('supplier'):
            supplier_list.append({
                'id': str(eng.supplier.id),
                'name': eng.supplier.name,
                'status': eng.status,
                'csd_verified': eng.supplier.csd_verified,
            })

        # Artists
        artist_list = []
        for eng in ArtistEngagement.objects.filter(
            operating_context=ctx,
        ).select_related('artist'):
            artist_list.append({
                'id': str(eng.artist.id),
                'name': eng.artist.professional_name or eng.artist.legal_name,
                'status': eng.status,
            })

        # Campaign (OneToOne, may not exist)
        campaign_data = None
        try:
            camp = ctx.campaign
            deliverables = camp.deliverables.all()
            campaign_data = {
                'level': camp.campaign_level,
                'status': camp.status,
                'deliverables_total': deliverables.count(),
                'deliverables_complete': deliverables.filter(status='completed').count(),
            }
        except ObjectDoesNotExist:
            pass

        # Technical rider (OneToOne)
        rider_data = None
        try:
            rider = ctx.technical_rider
            rider_data = {
                'status': rider.status,
                'crew_size': rider.crew_size,
            }
        except ObjectDoesNotExist:
            pass

        # FOH plan (OneToOne)
        foh_data = None
        try:
            foh = ctx.foh_plan
            incidents = ctx.incidents.count()
            foh_data = {
                'status': foh.status,
                'incidents': incidents,
            }
        except ObjectDoesNotExist:
            pass

        # Ticketing (OneToOne)
        ticketing_data = None
        try:
            ts = ctx.ticketing_setup
            ticketing_data = {
                'provider': ts.provider,
                'setup_status': ts.setup_status,
                'tickets_sold': ts.tickets_sold,
                'settlement_status': ts.settlement_status,
            }
        except ObjectDoesNotExist:
            pass

        # Youth project (OneToOne)
        youth_data = None
        try:
            yp = ctx.youth_project
            from apps.youth.models import AttendanceRecord, ConsentRecord, Session
            unique_learners = AttendanceRecord.objects.filter(
                session__activity__youth_project=yp,
            ).values('learner_identifier').distinct().count()
            consent_total = ConsentRecord.objects.filter(youth_project=yp).count()
            consent_received = ConsentRecord.objects.filter(
                youth_project=yp, guardian_consent_received=True,
            ).count()
            consent_rate = round(
                (consent_received / consent_total * 100) if consent_total else 0.0, 1,
            )
            sessions_done = Session.objects.filter(
                activity__youth_project=yp, status='completed',
            ).count()
            youth_data = {
                'status': yp.status,
                'learners': unique_learners,
                'target': yp.target_learners,
                'consent_rate': consent_rate,
                'sessions_completed': sessions_done,
            }
        except ObjectDoesNotExist:
            pass

        # Risks
        risk_list = [
            {
                'id': str(r.id),
                'title': r.title,
                'level': r.risk_level,
                'status': r.status,
            }
            for r in Risk.objects.filter(operating_context=ctx)
        ]

        today = date.today()
        blockers = []
        for task in tasks_qs.exclude(status__in=['done', 'cancelled']):
            if task.status == 'blocked':
                blockers.append({
                    'type': 'task',
                    'severity': 'high',
                    'label': task.title,
                    'detail': 'Task is blocked.',
                    'owner': task.assigned_to.email if task.assigned_to else None,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                })
            elif task.due_date and task.due_date < today:
                blockers.append({
                    'type': 'task',
                    'severity': 'medium',
                    'label': task.title,
                    'detail': 'Task is overdue.',
                    'owner': task.assigned_to.email if task.assigned_to else None,
                    'due_date': task.due_date.isoformat(),
                })
            if task.evidence_required and not task.evidence_provided:
                blockers.append({
                    'type': 'evidence',
                    'severity': 'medium',
                    'label': task.title,
                    'detail': 'Required evidence has not been accepted.',
                    'owner': task.assigned_to.email if task.assigned_to else None,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                })

        for issue in CalendarIssue.objects.filter(operating_context=ctx).exclude(
            status__in=['resolved', 'cancelled'],
        ):
            blockers.append({
                'type': 'calendar_issue',
                'severity': issue.severity,
                'label': issue.title,
                'detail': issue.description,
                'owner': issue.department.name if issue.department else None,
                'due_date': issue.due_date.isoformat() if issue.due_date else None,
            })

        for action_obj in ExecutiveAction.objects.filter(operating_context=ctx).exclude(
            status__in=['completed', 'cancelled'],
        ):
            blockers.append({
                'type': 'executive_action',
                'severity': 'high' if action_obj.action_type in ['override', 'decline', 'escalate'] else 'medium',
                'label': action_obj.title,
                'detail': action_obj.instruction or action_obj.reason,
                'owner': action_obj.assigned_to.email if action_obj.assigned_to else None,
                'due_date': action_obj.due_date.isoformat() if action_obj.due_date else None,
            })

        for approval in ApprovalRequest.objects.filter(operating_context=ctx, decision='pending'):
            blockers.append({
                'type': 'approval',
                'severity': 'medium',
                'label': approval.approval_step.name,
                'detail': 'Approval is still pending.',
                'owner': approval.approval_step.approver_department.name if approval.approval_step.approver_department else None,
                'due_date': None,
            })

        for step in WorkflowStepInstance.objects.select_related(
            'workflow_instance', 'step_template', 'assigned_to', 'approval_request',
        ).filter(workflow_instance__operating_context=ctx).exclude(status__in=['completed', 'skipped']):
            step_blockers = []
            if step.step_template.requires_evidence and step.evidence_document_id is None:
                step_blockers.append('Required evidence is not linked.')
            if step.step_template.requires_approval:
                if step.approval_request_id is None:
                    step_blockers.append('Required approval is not linked.')
                elif step.approval_request.decision not in ['approved', 'exception_approved']:
                    step_blockers.append('Linked approval is not approved.')
            if step_blockers:
                blockers.append({
                    'type': 'process_step',
                    'severity': 'medium',
                    'label': step.step_template.name,
                    'detail': ' '.join(step_blockers),
                    'owner': step.assigned_to.email if step.assigned_to else step.step_template.owner_role_description or None,
                    'due_date': None,
                })

        return Response({
            'context': {
                'id': str(ctx.id),
                'title': ctx.title,
                'context_type': ctx.context_type,
                'status': ctx.status,
                'readiness_score': ctx.readiness_score,
                'opening_date': ctx.opening_date.isoformat() if ctx.opening_date else None,
            },
            'approvals': approval_list,
            'tasks': task_counts,
            'documents_count': docs_count,
            'contracts': contract_list,
            'suppliers': supplier_list,
            'artists': artist_list,
            'campaign': campaign_data,
            'rider': rider_data,
            'foh_plan': foh_data,
            'ticketing': ticketing_data,
            'youth_project': youth_data,
            'risks': risk_list,
            'blockers': blockers,
        })


class ContextAuditTrailView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessAudit]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request, context_id):
        org = request.user.organisation
        try:
            ctx = OperatingContext.objects.get(id=context_id, organisation=org)
        except OperatingContext.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        context_value = str(ctx.id)
        qs = AuditEvent.objects.filter(organisation=org).filter(
            Q(target_id=context_value)
            | Q(payload__context_id=context_value)
            | Q(payload__operating_context_id=context_value)
        ).order_by('-created_at')

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        data = [
            {
                'id': str(event.id),
                'event_type': event.event_type,
                'actor': event.actor.email if event.actor else None,
                'target_type': event.target_type,
                'target_id': event.target_id,
                'reason': event.reason,
                'payload': event.payload,
                'created_at': event.created_at.isoformat(),
            }
            for event in page
        ]
        return paginator.get_paginated_response(data)


class DepartmentReadinessView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request, department_id):
        org = request.user.organisation
        try:
            dept = Department.objects.get(id=department_id, organisation=org)
        except Department.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()

        open_statuses = ['open', 'in_progress', 'blocked']

        dept_tasks = Task.objects.filter(organisation=org, department=dept)

        open_tasks = dept_tasks.filter(status__in=open_statuses).count()
        overdue_tasks = dept_tasks.filter(
            status__in=open_statuses,
            due_date__lt=today,
        ).count()
        completed_tasks = dept_tasks.filter(status='done').count()

        # contexts where dept owns tasks OR is the context's owning department
        context_ids_via_tasks = dept_tasks.values_list('operating_context_id', flat=True).distinct()
        context_ids_via_dept = OperatingContext.objects.filter(
            organisation=org, department=dept,
        ).values_list('id', flat=True)
        all_context_ids = set(list(context_ids_via_tasks) + list(context_ids_via_dept))
        contexts_count = len(all_context_ids)

        pending_approvals = ApprovalRequest.objects.filter(
            organisation=org,
            approval_step__approver_department=dept,
            decision='pending',
        ).count()

        # Risks linked to contexts owned by this department
        open_risks = Risk.objects.filter(
            organisation=org,
            operating_context__department=dept,
        ).exclude(status='closed').count()

        return Response({
            'department': {
                'id': str(dept.id),
                'name': dept.name,
                'department_type': dept.department_type,
            },
            'contexts_count': contexts_count,
            'open_tasks': open_tasks,
            'overdue_tasks': overdue_tasks,
            'completed_tasks': completed_tasks,
            'pending_approvals': pending_approvals,
            'open_risks': open_risks,
        })


class YouthSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request, project_id):
        org = request.user.organisation
        from apps.youth.models import (
            YouthProject, AttendanceRecord, ConsentRecord,
            Session, FacilitatorAssignment, ShowcaseOutput, Assessment,
        )
        try:
            yp = YouthProject.objects.select_related('operating_context').get(
                id=project_id,
                operating_context__organisation=org,
            )
        except YouthProject.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Learners: unique identifiers across attendance
        total_learners = AttendanceRecord.objects.filter(
            session__activity__youth_project=yp,
        ).values('learner_identifier').distinct().count()

        # Consent
        consent_total = ConsentRecord.objects.filter(youth_project=yp).count()
        consent_received = ConsentRecord.objects.filter(
            youth_project=yp, guardian_consent_received=True,
        ).count()
        consent_rate = round(
            (consent_received / consent_total * 100) if consent_total else 0.0, 1,
        )

        # Sessions
        sessions_qs = Session.objects.filter(activity__youth_project=yp)
        sessions_total = sessions_qs.count()
        sessions_completed = sessions_qs.filter(status='completed').count()

        # Attendance rate: single aggregation across all completed-session records
        att_agg = AttendanceRecord.objects.filter(
            session__activity__youth_project=yp,
            session__status='completed',
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(present=True)),
        )
        attendance_rate = round(
            (att_agg['present'] / att_agg['total'] * 100) if att_agg['total'] else 0.0, 1,
        )

        # Facilitators
        facilitators = FacilitatorAssignment.objects.filter(youth_project=yp)
        facilitators_count = facilitators.values('facilitator').distinct().count()
        facilitators_vetted = facilitators.filter(is_vetted=True).values('facilitator').distinct().count()

        # Activities with session counts
        activities_list = []
        for act in yp.activities.all():
            act_sessions = Session.objects.filter(activity=act)
            activities_list.append({
                'id': str(act.id),
                'name': act.name,
                'type': act.activity_type,
                'sessions_total': act_sessions.count(),
                'sessions_completed': act_sessions.filter(status='completed').count(),
            })

        # Showcases
        showcases_list = []
        for sc in ShowcaseOutput.objects.filter(youth_project=yp).select_related('output_context'):
            showcases_list.append({
                'id': str(sc.id),
                'title': sc.title,
                'type': sc.output_type,
                'date': sc.date.isoformat() if sc.date else None,
                'has_production_context': sc.output_context_id is not None,
            })

        assessments_count = Assessment.objects.filter(youth_project=yp).count()

        return Response({
            'project': {
                'id': str(yp.id),
                'title': yp.operating_context.title,
                'status': yp.status,
            },
            'total_learners': total_learners,
            'target_learners': yp.target_learners,
            'schools': yp.target_schools,
            'consent_total': consent_total,
            'consent_received': consent_received,
            'consent_rate': consent_rate,
            'sessions_total': sessions_total,
            'sessions_completed': sessions_completed,
            'attendance_rate': attendance_rate,
            'facilitators': facilitators_count,
            'facilitators_vetted': facilitators_vetted,
            'activities': activities_list,
            'showcases': showcases_list,
            'assessments_count': assessments_count,
        })


class RiskRegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        risks = Risk.objects.filter(organisation=org).select_related('operating_context', 'owner')
        rows = []
        by_level: dict = {}
        by_status: dict = {}
        open_count = 0
        high_critical_open = 0
        for risk in risks:
            by_level[risk.risk_level] = by_level.get(risk.risk_level, 0) + 1
            by_status[risk.status] = by_status.get(risk.status, 0) + 1
            if risk.status != 'closed':
                open_count += 1
                if risk.risk_level in ('high', 'critical'):
                    high_critical_open += 1
            rows.append({
                'id': str(risk.id),
                'title': risk.title,
                'level': risk.risk_level,
                'status': risk.status,
                'workspace': risk.operating_context.title if risk.operating_context else None,
                'owner': risk.owner.email if risk.owner else None,
                'raised_date': risk.raised_date.isoformat() if risk.raised_date else None,
                'mitigation': risk.mitigation_plan,
            })
        return Response({
            'total': len(rows),
            'open': open_count,
            'high_or_critical': high_critical_open,
            'by_level': by_level,
            'by_status': by_status,
            'results': rows,
        })


class ContractStatusReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        contracts = ContractRecord.objects.filter(organisation=org).select_related('operating_context')
        rows = []
        by_status: dict = {}
        total_value = Decimal('0')
        pending_sig = 0
        signed_count = 0
        for contract in contracts:
            by_status[contract.status] = by_status.get(contract.status, 0) + 1
            total_value += contract.value or Decimal('0')
            if contract.status in ('issued', 'counter_signed'):
                pending_sig += 1
            if contract.status == 'signed':
                signed_count += 1
            rows.append({
                'id': str(contract.id),
                'workspace': contract.operating_context.title,
                'counterparty': contract.counterparty_name,
                'type': contract.contract_type,
                'status': contract.status,
                'value': str(contract.value),
                'currency': contract.currency,
                'signatures': f'{contract.signatures_received}/{contract.signatures_required}',
                'signed_document': str(contract.signed_document_id) if contract.signed_document_id else None,
            })
        return Response({
            'total': len(rows),
            'total_value': str(total_value),
            'pending_signature': pending_sig,
            'signed': signed_count,
            'by_status': by_status,
            'results': rows,
        })


class SupplierReadinessReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        suppliers = Supplier.objects.filter(organisation=org)
        documents = SupplierDocument.objects.filter(organisation=org)
        engagements = SupplierEngagement.objects.filter(organisation=org).select_related('operating_context')

        # Pre-build engagement map to avoid N+1 (one query, not one per supplier)
        from collections import defaultdict
        eng_workspaces: dict = defaultdict(list)
        for eng in engagements:
            eng_workspaces[eng.supplier_id].append(eng.operating_context.title)

        # Pre-build doc counts per supplier
        doc_total_map: dict = defaultdict(int)
        doc_unverified_map: dict = defaultdict(int)
        for doc in documents:
            doc_total_map[doc.supplier_id] += 1
            if doc.status != 'verified':
                doc_unverified_map[doc.supplier_id] += 1

        rows = []
        for supplier in suppliers:
            rows.append({
                'id': str(supplier.id),
                'name': supplier.name,
                'status': supplier.status,
                'category': supplier.category,
                'csd_verified': supplier.csd_verified,
                'documents_total': doc_total_map[supplier.id],
                'documents_missing_or_unverified': doc_unverified_map[supplier.id],
                'workspaces': eng_workspaces[supplier.id],
            })
        verified_count = sum(1 for s in suppliers if s.csd_verified)
        doc_gap_count = sum(doc_unverified_map.values())
        return Response({
            'total': len(rows),
            'verified': verified_count,
            'pending_verification': len(rows) - verified_count,
            'document_gaps': doc_gap_count,
            'engagements': sum(len(v) for v in eng_workspaces.values()),
            'results': rows,
        })


class EvidenceGapsReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        task_gaps = Task.objects.filter(
            organisation=org,
            evidence_required=True,
            evidence_provided=False,
        ).exclude(status__in=['done', 'cancelled']).select_related('operating_context', 'assigned_to')
        process_gaps = WorkflowStepInstance.objects.filter(
            organisation=org,
            step_template__requires_evidence=True,
            evidence_document__isnull=True,
        ).exclude(status__in=['completed', 'skipped']).select_related('workflow_instance__operating_context', 'step_template', 'assigned_to')
        rows = []
        for task in task_gaps:
            rows.append({
                'type': 'task',
                'id': str(task.id),
                'title': task.title,
                'workspace': task.operating_context.title,
                'owner': task.assigned_to.email if task.assigned_to else None,
                'due_date': task.due_date.isoformat() if task.due_date else None,
            })
        for step in process_gaps:
            rows.append({
                'type': 'process_step',
                'id': str(step.id),
                'title': step.step_template.name,
                'workspace': step.workflow_instance.operating_context.title,
                'owner': step.assigned_to.email if step.assigned_to else step.step_template.owner_role_description,
                'due_date': None,
            })
        return Response({
            'total': len(rows),
            'task_gaps': task_gaps.count(),
            'process_step_gaps': process_gaps.count(),
            'results': rows,
        })


class CalendarIssuesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        issues = CalendarIssue.objects.filter(organisation=org).select_related('operating_context', 'department', 'raised_by')
        open_issues = issues.exclude(status__in=['resolved', 'cancelled'])
        rows = [{
            'id': str(issue.id),
            'title': issue.title,
            'severity': issue.severity,
            'status': issue.status,
            'workspace': issue.operating_context.title if issue.operating_context else None,
            'department': issue.department.name if issue.department else None,
            'due_date': issue.due_date.isoformat() if issue.due_date else None,
            'raised_by': issue.raised_by.email if issue.raised_by else None,
        } for issue in issues]
        return Response({
            'total': issues.count(),
            'open': open_issues.count(),
            'critical_or_high': open_issues.filter(severity__in=['critical', 'high']).count(),
            'results': rows,
        })


class BoardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessReports]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        contexts = OperatingContext.objects.filter(organisation=org).exclude(status='cancelled')
        risks = Risk.objects.filter(organisation=org).exclude(status='closed')
        approvals = ApprovalRequest.objects.filter(organisation=org, decision='pending')
        evidence_gaps = Task.objects.filter(
            organisation=org, evidence_required=True, evidence_provided=False,
        ).exclude(status__in=['done', 'cancelled']).count()
        calendar_issues = CalendarIssue.objects.filter(organisation=org).exclude(status__in=['resolved', 'cancelled']).count()
        return Response({
            'workspaces': contexts.count(),
            'average_readiness': round(contexts.aggregate(avg=Avg('readiness_score'))['avg'] or 0),
            'high_risks': risks.filter(risk_level__in=['high', 'critical']).count(),
            'pending_approvals': approvals.count(),
            'evidence_gaps': evidence_gaps,
            'calendar_issues': calendar_issues,
            'board_ready': risks.filter(risk_level__in=['high', 'critical']).count() == 0 and approvals.count() == 0,
        })


class AuditExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanAccessAudit]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        org = request.user.organisation
        qs = AuditEvent.objects.filter(organisation=org).order_by('-created_at')

        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        action = request.query_params.get('action')
        target_type = request.query_params.get('target_type')

        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        if action:
            qs = qs.filter(event_type__icontains=action)
        if target_type:
            qs = qs.filter(event_type__startswith=target_type)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        data = [
            {
                'id': str(e.id),
                'event_type': e.event_type,
                'actor': e.actor.email if e.actor else None,
                'payload': e.payload,
                'created_at': e.created_at.isoformat(),
            }
            for e in page
        ]
        AuditService.record(
            organisation=org,
            actor=request.user,
            event_type='audit.exported',
            target_type='AuditEvent',
            reason='Audit export requested',
            payload={
                'from': from_date,
                'to': to_date,
                'action': action,
                'target_type': target_type,
            },
        )
        return paginator.get_paginated_response(data)
