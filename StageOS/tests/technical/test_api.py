import pytest
from apps.audit.models import AuditEvent
from apps.technical.models import TechnicalRider, CrewRequirement, EquipmentRequirement


@pytest.mark.django_db
class TestTechnicalRiderCRUD:
    def test_list(self, client_a, rider_a):
        r = client_a.get('/api/v1/technical/riders/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/technical/riders/', {
            'operating_context': str(context_a.id),
            'lighting': 'Full rig',
        }, format='json')
        assert r.status_code == 201
        assert TechnicalRider.objects.filter(organisation=org_a).exists()

    def test_create_without_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/technical/riders/', {
            'lighting': 'Full rig',
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, rider_a):
        r = client_a.get(f'/api/v1/technical/riders/{rider_a.id}/')
        assert r.status_code == 200

    def test_partial_update(self, client_a, rider_a):
        r = client_a.patch(
            f'/api/v1/technical/riders/{rider_a.id}/',
            {'lighting': 'Updated lighting notes'}, format='json',
        )
        assert r.status_code == 200
        rider_a.refresh_from_db()
        assert rider_a.lighting == 'Updated lighting notes'

    def test_direct_status_patch_rejected(self, client_a, rider_a):
        r = client_a.patch(
            f'/api/v1/technical/riders/{rider_a.id}/',
            {'status': 'submitted'}, format='json',
        )
        assert r.status_code == 400

    def test_delete(self, client_a, rider_a):
        r = client_a.delete(f'/api/v1/technical/riders/{rider_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, rider_b):
        r = client_a.get(f'/api/v1/technical/riders/{rider_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/technical/riders/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestTechnicalRiderUniqueEnforcement:
    def test_duplicate_context_returns_400(self, client_a, rider_a, context_a):
        r = client_a.post('/api/v1/technical/riders/', {
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, context_b):
        r = client_a.post('/api/v1/technical/riders/', {
            'operating_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestApproveRiderAction:
    def test_approve_sets_status(self, client_a, rider_a):
        r = client_a.post(f'/api/v1/technical/riders/{rider_a.id}/approve/', {}, format='json')
        assert r.status_code == 200
        rider_a.refresh_from_db()
        assert rider_a.status == 'approved'

    def test_approve_sets_approved_by(self, client_a, rider_a, user_a):
        client_a.post(f'/api/v1/technical/riders/{rider_a.id}/approve/', {}, format='json')
        rider_a.refresh_from_db()
        assert rider_a.approved_by == user_a

    def test_approve_sets_approved_at(self, client_a, rider_a):
        client_a.post(f'/api/v1/technical/riders/{rider_a.id}/approve/', {}, format='json')
        rider_a.refresh_from_db()
        assert rider_a.approved_at is not None

    def test_approve_emits_audit(self, client_a, rider_a):
        client_a.post(f'/api/v1/technical/riders/{rider_a.id}/approve/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='rider.approved').exists()

    def test_approve_response_contains_updated_rider(self, client_a, rider_a):
        r = client_a.post(f'/api/v1/technical/riders/{rider_a.id}/approve/', {}, format='json')
        assert r.status_code == 200
        assert r.data['status'] == 'approved'
        assert r.data['approved_at'] is not None

    def test_approve_other_org_rider_returns_404(self, client_a, rider_b):
        r = client_a.post(f'/api/v1/technical/riders/{rider_b.id}/approve/', {}, format='json')
        assert r.status_code == 404


@pytest.mark.django_db
class TestCrewRequirementCRUD:
    def test_list(self, client_a, rider_a):
        CrewRequirement.objects.create(
            organisation=rider_a.organisation, rider=rider_a, role='LD', quantity=1,
        )
        r = client_a.get('/api/v1/technical/crew/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, rider_a):
        r = client_a.post('/api/v1/technical/crew/', {
            'rider': str(rider_a.id),
            'role': 'Sound Engineer',
            'quantity': 2,
        }, format='json')
        assert r.status_code == 201
        assert CrewRequirement.objects.filter(organisation=org_a, role='Sound Engineer').exists()

    def test_cross_org_rider_returns_400(self, client_a, rider_b):
        r = client_a.post('/api/v1/technical/crew/', {
            'rider': str(rider_b.id),
            'role': 'LD',
            'quantity': 1,
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestEquipmentRequirementCRUD:
    def test_create(self, client_a, org_a, rider_a):
        r = client_a.post('/api/v1/technical/equipment/', {
            'rider': str(rider_a.id),
            'item': 'Follow spot',
            'quantity': 2,
            'source': 'in_house',
        }, format='json')
        assert r.status_code == 201
        assert EquipmentRequirement.objects.filter(
            organisation=org_a, item='Follow spot',
        ).exists()

    def test_cross_org_rider_returns_400(self, client_a, rider_b):
        r = client_a.post('/api/v1/technical/equipment/', {
            'rider': str(rider_b.id),
            'item': 'Follow spot',
            'quantity': 1,
            'source': 'in_house',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, org_b, rider_b):
        eq = EquipmentRequirement.objects.create(
            organisation=org_b, rider=rider_b, item='Console', quantity=1, source='hired',
        )
        r = client_a.get(f'/api/v1/technical/equipment/{eq.id}/')
        assert r.status_code == 404
