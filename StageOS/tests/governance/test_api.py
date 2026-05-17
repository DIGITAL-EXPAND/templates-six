import pytest
from apps.governance.models import KPI, KPIEvidence, Risk, CorrectiveAction, ExecutiveAction
from apps.audit.models import AuditEvent
from apps.tasks.models import Task


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def kpi_a(db, org_a):
    return KPI.objects.create(
        organisation=org_a,
        name='Attendance Rate',
        target_value='80.00',
        actual_value='0.00',
        unit='%',
        reporting_period='quarterly',
    )


@pytest.fixture
def evidence_required_kpi_a(db, org_a):
    return KPI.objects.create(
        organisation=org_a,
        name='Evidence-backed Youth Reach',
        target_value='100.00',
        actual_value='0.00',
        unit='count',
        evidence_description='Upload the signed attendance summary.',
        reporting_period='quarterly',
    )


@pytest.fixture
def kpi_b(db, org_b):
    return KPI.objects.create(
        organisation=org_b,
        name='Org B KPI',
        target_value='100.00',
        unit='count',
        reporting_period='monthly',
    )


@pytest.fixture
def risk_a(db, org_a, user_a):
    return Risk.objects.create(
        organisation=org_a,
        title='Budget overrun risk',
        risk_level='high',
        owner=user_a,
    )


@pytest.fixture
def risk_b(db, org_b, user_b):
    return Risk.objects.create(
        organisation=org_b,
        title='Org B Risk',
        risk_level='low',
        owner=user_b,
    )


@pytest.fixture
def corrective_action_a(db, org_a, risk_a, user_a):
    return CorrectiveAction.objects.create(
        organisation=org_a,
        risk=risk_a,
        action='Review budget monthly',
        owner=user_a,
    )


