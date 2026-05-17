"""
Cross-org isolation tests for reports and integrations endpoints.
Verifies that no data from org_b leaks to org_a and vice versa.
"""
import pytest
from rest_framework.test import APIClient
from apps.audit.models import AuditEvent


# ── Executive Summary isolation ────────────────────────────────────────────────

@pytest.mark.django_db
class TestExecutiveSummaryIsolation:
    url = '/api/v1/reports/executive-summary/'

    def test_contexts_not_shared(self, client_a, context_b):
        r = client_a.get(self.url)
        assert r.data['total_contexts'] == 0

    def test_risks_not_shared(self, client_a, risk_b):
        r = client_a.get(self.url)
        assert r.data['open_risks'] == 0
        assert r.data['high_risks'] == 0

    def test_tasks_not_shared(self, client_a, task_b):
        r = client_a.get(self.url)
        assert r.data['open_tasks'] == 0

    def test_kpis_not_shared(self, client_a, kpi_b):
        r = client_a.get(self.url)
        assert r.data['kpi_summary'] == []

    def test_org_b_sees_own_data(self, client_b, context_b, risk_b, task_b):
        r = client_b.get(self.url)
        assert r.data['total_contexts'] == 1
        assert r.data['open_risks'] == 1
        assert r.data['open_tasks'] == 1


# ── Context Readiness isolation ────────────────────────────────────────────────

@pytest.mark.django_db
class TestContextReadinessIsolation:
    def url(self, pk):
        return f'/api/v1/reports/context-readiness/{pk}/'

    def test_org_a_cannot_access_org_b_context(self, client_a, context_b):
        r = client_a.get(self.url(context_b.id))
        assert r.status_code == 404

    def test_org_b_cannot_access_org_a_context(self, client_b, context_a):
        r = client_b.get(self.url(context_a.id))
        assert r.status_code == 404

    def test_tasks_in_org_a_context_not_visible_to_b(self, client_b, context_a, task_a):
        r = client_b.get(self.url(context_a.id))
        assert r.status_code == 404

    def test_org_a_context_visible_to_a(self, client_a, context_a):
        r = client_a.get(self.url(context_a.id))
        assert r.status_code == 200
        assert r.data['context']['id'] == str(context_a.id)


# ── Department Readiness isolation ─────────────────────────────────────────────

@pytest.mark.django_db
class TestDepartmentReadinessIsolation:
    def url(self, pk):
        return f'/api/v1/reports/department-readiness/{pk}/'

    def test_org_a_cannot_access_org_b_department(self, client_a, department_b):
        r = client_a.get(self.url(department_b.id))
        assert r.status_code == 404

    def test_org_b_cannot_access_org_a_department(self, client_b, department_a):
        r = client_b.get(self.url(department_a.id))
        assert r.status_code == 404

    def test_org_a_department_visible_to_a(self, client_a, department_a):
        r = client_a.get(self.url(department_a.id))
        assert r.status_code == 200

    def test_tasks_not_shared_across_orgs(self, client_a, department_a, org_b, context_b, department_b):
        import datetime
        from apps.tasks.models import Task
        Task.objects.create(
            organisation=org_b,
            operating_context=context_b,
            department=department_b,
            title='Org B Task',
            priority='medium',
            status='open',
        )
        r = client_a.get(self.url(department_a.id))
        assert r.data['open_tasks'] == 0


# ── Youth Summary isolation ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestYouthSummaryIsolation:
    def url(self, pk):
        return f'/api/v1/reports/youth-summary/{pk}/'

    def test_org_a_cannot_access_org_b_project(self, client_a, youth_project_b):
        r = client_a.get(self.url(youth_project_b.id))
        assert r.status_code == 404

    def test_org_b_cannot_access_org_a_project(self, client_b, youth_project_a):
        r = client_b.get(self.url(youth_project_a.id))
        assert r.status_code == 404

    def test_org_a_project_visible_to_a(self, client_a, youth_project_a):
        r = client_a.get(self.url(youth_project_a.id))
        assert r.status_code == 200
        assert r.data['project']['id'] == str(youth_project_a.id)

    def test_org_b_project_visible_to_b(self, client_b, youth_project_b):
        r = client_b.get(self.url(youth_project_b.id))
        assert r.status_code == 200


# ── Audit Export isolation ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAuditExportIsolation:
    url = '/api/v1/reports/audit-export/'

    def test_org_a_sees_only_own_events(self, client_a, org_a, org_b, user_a, user_b):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a, event_type='x.created', payload={},
        )
        AuditEvent.objects.create(
            organisation=org_b, actor=user_b, event_type='x.created', payload={},
        )
        r = client_a.get(self.url)
        assert r.data['count'] == 1

    def test_org_b_sees_only_own_events(self, client_b, org_a, org_b, user_a, user_b):
        AuditEvent.objects.create(
            organisation=org_a, actor=user_a, event_type='x.created', payload={},
        )
        AuditEvent.objects.create(
            organisation=org_b, actor=user_b, event_type='y.created', payload={},
        )
        r = client_b.get(self.url)
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_type'] == 'y.created'

    def test_unauthenticated_blocked(self):
        r = APIClient().get(self.url)
        assert r.status_code == 401


# ── Integration Provider isolation ─────────────────────────────────────────────

@pytest.mark.django_db
class TestIntegrationProviderIsolation:
    url = '/api/v1/integrations/providers/'

    def detail_url(self, pk):
        return f'{self.url}{pk}/'

    def test_org_a_list_excludes_org_b(self, client_a, integration_provider_b):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_org_b_list_excludes_org_a(self, client_b, integration_provider_a):
        r = client_b.get(self.url)
        assert r.data['count'] == 0

    def test_org_a_retrieve_org_b_provider_404(self, client_a, integration_provider_b):
        r = client_a.get(self.detail_url(integration_provider_b.id))
        assert r.status_code == 404

    def test_org_b_retrieve_org_a_provider_404(self, client_b, integration_provider_a):
        r = client_b.get(self.detail_url(integration_provider_a.id))
        assert r.status_code == 404

    def test_each_org_sees_own(self, client_a, client_b, integration_provider_a, integration_provider_b):
        ra = client_a.get(self.url)
        rb = client_b.get(self.url)
        assert ra.data['count'] == 1
        assert rb.data['count'] == 1
        assert ra.data['results'][0]['name'] == 'Webtickets'
        assert rb.data['results'][0]['name'] == 'Computicket'


# ── External Reference isolation ───────────────────────────────────────────────

@pytest.mark.django_db
class TestExternalReferenceIsolation:
    url = '/api/v1/integrations/references/'

    def detail_url(self, pk):
        return f'{self.url}{pk}/'

    def test_org_a_list_excludes_org_b(self, client_a, external_reference_b):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_org_b_list_excludes_org_a(self, client_b, external_reference_a):
        r = client_b.get(self.url)
        assert r.data['count'] == 0

    def test_org_a_retrieve_org_b_ref_404(self, client_a, external_reference_b):
        r = client_a.get(self.detail_url(external_reference_b.id))
        assert r.status_code == 404

    def test_org_b_retrieve_org_a_ref_404(self, client_b, external_reference_a):
        r = client_b.get(self.detail_url(external_reference_a.id))
        assert r.status_code == 404

    def test_each_org_sees_own(self, client_a, client_b, external_reference_a, external_reference_b):
        ra = client_a.get(self.url)
        rb = client_b.get(self.url)
        assert ra.data['count'] == 1
        assert rb.data['count'] == 1
        assert ra.data['results'][0]['external_id'] == 'EVT-001'
        assert rb.data['results'][0]['external_id'] == 'EVT-002'
