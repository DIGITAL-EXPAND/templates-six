import pytest
from rest_framework.test import APIClient
from apps.audit.models import AuditEvent
from apps.governance.models import ExecutiveAction
from apps.programming.models import CalendarIssue


# ── Executive Summary ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestExecutiveSummaryView:
    url = '/api/v1/reports/executive-summary/'

    def test_requires_auth(self, client):
        r = APIClient().get(self.url)
        assert r.status_code == 401

    def test_returns_200(self, client_a):
        r = client_a.get(self.url)
        assert r.status_code == 200

    def test_empty_org_defaults(self, client_a):
        r = client_a.get(self.url)
        d = r.data
        assert d['total_contexts'] == 0
        assert d['open_risks'] == 0
        assert d['pending_approvals'] == 0
        assert d['open_tasks'] == 0
        assert d['kpi_summary'] == []
        assert d['upcoming_openings'] == []

    def test_context_counts(self, client_a, context_a):
        r = client_a.get(self.url)
        assert r.data['total_contexts'] == 1
        assert r.data['contexts_by_status']['draft'] == 1

    def test_context_type_breakdown(self, client_a, context_a):
        r = client_a.get(self.url)
        assert 'production' in r.data['contexts_by_type']

    def test_cancelled_context_excluded(self, client_a, org_a, site_a, user_a):
        from apps.contexts.models import OperatingContext
        OperatingContext.objects.create(
            organisation=org_a,
            title='Cancelled Show',
            context_type='production',
            status='cancelled',
            priority='low',
            risk_level='low',
            site=site_a,
            owner=user_a,
        )
        r = client_a.get(self.url)
        assert r.data['total_contexts'] == 0

    def test_open_risks(self, client_a, risk_a):
        r = client_a.get(self.url)
        assert r.data['open_risks'] == 1

    def test_high_risks(self, client_a, risk_a):
        r = client_a.get(self.url)
        assert r.data['high_risks'] == 1

    def test_open_tasks(self, client_a, task_a):
        r = client_a.get(self.url)
        assert r.data['open_tasks'] == 1

    def test_kpi_summary_entry(self, client_a, kpi_a):
        from decimal import Decimal
        from apps.governance.models import KPI
        kpi = KPI.objects.get(id=kpi_a.id)
        kpi.actual_value = Decimal('60.00')
        kpi.save()
        r = client_a.get(self.url)
        summary = r.data['kpi_summary']
        assert len(summary) == 1
        entry = summary[0]
        assert entry['name'] == 'Attendance Rate A'
        assert entry['percentage'] == 75  # 60/80*100

    def test_kpi_zero_target_no_crash(self, client_a, org_a):
        from apps.governance.models import KPI
        KPI.objects.create(
            organisation=org_a,
            name='Zero Target KPI',
            target_value='0.00',
            unit='count',
            reporting_period='annual',
        )
        r = client_a.get(self.url)
        assert r.status_code == 200
        entry = next(e for e in r.data['kpi_summary'] if e['name'] == 'Zero Target KPI')
        assert entry['percentage'] == 0

    def test_upcoming_openings(self, client_a, org_a, site_a, user_a):
        import datetime
        from apps.contexts.models import OperatingContext
        today = datetime.date.today()
        oc = OperatingContext.objects.create(
            organisation=org_a,
            title='Imminent Show',
            context_type='production',
            status='active',
            priority='high',
            risk_level='low',
            site=site_a,
            owner=user_a,
            opening_date=today + datetime.timedelta(days=5),
        )
        r = client_a.get(self.url)
        openings = r.data['upcoming_openings']
        assert len(openings) == 1
        assert openings[0]['title'] == 'Imminent Show'
        assert openings[0]['days_until'] == 5

    def test_upcoming_excludes_past(self, client_a, org_a, site_a, user_a):
        import datetime
        from apps.contexts.models import OperatingContext
        today = datetime.date.today()
        OperatingContext.objects.create(
            organisation=org_a,
            title='Past Show',
            context_type='production',
            status='closed',
            priority='low',
            risk_level='low',
            site=site_a,
            owner=user_a,
            opening_date=today - datetime.timedelta(days=1),
        )
        r = client_a.get(self.url)
        assert r.data['upcoming_openings'] == []

    def test_budget_and_spend_aggregation(self, client_a, org_a, site_a, user_a):
        from decimal import Decimal
        from apps.contexts.models import OperatingContext
        OperatingContext.objects.create(
            organisation=org_a,
            title='Show With Budget',
            context_type='production',
            status='active',
            priority='medium',
            risk_level='low',
            site=site_a,
            owner=user_a,
            budget=Decimal('100000.00'),
            actual_spend=Decimal('45000.00'),
        )
        r = client_a.get(self.url)
        from decimal import Decimal
        assert Decimal(r.data['total_budget']) == Decimal('100000.00')
        assert Decimal(r.data['total_spend']) == Decimal('45000.00')

    def test_tenant_isolation(self, client_a, context_b, risk_b, task_b):
        r = client_a.get(self.url)
        assert r.data['total_contexts'] == 0
        assert r.data['open_risks'] == 0
        assert r.data['open_tasks'] == 0


