import pytest
from apps.audit.models import AuditEvent
from apps.artists.models import Artist, ArtistDocument, ArtistEngagement


# ── Artist CRUD ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtistCRUD:
    def test_list(self, client_a, artist_a):
        r = client_a.get('/api/v1/artists/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a):
        r = client_a.post('/api/v1/artists/', {
            'legal_name': 'New Artist',
            'discipline': 'Music',
        }, format='json')
        assert r.status_code == 201
        assert Artist.objects.filter(organisation=org_a, legal_name='New Artist').exists()

    def test_retrieve(self, client_a, artist_a):
        r = client_a.get(f'/api/v1/artists/{artist_a.id}/')
        assert r.status_code == 200
        assert r.data['legal_name'] == 'Alice Performer'

    def test_partial_update(self, client_a, artist_a):
        r = client_a.patch(f'/api/v1/artists/{artist_a.id}/', {'notes': 'Reliable performer'}, format='json')
        assert r.status_code == 200
        artist_a.refresh_from_db()
        assert artist_a.notes == 'Reliable performer'

    def test_delete(self, client_a, artist_a):
        r = client_a.delete(f'/api/v1/artists/{artist_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, artist_b):
        r = client_a.get(f'/api/v1/artists/{artist_b.id}/')
        assert r.status_code == 404

    def test_filter_by_status(self, client_a, org_a):
        Artist.objects.create(organisation=org_a, legal_name='Ready Artist', discipline='Dance', status='contract_ready')
        Artist.objects.create(organisation=org_a, legal_name='Incomplete Artist', discipline='Dance', status='documents_incomplete')
        r = client_a.get('/api/v1/artists/?status=contract_ready')
        assert r.data['count'] == 1

    def test_search_by_legal_name(self, client_a, org_a):
        Artist.objects.create(organisation=org_a, legal_name='Unique Musician Person', discipline='Music')
        Artist.objects.create(organisation=org_a, legal_name='Other Performer', discipline='Theatre')
        r = client_a.get('/api/v1/artists/?search=Unique+Musician')
        assert r.data['count'] == 1

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/artists/')
        assert r.status_code == 401


# ── ArtistDocument CRUD ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtistDocumentCRUD:
    def test_create(self, client_a, org_a, artist_a):
        r = client_a.post('/api/v1/artists/documents/', {
            'artist': str(artist_a.id),
            'document_type': 'id_copy',
            'file_name': 'id.pdf',
        }, format='json')
        assert r.status_code == 201
        assert ArtistDocument.objects.filter(
            organisation=org_a, artist=artist_a, document_type='id_copy',
        ).exists()

    def test_list_filterable_by_artist(self, client_a, org_a, artist_a):
        ArtistDocument.objects.create(
            organisation=org_a, artist=artist_a, document_type='id_copy',
        )
        r = client_a.get(f'/api/v1/artists/documents/?artist={artist_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_document_type(self, client_a, org_a, artist_a):
        ArtistDocument.objects.create(organisation=org_a, artist=artist_a, document_type='id_copy')
        ArtistDocument.objects.create(organisation=org_a, artist=artist_a, document_type='contract')
        r = client_a.get('/api/v1/artists/documents/?document_type=id_copy')
        assert r.data['count'] == 1

    def test_cross_org_artist_returns_400(self, client_a, artist_b):
        r = client_a.post('/api/v1/artists/documents/', {
            'artist': str(artist_b.id),
            'document_type': 'id_copy',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org_doc(self, client_a, org_b, artist_b):
        doc = ArtistDocument.objects.create(
            organisation=org_b, artist=artist_b, document_type='id_copy',
        )
        r = client_a.get(f'/api/v1/artists/documents/{doc.id}/')
        assert r.status_code == 404


# ── ArtistEngagement CRUD ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtistEngagementCRUD:
    def test_create(self, client_a, org_a, artist_a, context_a):
        r = client_a.post('/api/v1/artists/engagements/', {
            'artist': str(artist_a.id),
            'operating_context': str(context_a.id),
            'role': 'Lead Actor',
        }, format='json')
        assert r.status_code == 201
        assert ArtistEngagement.objects.filter(organisation=org_a, artist=artist_a).exists()

    def test_list(self, client_a, artist_engagement_a):
        r = client_a.get('/api/v1/artists/engagements/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_duplicate_artist_context_returns_400(self, client_a, artist_engagement_a, artist_a, context_a):
        r = client_a.post('/api/v1/artists/engagements/', {
            'artist': str(artist_a.id),
            'operating_context': str(context_a.id),
            'role': 'Supporting Role',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_artist_returns_400(self, client_a, artist_b, context_a):
        r = client_a.post('/api/v1/artists/engagements/', {
            'artist': str(artist_b.id),
            'operating_context': str(context_a.id),
            'role': 'Cross-org artist',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, artist_a, context_b):
        r = client_a.post('/api/v1/artists/engagements/', {
            'artist': str(artist_a.id),
            'operating_context': str(context_b.id),
            'role': 'Cross-org context',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, artist_engagement_b):
        r = client_a.get(f'/api/v1/artists/engagements/{artist_engagement_b.id}/')
        assert r.status_code == 404


# ── confirm_engagement action ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestConfirmEngagementAction:
    def test_confirm_sets_status(self, client_a, artist_engagement_a):
        r = client_a.post(
            f'/api/v1/artists/engagements/{artist_engagement_a.id}/confirm/',
            {}, format='json',
        )
        assert r.status_code == 200
        artist_engagement_a.refresh_from_db()
        assert artist_engagement_a.status == 'confirmed'

    def test_confirm_emits_audit(self, client_a, artist_engagement_a):
        client_a.post(
            f'/api/v1/artists/engagements/{artist_engagement_a.id}/confirm/',
            {}, format='json',
        )
        assert AuditEvent.objects.filter(event_type='ARTIST_ENGAGEMENT_CONFIRMED').exists()

    def test_confirm_response_contains_updated_status(self, client_a, artist_engagement_a):
        r = client_a.post(
            f'/api/v1/artists/engagements/{artist_engagement_a.id}/confirm/',
            {}, format='json',
        )
        assert r.data['status'] == 'confirmed'

    def test_confirm_other_org_returns_404(self, client_a, artist_engagement_b):
        r = client_a.post(
            f'/api/v1/artists/engagements/{artist_engagement_b.id}/confirm/',
            {}, format='json',
        )
        assert r.status_code == 404


# ── upload_artist_document service ───────────────────────────────────────────

@pytest.mark.django_db
class TestUploadArtistDocument:
    def test_uploading_last_required_doc_sets_contract_ready(self, org_a, artist_a, user_a):
        from apps.artists.services import upload_artist_document
        upload_artist_document(artist_a, user_a, 'id_copy', 'id.pdf')
        upload_artist_document(artist_a, user_a, 'bank_confirmation', 'bank.pdf')
        artist_a.refresh_from_db()
        assert artist_a.status == 'contract_ready'

    def test_uploading_first_required_doc_does_not_change_status(self, org_a, artist_a, user_a):
        from apps.artists.services import upload_artist_document
        upload_artist_document(artist_a, user_a, 'id_copy', 'id.pdf')
        artist_a.refresh_from_db()
        assert artist_a.status == 'documents_incomplete'

    def test_upload_emits_audit(self, org_a, artist_a, user_a):
        from apps.artists.services import upload_artist_document
        upload_artist_document(artist_a, user_a, 'id_copy', 'id.pdf')
        assert AuditEvent.objects.filter(event_type='ARTIST_DOCUMENT_UPLOADED').exists()

    def test_upload_creates_or_updates_existing(self, org_a, artist_a, user_a):
        from apps.artists.services import upload_artist_document
        upload_artist_document(artist_a, user_a, 'id_copy', 'v1.pdf')
        upload_artist_document(artist_a, user_a, 'id_copy', 'v2.pdf')
        assert ArtistDocument.objects.filter(
            artist=artist_a, document_type='id_copy',
        ).count() == 1
        doc = ArtistDocument.objects.get(artist=artist_a, document_type='id_copy')
        assert doc.file_name == 'v2.pdf'
