import pytest
from apps.audit.models import AuditEvent
from apps.tasks.models import Task


@pytest.mark.django_db
class TestTaskListCreate:
    def test_list(self, client_a, task_a):
        r = client_a.get('/api/v1/tasks/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create_minimal(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_a.id),
            'title': 'New Task',
        }, format='json')
        assert r.status_code == 201
        assert Task.objects.filter(title='New Task', organisation=org_a).exists()

    def test_create_without_operating_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/tasks/', {'title': 'Orphan Task'}, format='json')
        assert r.status_code == 400

    def test_create_sets_organisation_automatically(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_a.id),
            'title': 'Auto Org Task',
        }, format='json')
        assert r.status_code == 201
        task = Task.objects.get(title='Auto Org Task')
        assert task.organisation == org_a

    def test_create_emits_audit_event(self, client_a, context_a):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_a.id),
            'title': 'Audited Task',
        }, format='json')
        assert r.status_code == 201
        assert AuditEvent.objects.filter(event_type='task.created').count() == 1

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/tasks/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestTaskRetrieveUpdateDelete:
    def test_retrieve(self, client_a, task_a):
        r = client_a.get(f'/api/v1/tasks/{task_a.id}/')
        assert r.status_code == 200
        assert r.data['title'] == task_a.title

    def test_partial_update(self, client_a, task_a):
        r = client_a.patch(f'/api/v1/tasks/{task_a.id}/', {'title': 'Updated'}, format='json')
        assert r.status_code == 200
        task_a.refresh_from_db()
        assert task_a.title == 'Updated'

    def test_delete(self, client_a, org_a, context_a):
        task = Task.objects.create(organisation=org_a, operating_context=context_a, title='To Delete')
        r = client_a.delete(f'/api/v1/tasks/{task.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, task_b):
        r = client_a.get(f'/api/v1/tasks/{task_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestTaskFiltering:
    def test_filter_by_operating_context(self, client_a, org_a, context_a, site_a, user_a):
        from apps.contexts.models import OperatingContext
        context2 = OperatingContext.objects.create(
            organisation=org_a, title='Context 2', site=site_a, owner=user_a,
        )
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Task in CTX1')
        Task.objects.create(organisation=org_a, operating_context=context2, title='Task in CTX2')
        r = client_a.get(f'/api/v1/tasks/?operating_context={context_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Task in CTX1'

    def test_filter_by_status(self, client_a, org_a, context_a):
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Open', status='open')
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Done', status='done')
        r = client_a.get('/api/v1/tasks/?status=done')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Done'

    def test_filter_by_priority(self, client_a, org_a, context_a):
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Low', priority='low')
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Critical', priority='critical')
        r = client_a.get('/api/v1/tasks/?priority=critical')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['title'] == 'Critical'

    def test_search_by_title(self, client_a, org_a, context_a):
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Lighting Rig Setup')
        Task.objects.create(organisation=org_a, operating_context=context_a, title='Sound Check')
        r = client_a.get('/api/v1/tasks/?search=Lighting')
        assert r.status_code == 200
        assert r.data['count'] == 1


@pytest.mark.django_db
class TestCompleteTaskAction:
    def test_complete_without_evidence_required(self, client_a, task_a):
        r = client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert r.status_code == 200
        task_a.refresh_from_db()
        assert task_a.status == 'done'

    def test_complete_sets_completed_at_and_by(self, client_a, task_a, user_a):
        r = client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert r.status_code == 200
        task_a.refresh_from_db()
        assert task_a.completed_at is not None
        assert task_a.completed_by == user_a

    def test_complete_with_evidence_required_no_evidence_returns_422(self, client_a, org_a, context_a):
        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Evidence Task', evidence_required=True,
        )
        r = client_a.post(f'/api/v1/tasks/{task.id}/complete/', {'has_evidence': False}, format='json')
        assert r.status_code == 422

    def test_complete_with_evidence_required_and_evidence_provided(self, client_a, org_a, context_a, document_a, user_a):
        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Evidence Task', evidence_required=True,
        )
        from apps.documents.models import EvidenceSubmission
        EvidenceSubmission.objects.create(
            organisation=org_a,
            operating_context=context_a,
            task=task,
            document=document_a,
            submitted_by=user_a,
            accepted=True,
        )
        r = client_a.post(f'/api/v1/tasks/{task.id}/complete/', {'has_evidence': True}, format='json')
        assert r.status_code == 200
        task.refresh_from_db()
        assert task.status == 'done'
        assert task.evidence_provided is True

    def test_complete_with_evidence_required_rejects_claim_without_accepted_evidence(self, client_a, org_a, context_a):
        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Evidence Task', evidence_required=True,
        )
        r = client_a.post(f'/api/v1/tasks/{task.id}/complete/', {'has_evidence': True}, format='json')
        assert r.status_code == 422

    def test_complete_sets_evidence_provided(self, client_a, task_a):
        r = client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {'has_evidence': True}, format='json')
        assert r.status_code == 200
        task_a.refresh_from_db()
        assert task_a.evidence_provided is True

    def test_complete_emits_audit_event(self, client_a, task_a):
        client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='task.completed').count() == 1

    def test_complete_other_org_task_returns_404(self, client_a, task_b):
        r = client_a.post(f'/api/v1/tasks/{task_b.id}/complete/', {}, format='json')
        assert r.status_code == 404

    def test_response_contains_full_task(self, client_a, task_a):
        r = client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert r.status_code == 200
        assert r.data['status'] == 'done'
        assert 'completed_at' in r.data


@pytest.mark.django_db
class TestTaskCrossOrgValidation:
    def test_create_with_other_org_context_rejected(self, client_a, context_b):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_b.id),
            'title': 'Cross-org task',
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_department_rejected(self, client_a, context_a, department_b):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_a.id),
            'title': 'Cross-org dept task',
            'department': str(department_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_assigned_to_rejected(self, client_a, context_a, user_b):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_a.id),
            'title': 'Cross-org assigned task',
            'assigned_to': str(user_b.id),
        }, format='json')
        assert r.status_code == 400