# ── Context Readiness ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContextReadinessView:
    def url(self, context_id):
        return f'/api/v1/reports/context-readiness/{context_id}/'

    def test_requires_auth(self, context_a):
        r = APIClient().get(self.url(context_a.id))
        assert r.status_code == 401

    def test_returns_200(self, client_a, context_a):
        r = client_a.get(self.url(context_a.id))
        assert r.status_code == 200

    def test_context_fields(self, client_a, context_a):
        r = client_a.get(self.url(context_a.id))
        ctx = r.data['context']
        assert ctx['id'] == str(context_a.id)
        assert ctx['title'] == 'Production A'
        assert ctx['context_type'] == 'production'

    def test_404_for_other_org(self, client_a, context_b):
        r = client_a.get(self.url(context_b.id))
        assert r.status_code == 404

    def test_tasks_summary(self, client_a, context_a, task_a):
        r = client_a.get(self.url(context_a.id))
        tasks = r.data['tasks']
        assert tasks['total'] == 1
        assert tasks['open'] == 1
        assert tasks['done'] == 0

    def test_documents_count(self, client_a, context_a, document_a):
        r = client_a.get(self.url(context_a.id))
        assert r.data['documents_count'] == 1

    def test_contracts_list(self, client_a, context_a, contract_a):
        r = client_a.get(self.url(context_a.id))
        assert len(r.data['contracts']) == 1
        c = r.data['contracts'][0]
        assert c['type'] == 'artist_performance'
        assert c['signed'] is False

    def test_supplier_list(self, client_a, context_a, supplier_engagement_a):
        r = client_a.get(self.url(context_a.id))
        assert len(r.data['suppliers']) == 1
        assert r.data['suppliers'][0]['status'] == 'proposed'

    def test_artist_list(self, client_a, context_a, artist_engagement_a):
        r = client_a.get(self.url(context_a.id))
        assert len(r.data['artists']) == 1
        assert r.data['artists'][0]['name'] == 'Alice P'

    def test_campaign_data(self, client_a, context_a, campaign_a):
        r = client_a.get(self.url(context_a.id))
        camp = r.data['campaign']
        assert camp is not None
        assert camp['level'] == 'standard'
        assert camp['deliverables_total'] == 0

    def test_rider_data(self, client_a, context_a, rider_a):
        r = client_a.get(self.url(context_a.id))
        rider = r.data['rider']
        assert rider is not None
        assert rider['status'] == 'draft'

    def test_foh_data(self, client_a, context_a, foh_plan_a):
        r = client_a.get(self.url(context_a.id))
        foh = r.data['foh_plan']
        assert foh is not None
        assert foh['status'] == 'planning'

    def test_ticketing_data(self, client_a, context_a, ticketing_setup_a):
        r = client_a.get(self.url(context_a.id))
        ts = r.data['ticketing']
        assert ts is not None
        assert ts['provider'] == 'webtickets'

    def test_no_onetoone_returns_null(self, client_a, context_a):
        r = client_a.get(self.url(context_a.id))
        assert r.data['campaign'] is None
        assert r.data['rider'] is None
        assert r.data['foh_plan'] is None
        assert r.data['ticketing'] is None
        assert r.data['youth_project'] is None

    def test_risks_list(self, client_a, context_a, org_a, user_a):
        from apps.governance.models import Risk
        Risk.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Context Risk',
            risk_level='high',
            owner=user_a,
        )
        r = client_a.get(self.url(context_a.id))
        assert len(r.data['risks']) == 1
        assert r.data['risks'][0]['title'] == 'Context Risk'

    def test_youth_data(self, client_a, youth_context_a, youth_project_a):
        r = client_a.get(self.url(youth_context_a.id))
        yp = r.data['youth_project']
        assert yp is not None
        assert yp['target'] == 50
        assert yp['consent_rate'] == 0.0

    def test_signed_contract(self, client_a, context_a, org_a):
        from apps.contracts.models import ContractRecord
        c = ContractRecord.objects.create(
            organisation=org_a,
            operating_context=context_a,
            contract_type='artist_performance',
            counterparty_name='Signed Artist',
            counterparty_type='artist',
            status='signed',
            signatures_required=2,
            signatures_received=2,
        )
        r = client_a.get(self.url(context_a.id))
        match = next(x for x in r.data['contracts'] if x['id'] == str(c.id))
        assert match['signed'] is True


