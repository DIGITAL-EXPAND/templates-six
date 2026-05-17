import datetime
import pytest
from apps.marketing.models import Campaign, CampaignDeliverable


@pytest.mark.django_db
class TestCampaignCRUD:
    def test_list(self, client_a, campaign_a):
        r = client_a.get('/api/v1/marketing/campaigns/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a, user_a):
        r = client_a.post('/api/v1/marketing/campaigns/', {
            'operating_context': str(context_a.id),
            'campaign_level': 'basic',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert Campaign.objects.filter(organisation=org_a).exists()

    def test_create_without_context_returns_400(self, client_a, user_a):
        r = client_a.post('/api/v1/marketing/campaigns/', {
            'campaign_level': 'basic',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, campaign_a):
        r = client_a.get(f'/api/v1/marketing/campaigns/{campaign_a.id}/')
        assert r.status_code == 200
        assert r.data['campaign_level'] == 'standard'

    def test_partial_update(self, client_a, campaign_a):
        r = client_a.patch(
            f'/api/v1/marketing/campaigns/{campaign_a.id}/',
            {'notes': 'Updated plan'}, format='json',
        )
        assert r.status_code == 200
        campaign_a.refresh_from_db()
        assert campaign_a.notes == 'Updated plan'

    def test_direct_status_patch_rejected(self, client_a, campaign_a):
        r = client_a.patch(
            f'/api/v1/marketing/campaigns/{campaign_a.id}/',
            {'status': 'active'}, format='json',
        )
        assert r.status_code == 400

    def test_launch_action_sets_status(self, client_a, campaign_a):
        r = client_a.post(f'/api/v1/marketing/campaigns/{campaign_a.id}/launch/')
        assert r.status_code == 200
        campaign_a.refresh_from_db()
        assert campaign_a.status == 'active'

    def test_delete(self, client_a, campaign_a):
        r = client_a.delete(f'/api/v1/marketing/campaigns/{campaign_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, campaign_b):
        r = client_a.get(f'/api/v1/marketing/campaigns/{campaign_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/marketing/campaigns/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestCampaignUniqueEnforcement:
    def test_duplicate_context_returns_400(self, client_a, campaign_a, context_a, user_a):
        r = client_a.post('/api/v1/marketing/campaigns/', {
            'operating_context': str(context_a.id),
            'campaign_level': 'full',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, context_b, user_a):
        r = client_a.post('/api/v1/marketing/campaigns/', {
            'operating_context': str(context_b.id),
            'campaign_level': 'basic',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_owner_returns_400(self, client_a, context_a, user_b):
        r = client_a.post('/api/v1/marketing/campaigns/', {
            'operating_context': str(context_a.id),
            'campaign_level': 'basic',
            'owner': str(user_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestCampaignDeliverableCRUD:
    def test_list(self, client_a, deliverable_a):
        r = client_a.get('/api/v1/marketing/deliverables/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, campaign_a):
        r = client_a.post('/api/v1/marketing/deliverables/', {
            'campaign': str(campaign_a.id),
            'deliverable_type': 'press_release',
            'title': 'Opening Night Press Release',
            'owner_name': 'PR Manager',
        }, format='json')
        assert r.status_code == 201
        assert CampaignDeliverable.objects.filter(
            organisation=org_a, title='Opening Night Press Release',
        ).exists()

    def test_create_without_campaign_returns_400(self, client_a):
        r = client_a.post('/api/v1/marketing/deliverables/', {
            'deliverable_type': 'newsletter',
            'title': 'Orphan Deliverable',
            'owner_name': 'Nobody',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_campaign_returns_400(self, client_a, campaign_b):
        r = client_a.post('/api/v1/marketing/deliverables/', {
            'campaign': str(campaign_b.id),
            'deliverable_type': 'newsletter',
            'title': 'Cross-org Deliverable',
            'owner_name': 'Nobody',
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, deliverable_a):
        r = client_a.get(f'/api/v1/marketing/deliverables/{deliverable_a.id}/')
        assert r.status_code == 200

    def test_partial_update(self, client_a, deliverable_a):
        r = client_a.patch(
            f'/api/v1/marketing/deliverables/{deliverable_a.id}/',
            {'owner_name': 'Updated owner'}, format='json',
        )
        assert r.status_code == 200
        deliverable_a.refresh_from_db()
        assert deliverable_a.owner_name == 'Updated owner'

    def test_direct_status_patch_rejected(self, client_a, deliverable_a):
        r = client_a.patch(
            f'/api/v1/marketing/deliverables/{deliverable_a.id}/',
            {'status': 'in_progress'}, format='json',
        )
        assert r.status_code == 400

    def test_complete_without_evidence_returns_400(self, client_a, deliverable_a):
        r = client_a.post(f'/api/v1/marketing/deliverables/{deliverable_a.id}/complete/')
        assert r.status_code == 400

    def test_complete_action_sets_status(self, client_a, deliverable_a, document_a):
        r = client_a.post(
            f'/api/v1/marketing/deliverables/{deliverable_a.id}/complete/',
            {'evidence_document': str(document_a.id)}, format='json',
        )
        assert r.status_code == 200
        deliverable_a.refresh_from_db()
        assert deliverable_a.status == 'complete'
        assert deliverable_a.evidence_document == document_a

    def test_cannot_reach_other_org(self, client_a, deliverable_b):
        r = client_a.get(f'/api/v1/marketing/deliverables/{deliverable_b.id}/')
        assert r.status_code == 404

    def test_list_excludes_other_org(self, client_a, deliverable_a, deliverable_b):
        r = client_a.get('/api/v1/marketing/deliverables/')
        assert r.status_code == 200
        assert r.data['count'] == 1
        ids = [d['id'] for d in r.data['results']]
        assert str(deliverable_a.id) in ids
        assert str(deliverable_b.id) not in ids
