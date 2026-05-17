import pytest
from django.utils import timezone
from apps.audit.models import AuditEvent
from apps.tasks.models import Task
from apps.tasks.services import create_task, complete_task, EvidenceRequired


@pytest.mark.django_db
class TestCreateTask:
    def test_creates_task(self, org_a, context_a, user_a):
        task = create_task(context_a, user_a, {'title': 'Service Task'})
        assert Task.objects.filter(id=task.id).exists()

    def test_task_linked_to_context(self, org_a, context_a, user_a):
        task = create_task(context_a, user_a, {'title': 'Linked Task'})
        assert task.operating_context == context_a

    def test_task_org_matches_context(self, org_a, context_a, user_a):
        task = create_task(context_a, user_a, {'title': 'Org Task'})
        assert task.organisation == org_a

    def test_emits_audit_event(self, context_a, user_a):
        task = create_task(context_a, user_a, {'title': 'Audited Task'})
        event = AuditEvent.objects.get(event_type='task.created')
        assert event.payload['task_id'] == str(task.id)
        assert event.actor == user_a

    def test_default_status_is_open(self, context_a, user_a):
        task = create_task(context_a, user_a, {'title': 'Default Status'})
        assert task.status == 'open'


@pytest.mark.django_db
class TestCompleteTask:
    def test_sets_status_done(self, org_a, context_a, user_a, task_a):
        complete_task(task_a, user_a)
        task_a.refresh_from_db()
        assert task_a.status == 'done'

    def test_sets_completed_at(self, org_a, context_a, user_a, task_a):
        before = timezone.now()
        complete_task(task_a, user_a)
        task_a.refresh_from_db()
        assert task_a.completed_at >= before

    def test_sets_completed_by(self, org_a, context_a, user_a, task_a):
        complete_task(task_a, user_a)
        task_a.refresh_from_db()
        assert task_a.completed_by == user_a

    def test_evidence_required_without_evidence_raises(self, org_a, context_a, user_a):
        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Needs Evidence', evidence_required=True,
        )
        with pytest.raises(EvidenceRequired):
            complete_task(task, user_a, has_evidence=False)

    def test_evidence_required_with_evidence_succeeds(self, org_a, context_a, user_a, document_a):
        from apps.documents.models import EvidenceSubmission

        task = Task.objects.create(
            organisation=org_a, operating_context=context_a,
            title='Has Evidence', evidence_required=True,
        )
        EvidenceSubmission.objects.create(
            organisation=org_a,
            operating_context=context_a,
            task=task,
            document=document_a,
            submitted_by=user_a,
            accepted=True,
        )
        complete_task(task, user_a, has_evidence=True)
        task.refresh_from_db()
        assert task.status == 'done'
        assert task.evidence_provided is True

    def test_emits_audit_event(self, org_a, context_a, user_a, task_a):
        complete_task(task_a, user_a)
        assert AuditEvent.objects.filter(event_type='task.completed').count() == 1