# ── Department Readiness ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContextBlockersAndAuditTrail:
    def readiness_url(self, context_id):
        return f'/api/v1/reports/context-readiness/{context_id}/'

    def audit_url(self, context_id):
        return f'/api/v1/reports/context-audit/{context_id}/'

    def test_blockers_include_calendar_issue_and_executive_action(self, client_a, org_a, context_a, user_a):
        CalendarIssue.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Calendar clash',
            severity='high',
            raised_by=user_a,
        )
        ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='request_change',
            title='Executive change',
            reason='Needs correction',
            instruction='Correct this item.',
            operating_context=context_a,
            created_by=user_a,
        )
        r = client_a.get(self.readiness_url(context_a.id))
        labels = [item['label'] for item in r.data['blockers']]
        assert 'Calendar clash' in labels
        assert 'Executive change' in labels

    def test_blockers_include_pending_approval_and_process_step(self, client_a, org_a, context_a, user_a):
        from apps.approvals.models import ApprovalRoute, ApprovalStep, ApprovalRequest
        from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate
        from apps.workflows.services import instantiate_workflow

        route = ApprovalRoute.objects.create(organisation=org_a, name='Readiness Route')
        approval_step = ApprovalStep.objects.create(
            organisation=org_a, route=route, step_number=1, name='GM Approval',
        )
        ApprovalRequest.objects.create(
            organisation=org_a, operating_context=context_a,
            approval_step=approval_step, requested_by=user_a,
        )
        template = WorkflowTemplate.objects.create(
            organisation=org_a, name='Readiness Process', context_type='production',
        )
        WorkflowStepTemplate.objects.create(
            organisation=org_a, template=template, step_number=1,
            name='Evidence and approval gate',
            requires_evidence=True,
            requires_approval=True,
        )
        instantiate_workflow(context_a, template, user_a)

        r = client_a.get(self.readiness_url(context_a.id))
        types = [item['type'] for item in r.data['blockers']]
        assert 'approval' in types
        assert 'process_step' in types

    def test_context_audit_requires_auth(self, context_a):
        r = APIClient().get(self.audit_url(context_a.id))
        assert r.status_code == 401

    def test_context_audit_returns_workspace_events(self, client_a, org_a, context_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a,
            actor=user_a,
            event_type='test.context_event',
            target_type='Workspace',
            target_id=str(context_a.id),
            payload={'context_id': str(context_a.id)},
        )
        r = client_a.get(self.audit_url(context_a.id))
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_type'] == 'test.context_event'

    def test_context_audit_other_org_returns_404(self, client_a, context_b):
        r = client_a.get(self.audit_url(context_b.id))
        assert r.status_code == 404


