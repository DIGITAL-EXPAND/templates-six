import pytest
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from apps.contexts.services import create_context, change_context_status
from common.enums import ContextStatus


@pytest.mark.django_db
class TestCreateContextService:
    def test_creates_context(self, org_a, site_a, user_a):
        ctx = create_context(
            organisation=org_a,
            user=user_a,
            data={'title': 'New Show', 'site': site_a, 'owner': user_a},
        )
        assert ctx.pk is not None
        assert ctx.title == 'New Show'
        assert ctx.organisation == org_a

    def test_emits_audit_event(self, org_a, site_a, user_a):
        assert AuditEvent.objects.count() == 0
        ctx = create_context(
            organisation=org_a,
            user=user_a,
            data={'title': 'New Show', 'site': site_a, 'owner': user_a},
        )
        event = AuditEvent.objects.get(event_type='context.created')
        assert event.actor == user_a
        assert event.organisation == org_a
        assert event.payload['context_id'] == str(ctx.id)
        assert event.payload['title'] == 'New Show'
        assert event.payload['status'] == ContextStatus.DRAFT

    def test_audit_event_payload_has_context_type(self, org_a, site_a, user_a):
        ctx = create_context(
            organisation=org_a,
            user=user_a,
            data={'title': 'Festival', 'context_type': 'festival', 'site': site_a, 'owner': user_a},
        )
        event = AuditEvent.objects.get(event_type='context.created')
        assert event.payload['context_type'] == 'festival'


@pytest.mark.django_db
class TestChangeContextStatusService:
    def test_valid_transition_draft_to_submitted(self, context_a, user_a):
        updated = change_context_status(context_a, user_a, 'submitted')
        assert updated.status == ContextStatus.SUBMITTED

    def test_valid_transition_submitted_to_under_review(self, context_a, user_a):
        context_a.status = ContextStatus.SUBMITTED
        context_a.save()
        updated = change_context_status(context_a, user_a, 'under_review')
        assert updated.status == ContextStatus.UNDER_REVIEW

    def test_valid_transition_rejected_to_draft(self, context_a, user_a):
        context_a.status = ContextStatus.REJECTED
        context_a.save()
        updated = change_context_status(context_a, user_a, 'draft')
        assert updated.status == ContextStatus.DRAFT

    def test_full_chain(self, context_a, user_a):
        chain = ['submitted', 'under_review', 'confirmed', 'in_production', 'in_delivery', 'completed', 'closed']
        for step in chain:
            context_a = change_context_status(context_a, user_a, step)
        assert context_a.status == ContextStatus.CLOSED

    def test_invalid_transition_raises(self, context_a, user_a):
        with pytest.raises(ValueError, match="Cannot transition from 'draft' to 'completed'"):
            change_context_status(context_a, user_a, 'completed')

    def test_invalid_transition_message_lists_valid_options(self, context_a, user_a):
        with pytest.raises(ValueError) as exc_info:
            change_context_status(context_a, user_a, 'closed')
        assert 'submitted' in str(exc_info.value)
        assert 'cancelled' in str(exc_info.value)

    def test_cancelled_is_terminal(self, context_a, user_a):
        context_a.status = ContextStatus.CANCELLED
        context_a.save()
        with pytest.raises(ValueError, match="terminal"):
            change_context_status(context_a, user_a, 'draft')

    def test_closed_is_terminal(self, context_a, user_a):
        context_a.status = ContextStatus.CLOSED
        context_a.save()
        with pytest.raises(ValueError, match="terminal"):
            change_context_status(context_a, user_a, 'draft')

    def test_emits_audit_event(self, context_a, user_a):
        change_context_status(context_a, user_a, 'submitted', comment='Ready')
        event = AuditEvent.objects.get(event_type='context.status_changed')
        assert event.actor == user_a
        assert event.payload['old_status'] == 'draft'
        assert event.payload['new_status'] == 'submitted'
        assert event.payload['comment'] == 'Ready'

    def test_audit_payload_contains_context_id(self, context_a, user_a):
        change_context_status(context_a, user_a, 'submitted')
        event = AuditEvent.objects.get(event_type='context.status_changed')
        assert event.payload['context_id'] == str(context_a.id)

    def test_persists_status_to_db(self, context_a, user_a):
        change_context_status(context_a, user_a, 'submitted')
        context_a.refresh_from_db()
        assert context_a.status == ContextStatus.SUBMITTED

    def test_invalid_status_value_raises(self, context_a, user_a):
        with pytest.raises(ValueError, match="not a valid status"):
            change_context_status(context_a, user_a, 'nonexistent')
