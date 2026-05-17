import datetime
import pytest
from apps.audit.models import AuditEvent
from apps.operations.models import FOHPlan, ShowDayChecklist, Incident


@pytest.mark.django_db
class TestFOHPlanCRUD:
    def test_list(self, client_a, foh_plan_a):
        r = client_a.get('/api/v1/operations/foh-plans/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/operations/foh-plans/', {
            'operating_context': str(context_a.id),
            'ushers': 8,
            'security': 4,
        }, format='json')
        assert r.status_code == 201
        assert FOHPlan.objects.filter(organisation=org_a, ushers=8).exists()

    def test_create_without_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/operations/foh-plans/', {
            'ushers': 5,
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, foh_plan_a):
        r = client_a.get(f'/api/v1/operations/foh-plans/{foh_plan_a.id}/')
        assert r.status_code == 200
        assert r.data['ushers'] == 5

    def test_partial_update(self, client_a, foh_plan_a):
        r = client_a.patch(
            f'/api/v1/operations/foh-plans/{foh_plan_a.id}/',
            {'ushers': 9}, format='json',
        )
        assert r.status_code == 200
        foh_plan_a.refresh_from_db()
        assert foh_plan_a.ushers == 9

    def test_direct_status_patch_rejected(self, client_a, foh_plan_a):
        r = client_a.patch(
            f'/api/v1/operations/foh-plans/{foh_plan_a.id}/',
            {'status': 'confirmed'}, format='json',
        )
        assert r.status_code == 400

    def test_confirm_action_sets_status(self, client_a, foh_plan_a):
        r = client_a.post(f'/api/v1/operations/foh-plans/{foh_plan_a.id}/confirm/')
        assert r.status_code == 200
        foh_plan_a.refresh_from_db()
        assert foh_plan_a.status == 'confirmed'

    def test_close_with_incomplete_checklist_returns_400(self, client_a, org_a, foh_plan_a):
        ShowDayChecklist.objects.create(
            organisation=org_a, foh_plan=foh_plan_a, item='Check emergency exits',
        )
        r = client_a.post(f'/api/v1/operations/foh-plans/{foh_plan_a.id}/close/')
        assert r.status_code == 400

    def test_close_after_checklist_sets_status(self, client_a, org_a, foh_plan_a):
        item = ShowDayChecklist.objects.create(
            organisation=org_a, foh_plan=foh_plan_a, item='Check emergency exits',
        )
        client_a.post(f'/api/v1/operations/checklists/{item.id}/check/')
        r = client_a.post(f'/api/v1/operations/foh-plans/{foh_plan_a.id}/close/')
        assert r.status_code == 200
        foh_plan_a.refresh_from_db()
        assert foh_plan_a.status == 'closed'

    def test_delete(self, client_a, foh_plan_a):
        r = client_a.delete(f'/api/v1/operations/foh-plans/{foh_plan_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, foh_plan_b):
        r = client_a.get(f'/api/v1/operations/foh-plans/{foh_plan_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/operations/foh-plans/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestFOHPlanUniqueEnforcement:
    def test_duplicate_context_returns_400(self, client_a, foh_plan_a, context_a):
        r = client_a.post('/api/v1/operations/foh-plans/', {
            'operating_context': str(context_a.id),
            'ushers': 10,
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, context_b):
        r = client_a.post('/api/v1/operations/foh-plans/', {
            'operating_context': str(context_b.id),
            'ushers': 5,
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestShowDayChecklistCRUD:
    def test_create(self, client_a, org_a, foh_plan_a):
        r = client_a.post('/api/v1/operations/checklists/', {
            'foh_plan': str(foh_plan_a.id),
            'item': 'Check emergency exits',
        }, format='json')
        assert r.status_code == 201
        assert ShowDayChecklist.objects.filter(
            organisation=org_a, item='Check emergency exits',
        ).exists()

    def test_create_without_foh_plan_returns_400(self, client_a):
        r = client_a.post('/api/v1/operations/checklists/', {
            'item': 'Orphan item',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_foh_plan_returns_400(self, client_a, foh_plan_b):
        r = client_a.post('/api/v1/operations/checklists/', {
            'foh_plan': str(foh_plan_b.id),
            'item': 'Cross-org item',
        }, format='json')
        assert r.status_code == 400

    def test_partial_update(self, client_a, org_a, foh_plan_a):
        item = ShowDayChecklist.objects.create(
            organisation=org_a, foh_plan=foh_plan_a, item='Lock stage door',
        )
        r = client_a.patch(
            f'/api/v1/operations/checklists/{item.id}/',
            {'item': 'Lock stage door twice'}, format='json',
        )
        assert r.status_code == 200
        item.refresh_from_db()
        assert item.item == 'Lock stage door twice'

    def test_direct_check_patch_rejected(self, client_a, org_a, foh_plan_a):
        item = ShowDayChecklist.objects.create(
            organisation=org_a, foh_plan=foh_plan_a, item='Lock stage door',
        )
        r = client_a.patch(
            f'/api/v1/operations/checklists/{item.id}/',
            {'is_checked': True}, format='json',
        )
        assert r.status_code == 400

    def test_check_action_sets_checked(self, client_a, org_a, foh_plan_a):
        item = ShowDayChecklist.objects.create(
            organisation=org_a, foh_plan=foh_plan_a, item='Lock stage door',
        )
        r = client_a.post(f'/api/v1/operations/checklists/{item.id}/check/')
        assert r.status_code == 200
        item.refresh_from_db()
        assert item.is_checked is True

    def test_cannot_reach_other_org(self, client_a, org_b, foh_plan_b):
        item = ShowDayChecklist.objects.create(
            organisation=org_b, foh_plan=foh_plan_b, item='B item',
        )
        r = client_a.get(f'/api/v1/operations/checklists/{item.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestIncidentCRUD:
    def test_create(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'patron_complaint',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Patron unhappy with seating.',
            'severity': 'low',
        }, format='json')
        assert r.status_code == 201
        assert Incident.objects.filter(organisation=org_a).exists()

    def test_create_sets_reported_by(self, client_a, context_a, user_a):
        client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'late_start',
            'occurred_at': '2026-05-07T20:05:00Z',
            'description': 'Show started 5 minutes late.',
            'severity': 'low',
        }, format='json')
        incident = Incident.objects.get(incident_type='late_start')
        assert incident.reported_by == user_a

    def test_create_without_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/operations/incidents/', {
            'incident_type': 'other',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Orphan incident.',
            'severity': 'low',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, context_b):
        r = client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_b.id),
            'incident_type': 'other',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Cross org.',
            'severity': 'low',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, org_b, context_b, user_b):
        incident = Incident.objects.create(
            organisation=org_b, operating_context=context_b,
            incident_type='other', occurred_at='2026-05-07T20:00:00Z',
            description='B incident.', severity='low', reported_by=user_b,
        )
        r = client_a.get(f'/api/v1/operations/incidents/{incident.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestIncidentAuditEvents:
    def test_low_severity_emits_incident_logged(self, client_a, context_a):
        client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'patron_complaint',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Low severity incident.',
            'severity': 'low',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='incident.logged').exists()
        assert not AuditEvent.objects.filter(event_type='incident.critical_logged').exists()

    def test_medium_severity_emits_incident_logged(self, client_a, context_a):
        client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'equipment_failure',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Medium severity.',
            'severity': 'medium',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='incident.logged').exists()

    def test_high_severity_emits_critical_logged(self, client_a, context_a):
        client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'safety_incident',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'High severity incident.',
            'severity': 'high',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='incident.critical_logged').exists()
        assert not AuditEvent.objects.filter(event_type='incident.logged').exists()

    def test_critical_severity_emits_critical_logged(self, client_a, context_a):
        client_a.post('/api/v1/operations/incidents/', {
            'operating_context': str(context_a.id),
            'incident_type': 'medical',
            'occurred_at': '2026-05-07T20:00:00Z',
            'description': 'Critical incident.',
            'severity': 'critical',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='incident.critical_logged').exists()
