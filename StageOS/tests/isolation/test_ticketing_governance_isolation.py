import pytest
from apps.ticketing.models import TicketingSetup, SalesImport
from apps.governance.models import KPI, KPIEvidence, Risk, CorrectiveAction


# ── Ticketing fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def setup_a(db, org_a, context_a, user_a):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_a, user_a, {
        'provider': 'webtickets', 'tickets_available': 500,
    })


@pytest.fixture
def setup_b(db, org_b, context_b, user_b):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_b, user_b, {
        'provider': 'computicket', 'tickets_available': 200,
    })


# ── Governance fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def kpi_a(db, org_a):
    return KPI.objects.create(
        organisation=org_a, name='KPI A', target_value='100',
        unit='count', reporting_period='monthly',
    )


@pytest.fixture
def kpi_b(db, org_b):
    return KPI.objects.create(
        organisation=org_b, name='KPI B', target_value='200',
        unit='count', reporting_period='monthly',
    )


@pytest.fixture
def risk_a(db, org_a, user_a):
    return Risk.objects.create(
        organisation=org_a, title='Risk A', risk_level='high', owner=user_a,
    )


@pytest.fixture
def risk_b(db, org_b, user_b):
    return Risk.objects.create(
        organisation=org_b, title='Risk B', risk_level='low', owner=user_b,
    )


@pytest.fixture
def action_a(db, org_a, risk_a, user_a):
    return CorrectiveAction.objects.create(
        organisation=org_a, risk=risk_a,
        action='Action A', owner=user_a,
    )


@pytest.fixture
def action_b(db, org_b, risk_b, user_b):
    return CorrectiveAction.objects.create(
        organisation=org_b, risk=risk_b,
        action='Action B', owner=user_b,
    )


# ── Ticketing isolation ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTicketingSetupIsolation:
    def test_list_excludes_other_org(self, client_a, setup_a, setup_b):
        r = client_a.get('/api/v1/ticketing/setups/')
        ids = [x['id'] for x in r.data['results']]
        assert str(setup_a.id) in ids
        assert str(setup_b.id) not in ids

    def test_retrieve_other_org_returns_404(self, client_a, setup_b):
        r = client_a.get(f'/api/v1/ticketing/setups/{setup_b.id}/')
        assert r.status_code == 404

    def test_update_other_org_returns_404(self, client_a, setup_b):
        r = client_a.patch(f'/api/v1/ticketing/setups/{setup_b.id}/', {
            'notes': 'hacked',
        }, format='json')
        assert r.status_code == 404

    def test_delete_other_org_returns_404(self, client_a, setup_b):
        r = client_a.delete(f'/api/v1/ticketing/setups/{setup_b.id}/')
        assert r.status_code == 404

    def test_go_live_other_org_returns_404(self, client_a, setup_b):
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_b.id}/go-live/', {}, format='json')
        assert r.status_code == 404

    def test_import_sales_other_org_returns_404(self, client_a, setup_b):
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_b.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
        }, format='json')
        assert r.status_code == 404

    def test_settle_other_org_returns_404(self, client_a, setup_b):
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_b.id}/settle/', {
            'amount': '10000.00',
        }, format='json')
        assert r.status_code == 404

    def test_cannot_create_setup_with_other_org_context(self, client_a, context_b):
        r = client_a.post('/api/v1/ticketing/setups/', {
            'operating_context': str(context_b.id),
            'provider': 'webtickets',
        }, format='json')
        assert r.status_code == 400

    def test_sales_imports_exclude_other_org(self, client_a, setup_a, setup_b, user_a, user_b, document_a, document_b):
        from apps.ticketing.services import go_live, import_sales
        go_live(setup_a, user_a)
        go_live(setup_b, user_b)
        import_sales(setup_a, user_a, {
            'tickets_sold': 100, 'revenue': '15000', 'notes': '',
            'source_file': document_a,
        })
        import_sales(setup_b, user_b, {
            'tickets_sold': 50, 'revenue': '7500', 'notes': '',
            'source_file': document_b,
        })
        r = client_a.get('/api/v1/ticketing/sales-imports/')
        assert r.data['count'] == 1


