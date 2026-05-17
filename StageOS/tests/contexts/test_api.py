import pytest
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from common.enums import ContextStatus, ContextType, Priority, RiskLevel


@pytest.mark.django_db
class TestContextListCreate:
    def test_list(self, client_a, context_a):
        r = client_a.get('/api/v1/contexts/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create_minimal(self, client_a, org_a, site_a, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'New Production',
            'site': str(site_a.id),
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert OperatingContext.objects.filter(title='New Production', organisation=org_a).exists()

    def test_create_emits_audit_event(self, client_a, site_a, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Audited Show',
            'site': str(site_a.id),
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert AuditEvent.objects.filter(event_type='context.created').count() == 1

    def test_organisation_set_automatically(self, client_a, org_a, site_a, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Auto Org',
            'site': str(site_a.id),
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        ctx = OperatingContext.objects.get(title='Auto Org')
        assert ctx.organisation == org_a

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/contexts/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestContextRetrieveUpdateDelete:
    def test_retrieve(self, client_a, context_a):
        r = client_a.get(f'/api/v1/contexts/{context_a.id}/')
        assert r.status_code == 200
        assert r.data['title'] == context_a.title

    def test_retrieve_includes_nested_site(self, client_a, context_a, site_a):
        r = client_a.get(f'/api/v1/contexts/{context_a.id}/')
        assert r.status_code == 200
        assert r.data['site_detail']['id'] == str(site_a.id)
        assert r.data['site_detail']['name'] == site_a.name

    def test_retrieve_includes_nested_owner(self, client_a, context_a, user_a):
        r = client_a.get(f'/api/v1/contexts/{context_a.id}/')
        assert r.status_code == 200
        assert r.data['owner_detail']['email'] == user_a.email

    def test_partial_update(self, client_a, context_a):
        r = client_a.patch(f'/api/v1/contexts/{context_a.id}/', {
            'title': 'Renamed', 'readiness_score': 50,
        }, format='json')
        assert r.status_code == 200
        context_a.refresh_from_db()
        assert context_a.title == 'Renamed'
        assert context_a.readiness_score == 50

    def test_delete(self, client_a, org_a, site_a, user_a):
        ctx = OperatingContext.objects.create(
            organisation=org_a, title='To Delete', site=site_a, owner=user_a,
        )
        r = client_a.delete(f'/api/v1/contexts/{ctx.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, context_b):
        r = client_a.get(f'/api/v1/contexts/{context_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestContextFiltering:
    def test_filter_by_context_type(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Festival', context_type='festival',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Production', context_type='production',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?context_type=festival')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Festival'

    def test_filter_by_status(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Draft One', status='draft',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Submitted One', status='submitted',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?status=submitted')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Submitted One'

    def test_filter_by_priority(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Low Priority', priority='low',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Critical Priority', priority='critical',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?priority=critical')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Critical Priority'

    def test_filter_by_risk_level(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='High Risk', risk_level='high',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Low Risk', risk_level='low',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?risk_level=high')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'High Risk'

    def test_filter_by_site(self, client_a, org_a, site_a, user_a):
        from apps.structure.models import Site
        site2 = Site.objects.create(
            organisation=org_a, name='Site 2', code='S2',
            city='Durban', province='KZN', country='South Africa',
        )
        OperatingContext.objects.create(
            organisation=org_a, title='At Site A', site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='At Site 2', site=site2, owner=user_a,
        )
        r = client_a.get(f'/api/v1/contexts/?site={site_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'At Site A'

    def test_search_by_title(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Hamlet 2025', site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Macbeth Gala', site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?search=Hamlet')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Hamlet 2025'

    def test_search_by_synopsis(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Show', synopsis='A story about revenge',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Other', synopsis='A love story',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?search=revenge')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_order_by_opening_date_ascending(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Late', opening_date='2025-12-01',
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='Early', opening_date='2025-01-01',
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?ordering=opening_date')
        assert r.status_code == 200
        titles = [c['title'] for c in r.data['results']]
        assert titles.index('Early') < titles.index('Late')

    def test_order_by_readiness_score_descending(self, client_a, org_a, site_a, user_a):
        OperatingContext.objects.create(
            organisation=org_a, title='Low', readiness_score=10,
            site=site_a, owner=user_a,
        )
        OperatingContext.objects.create(
            organisation=org_a, title='High', readiness_score=90,
            site=site_a, owner=user_a,
        )
        r = client_a.get('/api/v1/contexts/?ordering=-readiness_score')
        assert r.status_code == 200
        assert r.data['results'][0]['title'] == 'High'


@pytest.mark.django_db
class TestChangeStatusEndpoint:
    def test_valid_transition_returns_200(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'SUBMITTED', 'comment': 'Ready for review'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'submitted'

    def test_response_contains_full_context(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'submitted'},
            format='json',
        )
        assert r.status_code == 200
        assert 'title' in r.data
        assert 'site_detail' in r.data

    def test_accepts_uppercase_status(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'SUBMITTED'},
            format='json',
        )
        assert r.status_code == 200

    def test_invalid_transition_returns_400(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'completed'},
            format='json',
        )
        assert r.status_code == 400
        assert 'detail' in r.data

    def test_invalid_transition_message_helpful(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'closed'},
            format='json',
        )
        assert r.status_code == 400
        assert 'submitted' in r.data['detail'] or 'cancelled' in r.data['detail']

    def test_cancelled_terminal_returns_400(self, client_a, context_a):
        context_a.status = ContextStatus.CANCELLED
        context_a.save()
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'draft'},
            format='json',
        )
        assert r.status_code == 400
        assert 'terminal' in r.data['detail']

    def test_rejected_to_draft_resubmission(self, client_a, context_a):
        context_a.status = ContextStatus.REJECTED
        context_a.save()
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'draft'},
            format='json',
        )
        assert r.status_code == 200
        context_a.refresh_from_db()
        assert context_a.status == ContextStatus.DRAFT

    def test_status_change_emits_audit_event(self, client_a, context_a):
        client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'submitted', 'comment': 'All set'},
            format='json',
        )
        event = AuditEvent.objects.get(event_type='context.status_changed')
        assert event.payload['old_status'] == 'draft'
        assert event.payload['new_status'] == 'submitted'
        assert event.payload['comment'] == 'All set'

    def test_cannot_change_status_of_other_org_context(self, client_a, context_b):
        r = client_a.post(
            f'/api/v1/contexts/{context_b.id}/change-status/',
            {'status': 'submitted'},
            format='json',
        )
        assert r.status_code == 404

    def test_invalid_status_string_returns_400(self, client_a, context_a):
        r = client_a.post(
            f'/api/v1/contexts/{context_a.id}/change-status/',
            {'status': 'nonsense'},
            format='json',
        )
        assert r.status_code == 400


@pytest.mark.django_db
class TestContextCrossOrgValidation:
    def test_create_with_other_org_site_rejected(self, client_a, site_b, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_b.id), 'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_owner_rejected(self, client_a, site_a, user_b):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_a.id), 'owner': str(user_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_venue_rejected(self, client_a, site_a, user_a, venue_b):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_a.id),
            'owner': str(user_a.id), 'venue': str(venue_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_parent_context_rejected(self, client_a, site_a, user_a, context_b):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Sub-event', 'site': str(site_a.id),
            'owner': str(user_a.id), 'parent_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_parent_context_self_fk_same_org_allowed(self, client_a, org_a, site_a, user_a, context_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Sub-event', 'site': str(site_a.id),
            'owner': str(user_a.id), 'parent_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 201
