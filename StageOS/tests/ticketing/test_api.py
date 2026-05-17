import pytest
from apps.ticketing.models import TicketingSetup, SalesImport
from apps.audit.models import AuditEvent


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def setup_a(db, org_a, context_a, user_a):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_a, user_a, {
        'provider': 'webtickets',
        'tickets_available': 500,
    })


@pytest.fixture
def setup_b(db, org_b, context_b, user_b):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_b, user_b, {
        'provider': 'computicket',
        'tickets_available': 200,
    })


@pytest.fixture
def live_setup(db, org_a, context_a, user_a):
    from apps.ticketing.services import create_ticketing_setup, go_live
    setup = create_ticketing_setup(context_a, user_a, {
        'provider': 'webtickets',
        'tickets_available': 500,
    })
    go_live(setup, user_a)
    return setup


# ── CRUD ──────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTicketingSetupCRUD:
    def test_create(self, client_a, context_a):
        r = client_a.post('/api/v1/ticketing/setups/', {
            'operating_context': str(context_a.id),
            'provider': 'webtickets',
            'tickets_available': 500,
        }, format='json')
        assert r.status_code == 201
        assert r.data['provider'] == 'webtickets'
        assert r.data['setup_status'] == 'awaiting_setup'

    def test_create_emits_audit_event(self, client_a, context_a):
        client_a.post('/api/v1/ticketing/setups/', {
            'operating_context': str(context_a.id),
            'provider': 'internal_rsvp',
            'tickets_available': 100,
        }, format='json')
        assert AuditEvent.objects.filter(event_type='ticketing.setup_created').count() == 1

    def test_unique_per_context_enforced(self, client_a, context_a, setup_a):
        r = client_a.post('/api/v1/ticketing/setups/', {
            'operating_context': str(context_a.id),
            'provider': 'computicket',
        }, format='json')
        assert r.status_code == 400

    def test_list(self, client_a, setup_a):
        r = client_a.get('/api/v1/ticketing/setups/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_retrieve(self, client_a, setup_a):
        r = client_a.get(f'/api/v1/ticketing/setups/{setup_a.id}/')
        assert r.status_code == 200

    def test_update(self, client_a, setup_a):
        r = client_a.patch(f'/api/v1/ticketing/setups/{setup_a.id}/', {
            'booking_link': 'https://webtickets.co.za/event/123',
        }, format='json')
        assert r.status_code == 200

    def test_delete(self, client_a, setup_a):
        r = client_a.delete(f'/api/v1/ticketing/setups/{setup_a.id}/')
        assert r.status_code == 405

    def test_filter_by_provider(self, client_a, setup_a):
        r = client_a.get('/api/v1/ticketing/setups/?provider=webtickets')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_cannot_create_with_other_org_context(self, client_a, context_b):
        r = client_a.post('/api/v1/ticketing/setups/', {
            'operating_context': str(context_b.id),
            'provider': 'webtickets',
        }, format='json')
        assert r.status_code == 400


# ── Go-live action ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGoLiveAction:
    def test_go_live_from_awaiting_setup(self, client_a, setup_a):
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_a.id}/go-live/', {}, format='json')
        assert r.status_code == 200
        assert r.data['setup_status'] == 'live'

    def test_go_live_from_in_progress(self, client_a, setup_a):
        setup_a.setup_status = 'in_progress'
        setup_a.save()
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_a.id}/go-live/', {}, format='json')
        assert r.status_code == 200
        assert r.data['setup_status'] == 'live'

    def test_go_live_when_already_live_returns_400(self, client_a, live_setup):
        r = client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/go-live/', {}, format='json')
        assert r.status_code == 400

    def test_go_live_emits_audit_event(self, client_a, setup_a):
        client_a.post(f'/api/v1/ticketing/setups/{setup_a.id}/go-live/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='ticketing.live').count() == 1


# ── Import-sales action ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestImportSalesAction:
    def test_import_when_live(self, client_a, live_setup, document_a):
        r = client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 350,
            'revenue': '52500.00',
            'source_file': str(document_a.id),
            'notes': 'May import',
        }, format='json')
        assert r.status_code == 200
        assert r.data['tickets_sold'] == 350

    def test_import_without_source_file_returns_400(self, client_a, live_setup):
        r = client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 350,
            'revenue': '52500.00',
            'notes': 'Missing source file',
        }, format='json')
        assert r.status_code == 400

    def test_import_when_not_live_returns_400(self, client_a, setup_a, document_a):
        r = client_a.post(f'/api/v1/ticketing/setups/{setup_a.id}/import-sales/', {
            'tickets_sold': 100,
            'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_import_updates_tickets_sold(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 200,
            'revenue': '30000.00',
            'source_file': str(document_a.id),
        }, format='json')
        live_setup.refresh_from_db()
        assert live_setup.tickets_sold == 200
        assert live_setup.sales_imported is True

    def test_import_accumulates_tickets_sold(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 50, 'revenue': '7500.00',
            'source_file': str(document_a.id),
        }, format='json')
        live_setup.refresh_from_db()
        assert live_setup.tickets_sold == 150

    def test_import_creates_sales_import_record(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 350, 'revenue': '52500.00',
            'source_file': str(document_a.id),
        }, format='json')
        assert SalesImport.objects.filter(ticketing_setup=live_setup).count() == 1

    def test_import_emits_audit_event(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        event = AuditEvent.objects.filter(event_type='ticketing.sales_imported').first()
        assert event is not None
        assert event.payload['tickets_sold'] == 100


# ── Settle action ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSettleAction:
    def test_settle_when_sales_imported(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 200, 'revenue': '30000.00',
            'source_file': str(document_a.id),
        }, format='json')
        r = client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/settle/', {
            'amount': '28000.00',
        }, format='json')
        assert r.status_code == 200
        assert r.data['settlement_status'] == 'settled'

    def test_settle_records_amount(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 200, 'revenue': '30000.00',
            'source_file': str(document_a.id),
        }, format='json')
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/settle/', {
            'amount': '28000.00',
        }, format='json')
        live_setup.refresh_from_db()
        assert live_setup.settlement_amount == 28000

    def test_settle_without_imports_returns_400(self, client_a, live_setup):
        r = client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/settle/', {
            'amount': '28000.00',
        }, format='json')
        assert r.status_code == 400

    def test_settle_emits_audit_event(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/settle/', {
            'amount': '14000.00',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='ticketing.settled').count() == 1


# ── SalesImport list ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSalesImportList:
    def test_list_sales_imports(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        r = client_a.get('/api/v1/ticketing/sales-imports/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_setup(self, client_a, live_setup, document_a):
        client_a.post(f'/api/v1/ticketing/setups/{live_setup.id}/import-sales/', {
            'tickets_sold': 100, 'revenue': '15000.00',
            'source_file': str(document_a.id),
        }, format='json')
        r = client_a.get(f'/api/v1/ticketing/sales-imports/?ticketing_setup={live_setup.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_sales_imports_read_only(self, client_a):
        r = client_a.post('/api/v1/ticketing/sales-imports/', {}, format='json')
        assert r.status_code == 405