@pytest.mark.django_db
class TestDepartmentReadinessView:
    def url(self, dept_id):
        return f'/api/v1/reports/department-readiness/{dept_id}/'

    def test_requires_auth(self, department_a):
        r = APIClient().get(self.url(department_a.id))
        assert r.status_code == 401

    def test_returns_200(self, client_a, department_a):
        r = client_a.get(self.url(department_a.id))
        assert r.status_code == 200

    def test_404_for_other_org(self, client_a, department_b):
        r = client_a.get(self.url(department_b.id))
        assert r.status_code == 404

    def test_department_fields(self, client_a, department_a):
        r = client_a.get(self.url(department_a.id))
        dept = r.data['department']
        assert dept['name'] == 'Technical Department'
        assert dept['department_type'] == 'technical'

    def test_empty_department(self, client_a, department_a):
        r = client_a.get(self.url(department_a.id))
        assert r.data['open_tasks'] == 0
        assert r.data['overdue_tasks'] == 0
        assert r.data['completed_tasks'] == 0
        assert r.data['contexts_count'] == 0
        assert r.data['pending_approvals'] == 0
        assert r.data['open_risks'] == 0

    def test_counts_tasks_in_dept(self, client_a, department_a, org_a, context_a):
        import datetime
        from apps.tasks.models import Task
        Task.objects.create(
            organisation=org_a,
            operating_context=context_a,
            department=department_a,
            title='Dept Task',
            priority='medium',
            status='open',
        )
        r = client_a.get(self.url(department_a.id))
        assert r.data['open_tasks'] == 1

    def test_overdue_tasks(self, client_a, department_a, org_a, context_a):
        import datetime
        from apps.tasks.models import Task
        Task.objects.create(
            organisation=org_a,
            operating_context=context_a,
            department=department_a,
            title='Overdue Task',
            priority='high',
            status='open',
            due_date=datetime.date(2020, 1, 1),
        )
        r = client_a.get(self.url(department_a.id))
        assert r.data['overdue_tasks'] == 1

    def test_contexts_via_dept(self, client_a, department_a, org_a, site_a, user_a):
        from apps.contexts.models import OperatingContext
        OperatingContext.objects.create(
            organisation=org_a,
            title='Dept Context',
            context_type='production',
            status='active',
            priority='medium',
            risk_level='low',
            site=site_a,
            owner=user_a,
            department=department_a,
        )
        r = client_a.get(self.url(department_a.id))
        assert r.data['contexts_count'] == 1

    def test_tenant_isolation(self, client_a, department_b):
        r = client_a.get(self.url(department_b.id))
        assert r.status_code == 404


