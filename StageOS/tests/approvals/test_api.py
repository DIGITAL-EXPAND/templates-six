import pytest
from apps.approvals.models import ApprovalRoute, ApprovalStep, ApprovalRequest, ApprovalDecision
from apps.audit.models import AuditEvent


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def route_a(db, org_a):
    return ApprovalRoute.objects.create(organisation=org_a, name='Programming Route')


@pytest.fixture
def route_b(db, org_b):
    return ApprovalRoute.objects.create(organisation=org_b, name='Other Route')


@pytest.fixture
def step_a(db, org_a, route_a):
    return ApprovalStep.objects.create(
        organisation=org_a,
        route=route_a,
        step_number=1,
        name='Programming Approval',
    )


@pytest.fixture
def step_b(db, org_b, route_b):
    return ApprovalStep.objects.create(
        organisation=org_b,
        route=route_b,
        step_number=1,
        name='Other Step',
    )


@pytest.fixture
def approval_request_a(db, org_a, context_a, step_a, user_a):
    return ApprovalRequest.objects.create(
        organisation=org_a,
        operating_context=context_a,
        approval_step=step_a,
        requested_by=user_a,
        decision=ApprovalDecision.PENDING,
    )


# ── ApprovalRoute CRUD ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestApprovalRouteCRUD:
    def test_create(self, client_a, org_a):
        r = client_a.post('/api/v1/approvals/routes/', {
            'name': 'Budget Route',
            'description': 'Finance sign-off',
            'is_active': True,
        }, format='json')
        assert r.status_code == 201
        assert r.data['name'] == 'Budget Route'

    def test_list(self, client_a, route_a):
        r = client_a.get('/api/v1/approvals/routes/')
        assert r.status_code == 200
        ids = [x['id'] for x in r.data['results']]
        assert str(route_a.id) in ids

    def test_retrieve(self, client_a, route_a):
        r = client_a.get(f'/api/v1/approvals/routes/{route_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == route_a.name

    def test_update(self, client_a, route_a):
        r = client_a.patch(f'/api/v1/approvals/routes/{route_a.id}/', {
            'name': 'Updated Route',
        }, format='json')
        assert r.status_code == 200
        assert r.data['name'] == 'Updated Route'

    def test_delete(self, client_a, route_a):
        r = client_a.delete(f'/api/v1/approvals/routes/{route_a.id}/')
        assert r.status_code == 405

    def test_cannot_see_other_org_route(self, client_a, route_b):
        r = client_a.get(f'/api/v1/approvals/routes/{route_b.id}/')
        assert r.status_code == 404


# ── ApprovalStep CRUD ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestApprovalStepCRUD:
    def test_create(self, client_a, route_a):
        r = client_a.post('/api/v1/approvals/steps/', {
            'route': str(route_a.id),
            'step_number': 1,
            'name': 'CEO Sign-off',
        }, format='json')
        assert r.status_code == 201
        assert r.data['name'] == 'CEO Sign-off'

    def test_list(self, client_a, step_a):
        r = client_a.get('/api/v1/approvals/steps/')
        assert r.status_code == 200
        ids = [x['id'] for x in r.data['results']]
        assert str(step_a.id) in ids

    def test_unique_step_number_enforced(self, client_a, route_a, step_a):
        r = client_a.post('/api/v1/approvals/steps/', {
            'route': str(route_a.id),
            'step_number': 1,
            'name': 'Duplicate Step',
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_route_rejected(self, client_a, route_b):
        r = client_a.post('/api/v1/approvals/steps/', {
            'route': str(route_b.id),
            'step_number': 1,
            'name': 'Cross-org Step',
        }, format='json')
        assert r.status_code == 400

    def test_filter_by_route(self, client_a, route_a, step_a):
        r = client_a.get(f'/api/v1/approvals/steps/?route={route_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1


# ── ApprovalRequest: submit ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestSubmitForApproval:
    def test_submit_creates_pending_request(self, client_a, context_a, step_a):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(step_a.id),
        }, format='json')
        assert r.status_code == 201
        assert r.data['decision'] == 'pending'

    def test_submit_sets_requested_by(self, client_a, context_a, step_a, user_a):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(step_a.id),
        }, format='json')
        assert r.status_code == 201
        req = ApprovalRequest.objects.first()
        assert req.requested_by == user_a

    def test_submit_emits_audit_event(self, client_a, context_a, step_a):
        client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(step_a.id),
        }, format='json')
        assert AuditEvent.objects.filter(event_type='approval.requested').count() == 1

    def test_submit_with_other_org_context_rejected(self, client_a, context_b, step_a):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_b.id),
            'approval_step': str(step_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_submit_with_other_org_step_rejected(self, client_a, context_a, step_b):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(step_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_list_requests(self, client_a, approval_request_a):
        r = client_a.get('/api/v1/approvals/requests/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_decision(self, client_a, approval_request_a):
        r = client_a.get('/api/v1/approvals/requests/?decision=pending')
        assert r.status_code == 200
        assert r.data['count'] == 1


# ── Approve action ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestApproveAction:
    def test_approve_sets_decision(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Looks good'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'approved'

    def test_approve_sets_decided_by_and_at(self, client_a, approval_request_a, user_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'OK'},
            format='json',
        )
        approval_request_a.refresh_from_db()
        assert approval_request_a.decided_by == user_a
        assert approval_request_a.decided_at is not None

    def test_approve_emits_audit_event_with_old_and_new_values(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Approved'},
            format='json',
        )
        event = AuditEvent.objects.get(event_type='approval.decided')
        assert event.payload['old_value'] == 'pending'
        assert event.payload['new_value'] == 'approved'

    def test_cannot_approve_other_org_request(self, client_a, org_b, context_b, step_b, user_b):
        req_b = ApprovalRequest.objects.create(
            organisation=org_b, operating_context=context_b,
            approval_step=step_b, requested_by=user_b,
        )
        r = client_a.post(f'/api/v1/approvals/requests/{req_b.id}/approve/', {}, format='json')
        assert r.status_code == 404

    def test_staff_cannot_decide_approval(self, org_a, approval_request_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        staff = User.objects.create_user(
            email='approval-staff@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        api = APIClient()
        api.force_authenticate(user=staff)
        r = api.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Trying to approve'}, format='json',
        )
        assert r.status_code == 403


# ── Reject action ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRejectAction:
    def test_reject_sets_decision(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/reject/',
            {'comment': 'Budget not confirmed'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'rejected'

    def test_reject_emits_audit_event(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/reject/',
            {'comment': 'No budget'},
            format='json',
        )
        event = AuditEvent.objects.get(event_type='approval.decided')
        assert event.payload['new_value'] == 'rejected'
        assert event.payload['old_value'] == 'pending'

    def test_reject_requires_comment(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/reject/',
            {'comment': ''},
            format='json',
        )
        assert r.status_code == 400
        assert 'comment' in r.data


# ── Request-changes action ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRequestChangesAction:
    def test_request_changes_sets_decision(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/request-changes/',
            {'comment': 'Please update the dates'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'changes_requested'

    def test_request_changes_emits_audit_event(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/request-changes/',
            {'comment': 'Needs revision'},
            format='json',
        )
        event = AuditEvent.objects.get(event_type='approval.decided')
        assert event.payload['new_value'] == 'changes_requested'

    def test_request_changes_requires_comment(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/request-changes/',
            {'comment': ''},
            format='json',
        )
        assert r.status_code == 400

    def test_request_more_information_sets_changes_requested(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/request-more-information/',
            {'comment': 'Please provide a revised brief.'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'changes_requested'

    def test_escalate_sets_decision_and_requires_comment(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/escalate/',
            {'comment': 'Escalate to board committee.'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'escalated'

    def test_exception_approve_requires_comment(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/exception-approve/',
            {'comment': ''},
            format='json',
        )
        assert r.status_code == 400

    def test_exception_approve_sets_decision(self, client_a, approval_request_a):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/exception-approve/',
            {'comment': 'Executive override approved with risk noted.'},
            format='json',
        )
        assert r.status_code == 200
        assert r.data['decision'] == 'exception_approved'


# ── Already-decided guard ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAlreadyDecidedGuard:
    def test_cannot_approve_already_approved_request(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'First decision'},
            format='json',
        )
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Second attempt'},
            format='json',
        )
        assert r.status_code == 400

    def test_cannot_reject_already_approved_request(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Approved'},
            format='json',
        )
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/reject/',
            {'comment': 'Too late'},
            format='json',
        )
        assert r.status_code == 400

    def test_error_message_mentions_current_decision(self, client_a, approval_request_a):
        client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/reject/',
            {'comment': 'No'},
            format='json',
        )
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_a.id}/approve/',
            {'comment': 'Retry'},
            format='json',
        )
        assert r.status_code == 400
        assert 'rejected' in str(r.data).lower() or 'decided' in str(r.data).lower()