# ── KPI CRUD ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestKPICRUD:
    def test_create(self, client_a):
        r = client_a.post('/api/v1/governance/kpis/', {
            'name': 'Youth Reached',
            'target_value': '500.00',
            'unit': 'count',
            'reporting_period': 'annually',
        }, format='json')
        assert r.status_code == 201
        assert r.data['name'] == 'Youth Reached'
        assert r.data['actual_value'] == '0.00'

    def test_list(self, client_a, kpi_a):
        r = client_a.get('/api/v1/governance/kpis/')
        assert r.status_code == 200
        ids = [x['id'] for x in r.data['results']]
        assert str(kpi_a.id) in ids

    def test_retrieve(self, client_a, kpi_a):
        r = client_a.get(f'/api/v1/governance/kpis/{kpi_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == kpi_a.name

    def test_update(self, client_a, kpi_a):
        r = client_a.patch(f'/api/v1/governance/kpis/{kpi_a.id}/', {
            'target_value': '90.00',
        }, format='json')
        assert r.status_code == 200
        assert r.data['target_value'] == '90.00'

    def test_delete(self, client_a, kpi_a):
        r = client_a.delete(f'/api/v1/governance/kpis/{kpi_a.id}/')
        assert r.status_code == 405

    def test_filter_by_period(self, client_a, kpi_a):
        r = client_a.get('/api/v1/governance/kpis/?reporting_period=quarterly')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_cannot_see_other_org_kpi(self, client_a, kpi_b):
        r = client_a.get(f'/api/v1/governance/kpis/{kpi_b.id}/')
        assert r.status_code == 404


# ── Report KPI action ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestReportKPIAction:
    def test_report_creates_evidence(self, client_a, kpi_a):
        r = client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '75.00',
            'notes': 'Q2 result',
        }, format='json')
        assert r.status_code == 200
        assert KPIEvidence.objects.filter(kpi=kpi_a).count() == 1

    def test_report_updates_actual_value(self, client_a, kpi_a):
        client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '75.00',
        }, format='json')
        kpi_a.refresh_from_db()
        assert kpi_a.actual_value == 75

    def test_report_emits_audit_with_old_and_new_values(self, client_a, kpi_a):
        client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '65.00',
        }, format='json')
        event = AuditEvent.objects.get(event_type='governance.kpi_reported')
        assert event.payload['old_value'] == '0.00'
        assert event.payload['new_value'] == '65.00'

    def test_report_with_context(self, client_a, kpi_a, context_a):
        r = client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '80.00',
            'context': str(context_a.id),
        }, format='json')
        assert r.status_code == 200
        evidence = KPIEvidence.objects.get(kpi=kpi_a)
        assert evidence.operating_context == context_a

    def test_report_with_other_org_context_rejected(self, client_a, kpi_a, context_b):
        r = client_a.post(f'/api/v1/governance/kpis/{kpi_a.id}/report/', {
            'value': '80.00',
            'context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_evidence_required_kpi_without_document_returns_400(self, client_a, evidence_required_kpi_a):
        r = client_a.post(f'/api/v1/governance/kpis/{evidence_required_kpi_a.id}/report/', {
            'value': '80.00',
        }, format='json')
        assert r.status_code == 400

    def test_evidence_required_kpi_with_document_succeeds(self, client_a, evidence_required_kpi_a, document_a):
        r = client_a.post(f'/api/v1/governance/kpis/{evidence_required_kpi_a.id}/report/', {
            'value': '80.00',
            'evidence_document': str(document_a.id),
        }, format='json')
        assert r.status_code == 200
        assert str(r.data['evidence_document']) == str(document_a.id)


# ── KPIEvidence list ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestKPIEvidenceList:
    def test_list_evidence(self, client_a, kpi_a, user_a):
        KPIEvidence.objects.create(
            organisation=kpi_a.organisation, kpi=kpi_a,
            value_reported='70.00', reported_by=user_a,
        )
        r = client_a.get('/api/v1/governance/kpi-evidence/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_kpi(self, client_a, kpi_a, user_a):
        KPIEvidence.objects.create(
            organisation=kpi_a.organisation, kpi=kpi_a,
            value_reported='70.00', reported_by=user_a,
        )
        r = client_a.get(f'/api/v1/governance/kpi-evidence/?kpi={kpi_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_kpi_evidence_read_only(self, client_a):
        r = client_a.post('/api/v1/governance/kpi-evidence/', {}, format='json')
        assert r.status_code == 405


# ── Risk CRUD ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRiskCRUD:
    def test_create_org_level_risk(self, client_a, user_a):
        r = client_a.post('/api/v1/governance/risks/', {
            'title': 'Reputational risk',
            'risk_level': 'medium',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert r.data['title'] == 'Reputational risk'
        assert r.data['operating_context'] is None

    def test_create_context_linked_risk(self, client_a, context_a, user_a):
        r = client_a.post('/api/v1/governance/risks/', {
            'title': 'Budget overrun',
            'risk_level': 'high',
            'owner': str(user_a.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 201
        assert str(r.data['operating_context']) == str(context_a.id)

    def test_list(self, client_a, risk_a):
        r = client_a.get('/api/v1/governance/risks/')
        assert r.status_code == 200
        ids = [x['id'] for x in r.data['results']]
        assert str(risk_a.id) in ids

    def test_filter_by_level(self, client_a, risk_a):
        r = client_a.get('/api/v1/governance/risks/?risk_level=high')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_update(self, client_a, risk_a):
        r = client_a.patch(f'/api/v1/governance/risks/{risk_a.id}/', {
            'mitigation_plan': 'Monthly review of budget.',
        }, format='json')
        assert r.status_code == 200

    def test_delete(self, client_a, risk_a):
        r = client_a.delete(f'/api/v1/governance/risks/{risk_a.id}/')
        assert r.status_code == 405

    def test_cannot_create_with_other_org_context(self, client_a, context_b, user_a):
        r = client_a.post('/api/v1/governance/risks/', {
            'title': 'Cross-org risk',
            'risk_level': 'low',
            'owner': str(user_a.id),
            'operating_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400


# ── Close risk action ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCloseRiskAction:
    def test_close_risk(self, client_a, risk_a):
        r = client_a.post(f'/api/v1/governance/risks/{risk_a.id}/close/', {
            'comment': 'Risk mitigated',
        }, format='json')
        assert r.status_code == 200
        assert r.data['status'] == 'closed'

    def test_close_sets_closed_date_and_by(self, client_a, risk_a, user_a):
        client_a.post(f'/api/v1/governance/risks/{risk_a.id}/close/', {}, format='json')
        risk_a.refresh_from_db()
        assert risk_a.closed_date is not None
        assert risk_a.closed_by == user_a

    def test_close_already_closed_returns_400(self, client_a, risk_a):
        client_a.post(f'/api/v1/governance/risks/{risk_a.id}/close/', {}, format='json')
        r = client_a.post(f'/api/v1/governance/risks/{risk_a.id}/close/', {}, format='json')
        assert r.status_code == 400

    def test_close_emits_audit_event(self, client_a, risk_a):
        client_a.post(f'/api/v1/governance/risks/{risk_a.id}/close/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='governance.risk_closed').count() == 1


# ── CorrectiveAction CRUD ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCorrectiveActionCRUD:
    def test_create(self, client_a, risk_a, user_a):
        r = client_a.post('/api/v1/governance/corrective-actions/', {
            'risk': str(risk_a.id),
            'action': 'Implement monthly reviews',
            'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert r.data['status'] == 'open'

    def test_list(self, client_a, corrective_action_a):
        r = client_a.get('/api/v1/governance/corrective-actions/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_risk(self, client_a, corrective_action_a, risk_a):
        r = client_a.get(f'/api/v1/governance/corrective-actions/?risk={risk_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_update(self, client_a, corrective_action_a):
        r = client_a.patch(f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/', {
            'action': 'Updated corrective action',
        }, format='json')
        assert r.status_code == 200

    def test_direct_status_patch_rejected(self, client_a, corrective_action_a):
        r = client_a.patch(f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/', {
            'status': 'in_progress',
        }, format='json')
        assert r.status_code == 400

    def test_delete(self, client_a, corrective_action_a):
        r = client_a.delete(f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/')
        assert r.status_code == 405


# ── Complete corrective action ────────────────────────────────────────────────

@pytest.mark.django_db
class TestCompleteCorrectiveAction:
    def test_complete_without_evidence_returns_400(self, client_a, corrective_action_a):
        r = client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        assert r.status_code == 400

    def test_complete(self, client_a, corrective_action_a, document_a):
        corrective_action_a.evidence_document = document_a
        corrective_action_a.save(update_fields=['evidence_document'])
        r = client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'completed'

    def test_complete_sets_date_and_user(self, client_a, corrective_action_a, user_a, document_a):
        corrective_action_a.evidence_document = document_a
        corrective_action_a.save(update_fields=['evidence_document'])
        client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        corrective_action_a.refresh_from_db()
        assert corrective_action_a.completed_date is not None
        assert corrective_action_a.completed_by == user_a

    def test_complete_already_completed_returns_400(self, client_a, corrective_action_a, document_a):
        corrective_action_a.evidence_document = document_a
        corrective_action_a.save(update_fields=['evidence_document'])
        client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        r = client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        assert r.status_code == 400

    def test_complete_emits_audit_event(self, client_a, corrective_action_a, document_a):
        corrective_action_a.evidence_document = document_a
        corrective_action_a.save(update_fields=['evidence_document'])
        client_a.post(
            f'/api/v1/governance/corrective-actions/{corrective_action_a.id}/complete/',
            {}, format='json',
        )
        assert AuditEvent.objects.filter(
            event_type='governance.corrective_action_completed'
        ).count() == 1


@pytest.mark.django_db
class TestExecutiveActionWorkflow:
    def test_executive_request_change_creates_task_and_audit(self, client_a, context_a, department_a, user_a):
        r = client_a.post('/api/v1/governance/executive-actions/', {
            'action_type': 'request_change',
            'title': 'Revise campaign artwork',
            'reason': 'Artwork does not match approved institutional positioning.',
            'instruction': 'Add funder logo and correct title before publishing.',
            'operating_context': str(context_a.id),
            'target_type': 'Campaign',
            'target_id': 'campaign-1',
            'department': str(department_a.id),
            'assigned_to': str(user_a.id),
            'due_date': '2026-06-01',
        }, format='json')
        assert r.status_code == 201
        action = ExecutiveAction.objects.get(id=r.data['id'])
        assert action.linked_task is not None
        assert action.linked_task.evidence_required is True
        assert Task.objects.filter(title='Executive action: Revise campaign artwork').exists()
        assert AuditEvent.objects.filter(event_type='executive.action_created').exists()

    def test_flag_risk_creates_risk(self, client_a, context_a, user_a):
        r = client_a.post('/api/v1/governance/executive-actions/', {
            'action_type': 'flag_risk',
            'title': 'Reputational risk',
            'reason': 'Public messaging conflicts with institutional position.',
            'instruction': 'Prepare mitigation note.',
            'operating_context': str(context_a.id),
            'assigned_to': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        action = ExecutiveAction.objects.get(id=r.data['id'])
        assert action.linked_risk is not None
        assert action.linked_risk.risk_level == 'high'

    def test_assign_corrective_action_creates_risk_action_and_task(self, client_a, context_a, user_a):
        r = client_a.post('/api/v1/governance/executive-actions/', {
            'action_type': 'assign_corrective_action',
            'title': 'Fix readiness blocker',
            'reason': 'FOH checklist remains incomplete.',
            'instruction': 'Complete checklist and submit evidence.',
            'operating_context': str(context_a.id),
            'assigned_to': str(user_a.id),
            'due_date': '2026-06-02',
        }, format='json')
        assert r.status_code == 201
        action = ExecutiveAction.objects.get(id=r.data['id'])
        assert action.linked_task is not None
        assert action.linked_risk is not None
        assert action.linked_corrective_action is not None

    def test_override_requires_reason(self, client_a, context_a):
        r = client_a.post('/api/v1/governance/executive-actions/', {
            'action_type': 'override',
            'title': 'Approve exception',
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400
        assert 'reason' in r.data

    def test_staff_cannot_create_executive_action(self, org_a, context_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        staff = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        api = APIClient()
        api.force_authenticate(user=staff)
        r = api.post('/api/v1/governance/executive-actions/', {
            'action_type': 'comment',
            'title': 'Staff comment',
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 403

    def test_staff_can_view_executive_actions(self, org_a, context_a, user_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='comment',
            title='Visible instruction',
            operating_context=context_a,
            created_by=user_a,
        )
        staff = User.objects.create_user(
            email='staff-view@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        api = APIClient()
        api.force_authenticate(user=staff)
        r = api.get('/api/v1/governance/executive-actions/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_staff_can_acknowledge_and_complete_executive_action(self, org_a, context_a, user_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        action = ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='request_change',
            title='Department action',
            reason='Executive instruction',
            instruction='Respond from department queue.',
            operating_context=context_a,
            created_by=user_a,
        )
        staff = User.objects.create_user(
            email='department-user@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        api = APIClient()
        api.force_authenticate(user=staff)
        r = api.post(
            f'/api/v1/governance/executive-actions/{action.id}/acknowledge/',
            {'comment': 'Seen by department'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'acknowledged'
        r = api.post(
            f'/api/v1/governance/executive-actions/{action.id}/complete/',
            {'comment': 'Resolved by department'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'completed'

    def test_staff_cannot_cancel_executive_action(self, org_a, context_a, user_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        action = ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='comment',
            title='Executive only cancel',
            operating_context=context_a,
            created_by=user_a,
        )
        staff = User.objects.create_user(
            email='department-cancel@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='staff',
        )
        api = APIClient()
        api.force_authenticate(user=staff)
        r = api.post(
            f'/api/v1/governance/executive-actions/{action.id}/cancel/',
            {'comment': 'Trying to cancel'}, format='json',
        )
        assert r.status_code == 403

    def test_acknowledge_complete_and_cancel_are_audited(self, client_a, org_a, context_a, user_a):
        action = ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='comment',
            title='Executive note',
            operating_context=context_a,
            created_by=user_a,
        )
        r = client_a.post(
            f'/api/v1/governance/executive-actions/{action.id}/acknowledge/',
            {'comment': 'Seen'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'acknowledged'
        r = client_a.post(
            f'/api/v1/governance/executive-actions/{action.id}/complete/',
            {'comment': 'Handled'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'completed'
        assert AuditEvent.objects.filter(event_type='executive.action_acknowledged').exists()
        assert AuditEvent.objects.filter(event_type='executive.action_completed').exists()

    def test_cancel_requires_comment(self, client_a, org_a, context_a, user_a):
        action = ExecutiveAction.objects.create(
            organisation=org_a,
            action_type='comment',
            title='Cancel me',
            operating_context=context_a,
            created_by=user_a,
        )
        r = client_a.post(
            f'/api/v1/governance/executive-actions/{action.id}/cancel/',
            {'comment': ''}, format='json',
        )
        assert r.status_code == 400
        assert 'comment' in r.data

    def test_other_org_executive_action_hidden(self, client_a, org_b, context_b, user_b):
        action = ExecutiveAction.objects.create(
            organisation=org_b,
            action_type='comment',
            title='Other org',
            operating_context=context_b,
            created_by=user_b,
        )
        r = client_a.get(f'/api/v1/governance/executive-actions/{action.id}/')
        assert r.status_code == 404
