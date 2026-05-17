import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from apps.audit.models import AuditEvent
from apps.documents.models import Document, EvidenceSubmission


@pytest.mark.django_db
class TestDocumentListCreate:
    def test_list(self, client_a, document_a):
        r = client_a.get('/api/v1/documents/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/documents/', {
            'operating_context': str(context_a.id),
            'title': 'My Plan',
            'document_type': 'plan',
            'file_name': 'plan.pdf',
            'file_size': 524288,
        }, format='json')
        assert r.status_code == 201
        assert Document.objects.filter(title='My Plan', organisation=org_a).exists()

    def test_create_without_operating_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/documents/', {
            'title': 'Orphan Doc',
            'document_type': 'brief',
            'file_name': 'file.pdf',
            'file_size': 1024,
        }, format='json')
        assert r.status_code == 400

    def test_create_sets_uploaded_by_automatically(self, client_a, context_a, user_a):
        r = client_a.post('/api/v1/documents/', {
            'operating_context': str(context_a.id),
            'title': 'Auto Uploader',
            'document_type': 'report',
            'file_name': 'report.pdf',
            'file_size': 204800,
        }, format='json')
        assert r.status_code == 201
        doc = Document.objects.get(title='Auto Uploader')
        assert doc.uploaded_by == user_a

    def test_create_emits_audit_event(self, client_a, context_a):
        r = client_a.post('/api/v1/documents/', {
            'operating_context': str(context_a.id),
            'title': 'Audited Doc',
            'document_type': 'brief',
            'file_name': 'brief.pdf',
            'file_size': 65536,
        }, format='json')
        assert r.status_code == 201
        assert AuditEvent.objects.filter(event_type='document.uploaded').count() == 1

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/documents/')
        assert r.status_code == 401

    def test_upload_actual_file(self, client_a, org_a, context_a):
        upload = SimpleUploadedFile(
            'brief.pdf',
            b'%PDF-1.4 test content',
            content_type='application/pdf',
        )
        r = client_a.post('/api/v1/documents/upload/', {
            'operating_context': str(context_a.id),
            'title': 'Uploaded Brief',
            'document_type': 'brief',
            'file': upload,
        }, format='multipart')
        assert r.status_code == 201
        doc = Document.objects.get(title='Uploaded Brief', organisation=org_a)
        assert doc.file_name == 'brief.pdf'
        assert doc.mime_type == 'application/pdf'
        assert doc.storage_ref
        assert doc.file
        assert AuditEvent.objects.filter(event_type='document.file_uploaded').exists()

    def test_unauthenticated_upload_rejected(self, context_a):
        from rest_framework.test import APIClient
        upload = SimpleUploadedFile('brief.pdf', b'test', content_type='application/pdf')
        r = APIClient().post('/api/v1/documents/upload/', {
            'operating_context': str(context_a.id),
            'title': 'No Auth',
            'document_type': 'brief',
            'file': upload,
        }, format='multipart')
        assert r.status_code == 401

    def test_read_only_upload_rejected(self, org_a, context_a):
        from rest_framework.test import APIClient
        from apps.accounts.models import User
        user = User.objects.create_user(
            email='readonly-docs@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='read_only',
        )
        client = APIClient()
        client.force_authenticate(user=user)
        upload = SimpleUploadedFile('brief.pdf', b'test', content_type='application/pdf')
        r = client.post('/api/v1/documents/upload/', {
            'operating_context': str(context_a.id),
            'title': 'Read only upload',
            'document_type': 'brief',
            'file': upload,
        }, format='multipart')
        assert r.status_code == 403

    def test_upload_blocks_disallowed_mime_type(self, client_a, context_a):
        upload = SimpleUploadedFile(
            'script.exe',
            b'bad',
            content_type='application/x-msdownload',
        )
        r = client_a.post('/api/v1/documents/upload/', {
            'operating_context': str(context_a.id),
            'title': 'Bad Upload',
            'document_type': 'other',
            'file': upload,
        }, format='multipart')
        assert r.status_code == 400
        assert 'file' in r.data

    @override_settings(STAGEOS_MAX_UPLOAD_BYTES=4)
    def test_upload_blocks_oversized_file(self, client_a, context_a):
        upload = SimpleUploadedFile(
            'large.pdf',
            b'12345',
            content_type='application/pdf',
        )
        r = client_a.post('/api/v1/documents/upload/', {
            'operating_context': str(context_a.id),
            'title': 'Large Upload',
            'document_type': 'brief',
            'file': upload,
        }, format='multipart')
        assert r.status_code == 400
        assert 'file' in r.data

    def test_download_actual_file(self, client_a, org_a, context_a, user_a):
        doc = Document.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Stored Doc',
            document_type='brief',
            file_name='stored.pdf',
            file_size=4,
            mime_type='application/pdf',
            uploaded_by=user_a,
        )
        doc.file.save('stored.pdf', SimpleUploadedFile('stored.pdf', b'test', content_type='application/pdf'))
        doc.storage_ref = doc.file.name
        doc.save(update_fields=['storage_ref'])
        r = client_a.get(f'/api/v1/documents/{doc.id}/download/')
        assert r.status_code == 200
        assert r['Content-Type'] == 'application/pdf'
        assert AuditEvent.objects.filter(event_type='document.downloaded').exists()

    def test_unauthenticated_download_rejected(self, document_a):
        from rest_framework.test import APIClient
        r = APIClient().get(f'/api/v1/documents/{document_a.id}/download/')
        assert r.status_code == 401

    def test_wrong_tenant_download_rejected(self, client_a, document_b):
        r = client_a.get(f'/api/v1/documents/{document_b.id}/download/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestDocumentRetrieveUpdateDelete:
    def test_retrieve(self, client_a, document_a):
        r = client_a.get(f'/api/v1/documents/{document_a.id}/')
        assert r.status_code == 200
        assert r.data['title'] == document_a.title

    def test_partial_update(self, client_a, document_a):
        r = client_a.patch(f'/api/v1/documents/{document_a.id}/', {'title': 'Updated title'}, format='json')
        assert r.status_code == 200
        document_a.refresh_from_db()
        assert document_a.title == 'Updated title'

    def test_direct_lock_patch_rejected(self, client_a, document_a):
        r = client_a.patch(f'/api/v1/documents/{document_a.id}/', {'is_locked': True}, format='json')
        assert r.status_code == 400

    def test_delete(self, client_a, org_a, context_a, user_a):
        doc = Document.objects.create(
            organisation=org_a, operating_context=context_a,
            title='To Delete', document_type='other',
            file_name='del.pdf', file_size=1024, uploaded_by=user_a,
        )
        r = client_a.delete(f'/api/v1/documents/{doc.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, document_b):
        r = client_a.get(f'/api/v1/documents/{document_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestDocumentFiltering:
    def test_filter_by_document_type(self, client_a, org_a, context_a, user_a):
        Document.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Brief', document_type='brief',
            file_name='b.pdf', file_size=1024, uploaded_by=user_a,
        )
        Document.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Contract', document_type='contract',
            file_name='c.pdf', file_size=2048, uploaded_by=user_a,
        )
        r = client_a.get('/api/v1/documents/?document_type=contract')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Contract'

    def test_filter_by_is_locked(self, client_a, org_a, context_a, user_a):
        Document.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Locked', document_type='brief',
            file_name='l.pdf', file_size=1024, uploaded_by=user_a, is_locked=True,
        )
        Document.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Unlocked', document_type='brief',
            file_name='u.pdf', file_size=1024, uploaded_by=user_a, is_locked=False,
        )
        r = client_a.get('/api/v1/documents/?is_locked=true')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Locked'


