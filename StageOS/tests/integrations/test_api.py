import pytest
from rest_framework.test import APIClient


# ── IntegrationProvider ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestIntegrationProviderViewSet:
    url = '/api/v1/integrations/providers/'

    def detail_url(self, pk):
        return f'{self.url}{pk}/'

    def test_requires_auth(self):
        r = APIClient().get(self.url)
        assert r.status_code == 401

    def test_list_returns_200(self, client_a):
        r = client_a.get(self.url)
        assert r.status_code == 200

    def test_list_empty(self, client_a):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_list_own_providers(self, client_a, integration_provider_a):
        r = client_a.get(self.url)
        assert r.data['count'] == 1
        assert r.data['results'][0]['name'] == 'Webtickets'

    def test_tenant_isolation_list(self, client_a, integration_provider_b):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_retrieve_own_provider(self, client_a, integration_provider_a):
        r = client_a.get(self.detail_url(integration_provider_a.id))
        assert r.status_code == 200
        assert r.data['name'] == 'Webtickets'
        assert r.data['provider_type'] == 'ticketing'
        assert r.data['is_enabled'] is True

    def test_retrieve_other_org_404(self, client_a, integration_provider_b):
        r = client_a.get(self.detail_url(integration_provider_b.id))
        assert r.status_code == 404

    def test_provider_fields(self, client_a, integration_provider_a):
        r = client_a.get(self.detail_url(integration_provider_a.id))
        for field in ['id', 'name', 'provider_type', 'is_enabled', 'config', 'notes', 'created_at', 'updated_at']:
            assert field in r.data

    def test_create_not_allowed(self, client_a):
        r = client_a.post(self.url, {'name': 'Test', 'provider_type': 'erp'})
        assert r.status_code == 405

    def test_update_not_allowed(self, client_a, integration_provider_a):
        r = client_a.patch(self.detail_url(integration_provider_a.id), {'name': 'New'})
        assert r.status_code == 405

    def test_delete_not_allowed(self, client_a, integration_provider_a):
        r = client_a.delete(self.detail_url(integration_provider_a.id))
        assert r.status_code == 405

    def test_filter_by_provider_type(self, client_a, integration_provider_a, org_a):
        from apps.integrations.models import IntegrationProvider
        IntegrationProvider.objects.create(
            organisation=org_a,
            name='DocuSign',
            provider_type='signature',
            is_enabled=True,
        )
        r = client_a.get(self.url, {'provider_type': 'ticketing'})
        assert r.data['count'] == 1
        assert r.data['results'][0]['name'] == 'Webtickets'

    def test_filter_by_is_enabled(self, client_a, org_a):
        from apps.integrations.models import IntegrationProvider
        IntegrationProvider.objects.create(
            organisation=org_a, name='Enabled', provider_type='erp', is_enabled=True,
        )
        IntegrationProvider.objects.create(
            organisation=org_a, name='Disabled', provider_type='crm', is_enabled=False,
        )
        r = client_a.get(self.url, {'is_enabled': 'true'})
        assert r.data['count'] == 1
        assert r.data['results'][0]['name'] == 'Enabled'


# ── ExternalReference ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestExternalReferenceViewSet:
    url = '/api/v1/integrations/references/'

    def detail_url(self, pk):
        return f'{self.url}{pk}/'

    def test_requires_auth(self):
        r = APIClient().get(self.url)
        assert r.status_code == 401

    def test_list_returns_200(self, client_a):
        r = client_a.get(self.url)
        assert r.status_code == 200

    def test_list_empty(self, client_a):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_list_own_references(self, client_a, external_reference_a):
        r = client_a.get(self.url)
        assert r.data['count'] == 1
        assert r.data['results'][0]['external_id'] == 'EVT-001'

    def test_tenant_isolation_list(self, client_a, external_reference_b):
        r = client_a.get(self.url)
        assert r.data['count'] == 0

    def test_retrieve_own_reference(self, client_a, external_reference_a):
        r = client_a.get(self.detail_url(external_reference_a.id))
        assert r.status_code == 200
        assert r.data['reference_type'] == 'event_id'
        assert r.data['external_id'] == 'EVT-001'

    def test_retrieve_other_org_404(self, client_a, external_reference_b):
        r = client_a.get(self.detail_url(external_reference_b.id))
        assert r.status_code == 404

    def test_reference_fields(self, client_a, external_reference_a):
        r = client_a.get(self.detail_url(external_reference_a.id))
        for field in ['id', 'provider', 'operating_context', 'reference_type', 'external_id', 'metadata', 'created_at']:
            assert field in r.data

    def test_create_not_allowed(self, client_a, integration_provider_a, context_a):
        r = client_a.post(self.url, {
            'provider': str(integration_provider_a.id),
            'operating_context': str(context_a.id),
            'reference_type': 'event_id',
            'external_id': 'X-999',
        })
        assert r.status_code == 405

    def test_filter_by_provider(self, client_a, external_reference_a, integration_provider_a):
        r = client_a.get(self.url, {'provider': str(integration_provider_a.id)})
        assert r.data['count'] == 1

    def test_filter_by_operating_context(self, client_a, external_reference_a, context_a):
        r = client_a.get(self.url, {'operating_context': str(context_a.id)})
        assert r.data['count'] == 1

    def test_filter_by_reference_type(self, client_a, external_reference_a):
        r = client_a.get(self.url, {'reference_type': 'event_id'})
        assert r.data['count'] == 1

    def test_filter_reference_type_no_match(self, client_a, external_reference_a):
        r = client_a.get(self.url, {'reference_type': 'artist_id'})
        assert r.data['count'] == 0
