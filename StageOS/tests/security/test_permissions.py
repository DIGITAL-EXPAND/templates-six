import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def read_only_client(org_a):
    user = User.objects.create_user(
        email='readonly@example.com',
        password='testpass123',
        organisation=org_a,
        user_type='read_only',
    )
    return authenticated_client(user)


@pytest.mark.django_db
class TestPermissionFoundation:
    def test_read_only_user_cannot_mutate_operational_data(self, read_only_client, context_a):
        r = read_only_client.patch(
            f'/api/v1/contexts/{context_a.id}/',
            {'title': 'Read only edit'},
            format='json',
        )
        assert r.status_code == 403

    def test_read_only_user_gets_403_for_privileged_action(self, read_only_client, task_a):
        r = read_only_client.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert r.status_code == 403

    def test_audit_export_restricted_to_authorised_roles(self, org_a):
        user = User.objects.create_user(
            email='staff-audit@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        r = authenticated_client(user).get('/api/v1/reports/audit-export/')
        assert r.status_code == 403

    def test_supplier_external_only_sees_own_supplier_records(self, org_a, supplier_a, supplier_b):
        supplier_a.contact_email = 'supplier-own@example.com'
        supplier_a.save(update_fields=['contact_email'])
        user = User.objects.create_user(
            email='supplier-own@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='supplier_external',
        )
        r = authenticated_client(user).get('/api/v1/suppliers/')
        assert r.status_code == 200
        ids = [row['id'] for row in r.data['results']]
        assert str(supplier_a.id) in ids
        assert str(supplier_b.id) not in ids

    def test_artist_external_only_sees_own_artist_records(self, org_a, artist_a, artist_b):
        artist_a.contact_email = 'artist-own@example.com'
        artist_a.save(update_fields=['contact_email'])
        user = User.objects.create_user(
            email='artist-own@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='artist_external',
        )
        r = authenticated_client(user).get('/api/v1/artists/')
        assert r.status_code == 200
        ids = [row['id'] for row in r.data['results']]
        assert str(artist_a.id) in ids
        assert str(artist_b.id) not in ids

    def test_client_external_cannot_see_internal_context_records(self, org_a):
        user = User.objects.create_user(
            email='client-ext@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='client_external',
        )
        r = authenticated_client(user).get('/api/v1/contexts/')
        assert r.status_code == 403