@pytest.mark.django_db
class TestDocumentCrossOrgValidation:
    def test_create_with_other_org_context_rejected(self, client_a, context_b):
        r = client_a.post('/api/v1/documents/', {
            'operating_context': str(context_b.id),
            'title': 'Cross-org',
            'document_type': 'brief',
            'file_name': 'x.pdf',
            'file_size': 1024,
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestEvidenceSubmissionListCreate:
    def test_list(self, client_a, org_a, context_a, task_a, document_a, user_a):
        EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        r = client_a.get('/api/v1/evidence/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a, task_a, document_a):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'task': str(task_a.id),
            'document': str(document_a.id),
            'submission_note': 'Here is the evidence',
        }, format='json')
        assert r.status_code == 201
        assert EvidenceSubmission.objects.filter(organisation=org_a).count() == 1

    def test_create_sets_submitted_by(self, client_a, context_a, task_a, document_a, user_a):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'task': str(task_a.id),
            'document': str(document_a.id),
        }, format='json')
        assert r.status_code == 201
        sub = EvidenceSubmission.objects.first()
        assert sub.submitted_by == user_a

    def test_create_links_document_to_task(self, client_a, context_a, task_a, document_a):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'task': str(task_a.id),
            'document': str(document_a.id),
        }, format='json')
        assert r.status_code == 201
        sub = EvidenceSubmission.objects.first()
        assert sub.task == task_a
        assert sub.document == document_a

    def test_create_without_task_is_allowed(self, client_a, context_a, document_a):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'document': str(document_a.id),
        }, format='json')
        assert r.status_code == 201

    def test_cannot_reach_other_org(self, client_a, org_b, context_b, task_b, document_b, user_b):
        EvidenceSubmission.objects.create(
            organisation=org_b, operating_context=context_b,
            task=task_b, document=document_b, submitted_by=user_b,
        )
        r = client_a.get('/api/v1/evidence/')
        assert r.status_code == 200
        assert r.data['count'] == 0


