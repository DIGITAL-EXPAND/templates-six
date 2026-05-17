import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def staff_client(org_a):
    user = User.objects.create_user(
        email='staff-security@example.com',
        password='testpass123',
        organisation=org_a,
        user_type='staff',
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(org_a):
    user = User.objects.create_user(
        email='admin-security@example.com',
        password='testpass123',
        organisation=org_a,
        user_type='internal_admin',
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestUserPrivilegeControls:
    def test_normal_user_cannot_create_admin_user(self, staff_client):
        r = staff_client.post('/api/v1/users/', {
            'email': 'new-admin@example.com',
            'password': 'testpass123',
            'user_type': 'internal_admin',
        }, format='json')
        assert r.status_code == 403

    def test_normal_user_cannot_set_user_type_directly(self, staff_client):
        r = staff_client.post('/api/v1/users/', {
            'email': 'new-staff@example.com',
            'password': 'testpass123',
            'user_type': 'staff',
        }, format='json')
        assert r.status_code == 403

    def test_user_cannot_choose_another_organisation_on_create(self, admin_client, org_b):
        r = admin_client.post('/api/v1/users/', {
            'email': 'scoped-user@example.com',
            'password': 'testpass123',
            'user_type': 'staff',
            'organisation': str(org_b.id),
        }, format='json')
        assert r.status_code == 201
        user = User.objects.get(email='scoped-user@example.com')
        assert user.organisation_id != org_b.id

    def test_external_user_cannot_list_internal_users(self, org_a):
        external = User.objects.create_user(
            email='supplier-ext@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='supplier_external',
        )
        client = APIClient()
        client.force_authenticate(user=external)
        r = client.get('/api/v1/users/')
        assert r.status_code == 200
        assert r.data['count'] == 0

    def test_authorised_admin_can_create_allowed_user_type(self, admin_client, org_a):
        r = admin_client.post('/api/v1/users/', {
            'email': 'new-manager@example.com',
            'password': 'testpass123',
            'user_type': 'manager',
        }, format='json')
        assert r.status_code == 201
        assert User.objects.get(email='new-manager@example.com').organisation == org_a