# ── Governance isolation ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestKPIIsolation:
    def test_list_excludes_other_org(self, client_a, kpi_a, kpi_b):
        r = client_a.get('/api/v1/governance/kpis/')
        ids = [x['id'] for x in r.data['results']]
        assert str(kpi_a.id) in ids
        assert str(kpi_b.id) not in ids

    def test_retrieve_other_org_returns_404(self, client_a, kpi_b):
        r = client_a.get(f'/api/v1/governance/kpis/{kpi_b.id}/')
        assert r.status_code == 404

    def test_update_other_org_returns_404(self, client_a, kpi_b):
        r = client_a.patch(f'/api/v1/governance/kpis/{kpi_b.id}/', {
            'target_value': '999',
        }, format='json')
        assert r.status_code == 404

    def test_report_other_org_kpi_returns_404(self, client_a, kpi_b):
        r = client_a.post(f'/api/v1/governance/kpis/{kpi_b.id}/report/', {
            'value': '50',
        }, format='json')
        assert r.status_code == 404

    def test_cannot_report_kpi_with_other_org_context(self, client_a, kpi_a, context_b):
        r = client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '50',
            'context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_kpi_evidence_excludes_other_org(self, client_a, kpi_a, kpi_b, user_a, user_b):
        KPIEvidence.objects.create(
            organisation=kpi_a.organisation, kpi=kpi_a,
            value_reported='70', reported_by=user_a,
        )
        KPIEvidence.objects.create(
            organisation=kpi_b.organisation, kpi=kpi_b,
            value_reported='80', reported_by=user_b,
        )
        r = client_a.get('/api/v1/governance/kpi-evidence/')
        assert r.data['count'] == 1


@pytest.mark.django_db
class TestRiskIsolation:
    def test_list_excludes_other_org(self, client_a, risk_a, risk_b):
        r = client_a.get('/api/v1/governance/risks/')
        ids = [x['id'] for x in r.data['results']]
        assert str(risk_a.id) in ids
        assert str(risk_b.id) not in ids

    def test_retrieve_other_org_returns_404(self, client_a, risk_b):
        r = client_a.get(f'/api/v1/governance/risks/{risk_b.id}/')
        assert r.status_code == 404

    def test_update_other_org_returns_404(self, client_a, risk_b):
        r = client_a.patch(f'/api/v1/governance/risks/{risk_b.id}/', {
            'title': 'Hacked',
        }, format='json')
        assert r.status_code == 404

    def test_close_other_org_risk_returns_404(self, client_a, risk_b):
        r = client_a.post(f'/api/v1/governance/risks/{risk_b.id}/close/', {}, format='json')
        assert r.status_code == 404

    def test_cannot_create_risk_with_other_org_context(self, client_a, context_b, user_a):
        r = client_a.post('/api/v1/governance/risks/', {
            'title': 'Cross-org risk',
            'risk_level': 'low',
            'owner': str(user_a.id),
            'operating_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestCorrectiveActionIsolation:
    def test_list_excludes_other_org(self, client_a, action_a, action_b):
        r = client_a.get('/api/v1/governance/corrective-actions/')
        ids = [x['id'] for x in r.data['results']]
        assert str(action_a.id) in ids
        assert str(action_b.id) not in ids

    def test_retrieve_other_org_returns_404(self, client_a, action_b):
        r = client_a.get(f'/api/v1/governance/corrective-actions/{action_b.id}/')
        assert r.status_code == 404

    def test_complete_other_org_action_returns_404(self, client_a, action_b):
        r = client_a.post(
            f'/api/v1/governance/corrective-actions/{action_b.id}/complete/',
            {}, format='json',
        )
        assert r.status_code == 404

    def test_cannot_create_action_with_other_org_risk(self, client_a, risk_b, user_a):
        r = client_a.post('/api/v1/governance/corrective-actions/', {
            'risk': str(risk_b.id),
            'action': 'Cross-org action',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400