@pytest.mark.django_db
class TestAcceptEvidenceAction:
    def test_accept_sets_accepted(self, client_a, org_a, context_a, task_a, document_a, user_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        r = client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        assert r.status_code == 200
        sub.refresh_from_db()
        assert sub.accepted is True

    def test_accept_sets_accepted_by_and_at(self, client_a, org_a, context_a, task_a, document_a, user_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        r = client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        assert r.status_code == 200
        sub.refresh_from_db()
        assert sub.accepted_by == user_a
        assert sub.accepted_at is not None

    def test_accept_sets_task_evidence_provided_when_required(self, client_a, org_a, context_a, document_a, user_a):
        from apps.tasks.models import Task
        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Evidence Required Task', evidence_required=True,
        )
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task, document=document_a, submitted_by=user_a,
        )
        client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        task.refresh_from_db()
        assert task.evidence_provided is True

    def test_accept_does_not_set_evidence_provided_when_not_required(self, client_a, org_a, context_a, document_a, user_a, task_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        task_a.refresh_from_db()
        assert task_a.evidence_provided is False

    def test_accept_emits_audit_event(self, client_a, org_a, context_a, task_a, document_a, user_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        assert AuditEvent.objects.filter(event_type='evidence.accepted').count() == 1

    def test_accept_other_org_evidence_returns_404(self, client_a, org_b, context_b, task_b, document_b, user_b):
        sub = EvidenceSubmission.objects.create(
            organisation=org_b, operating_context=context_b,
            task=task_b, document=document_b, submitted_by=user_b,
        )
        r = client_a.post(f'/api/v1/evidence/{sub.id}/accept/')
        assert r.status_code == 404

    def test_reject_requires_reason(self, client_a, org_a, context_a, task_a, document_a, user_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        r = client_a.post(f'/api/v1/evidence/{sub.id}/reject/', {'reason': ''}, format='json')
        assert r.status_code == 400
        assert 'reason' in r.data

    def test_reject_sets_rejection_fields_and_audit(self, client_a, org_a, context_a, task_a, document_a, user_a):
        sub = EvidenceSubmission.objects.create(
            organisation=org_a, operating_context=context_a,
            task=task_a, document=document_a, submitted_by=user_a,
        )
        r = client_a.post(f'/api/v1/evidence/{sub.id}/reject/', {
            'reason': 'Document is illegible.',
        }, format='json')
        assert r.status_code == 200
        sub.refresh_from_db()
        assert sub.rejected is True
        assert sub.rejected_by == user_a
        assert sub.rejection_reason == 'Document is illegible.'
        assert AuditEvent.objects.filter(event_type='evidence.rejected').exists()


@pytest.mark.django_db
class TestEvidenceCrossOrgValidation:
    def test_create_with_other_org_context_rejected(self, client_a, context_b, document_a):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_b.id),
            'document': str(document_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_document_rejected(self, client_a, context_a, document_b):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'document': str(document_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_task_rejected(self, client_a, context_a, document_a, task_b):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'document': str(document_a.id),
            'task': str(task_b.id),
        }, format='json')
        assert r.status_code == 400