# ── Youth Summary ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestYouthSummaryView:
    def url(self, project_id):
        return f'/api/v1/reports/youth-summary/{project_id}/'

    def test_requires_auth(self, youth_project_a):
        r = APIClient().get(self.url(youth_project_a.id))
        assert r.status_code == 401

    def test_returns_200(self, client_a, youth_project_a):
        r = client_a.get(self.url(youth_project_a.id))
        assert r.status_code == 200

    def test_404_for_other_org(self, client_a, youth_project_b):
        r = client_a.get(self.url(youth_project_b.id))
        assert r.status_code == 404

    def test_project_fields(self, client_a, youth_project_a, youth_context_a):
        r = client_a.get(self.url(youth_project_a.id))
        p = r.data['project']
        assert p['id'] == str(youth_project_a.id)
        assert p['title'] == 'Youth Orchestra Project A'
        assert p['status'] == 'planning'

    def test_learner_target(self, client_a, youth_project_a):
        r = client_a.get(self.url(youth_project_a.id))
        assert r.data['target_learners'] == 50
        assert r.data['schools'] == 5
        assert r.data['total_learners'] == 0

    def test_consent_rate_zero(self, client_a, youth_project_a):
        r = client_a.get(self.url(youth_project_a.id))
        assert r.data['consent_rate'] == 0.0

    def test_sessions_count(self, client_a, youth_project_a, session_a):
        r = client_a.get(self.url(youth_project_a.id))
        assert r.data['sessions_total'] == 1
        assert r.data['sessions_completed'] == 0

    def test_attendance_rate_computed(self, client_a, org_a, youth_project_a, activity_a):
        import datetime
        from apps.youth.models import Session, AttendanceRecord
        sess = Session.objects.create(
            organisation=org_a,
            activity=activity_a,
            session_date=datetime.date(2026, 5, 1),
            status='completed',
        )
        AttendanceRecord.objects.create(
            organisation=org_a,
            session=sess,
            learner_identifier='L001',
            present=True,
        )
        AttendanceRecord.objects.create(
            organisation=org_a,
            session=sess,
            learner_identifier='L002',
            present=False,
        )
        r = client_a.get(self.url(youth_project_a.id))
        assert r.data['attendance_rate'] == 50.0
        assert r.data['total_learners'] == 2

    def test_activity_list(self, client_a, youth_project_a, activity_a):
        r = client_a.get(self.url(youth_project_a.id))
        acts = r.data['activities']
        assert len(acts) == 1
        assert acts[0]['name'] == 'Violin Rehearsal'

    def test_assessments_count(self, client_a, org_a, youth_project_a, user_a):
        import datetime
        from apps.youth.models import Assessment
        Assessment.objects.create(
            organisation=org_a,
            youth_project=youth_project_a,
            learner_identifier='L001',
            assessment_type='written',
            assessor=user_a,
            assessment_date=datetime.date(2026, 6, 1),
        )
        r = client_a.get(self.url(youth_project_a.id))
        assert r.data['assessments_count'] == 1


# ── Audit Export ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAuditExportView:
    url = '/api/v1/reports/audit-export/'

    def test_requires_auth(self):
        r = APIClient().get(self.url)
        assert r.status_code == 401

    def test_returns_200(self, client_a):
        r = client_a.get(self.url)
        assert r.status_code == 200

    def test_empty_results(self, client_a):
        r = client_a.get(self.url)
        assert r.data['count'] == 0
        assert r.data['results'] == []

    def test_returns_org_events(self, client_a, org_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a,
            actor=user_a,
            event_type='context.created',
            payload={},
        )
        r = client_a.get(self.url)
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_type'] == 'context.created'

    def test_tenant_isolation(self, client_a, org_b, user_b):
        AuditEvent.objects.create(
            organisation=org_b,
            actor=user_b,
            event_type='context.created',
            payload={},
        )
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_filter_by_action(self, client_a, org_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='context.created', payload={},
        )
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='task.completed', payload={},
        )
        r = client_a.get(self.url, {'action': 'created'})
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_type'] == 'context.created'

    def test_filter_by_target_type(self, client_a, org_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='context.created', payload={},
        )
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='task.completed', payload={},
        )
        r = client_a.get(self.url, {'target_type': 'task'})
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_type'] == 'task.completed'

    def test_filter_by_date_range(self, client_a, org_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='context.created', payload={},
        )
        # Filter from a future date — today's event should not appear
        r = client_a.get(self.url, {'from': '2099-01-01'})
        assert r.data['count'] == 0

    def test_pagination(self, client_a, org_a, user_a):
        for i in range(5):
            AuditEvent.objects.create(
                organisation=org_a, actor=user_a,
                event_type=f'context.event_{i}', payload={},
            )
        r = client_a.get(self.url, {'page_size': 2})
        assert r.data['count'] == 5
        assert len(r.data['results']) == 2
        assert r.data['next'] is not None

    def test_event_fields(self, client_a, org_a, user_a):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a,
            event_type='context.created', payload={'key': 'val'},
        )
        r = client_a.get(self.url)
        e = r.data['results'][0]
        assert 'id' in e
        assert 'event_type' in e
        assert 'actor' in e
        assert 'payload' in e
        assert 'created_at' in e
        assert e['actor'] == 'user-a@example.com'
