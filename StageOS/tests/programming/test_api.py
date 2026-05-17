import datetime
import pytest
from apps.audit.models import AuditEvent
from apps.programming.models import (
    CalendarIssue, IntakeRequest, IntakeReview, ProducerAssignment, VenueHold, CalendarSlot,
)


@pytest.mark.django_db
class TestIntakeRequestFlow:
    def test_internal_user_can_create_private_intake_request(self, client_a, org_a, venue_a, user_a):
        r = client_a.post('/api/v1/programming/intake-requests/', {
            'request_type': 'venue_booking',
            'event_title': 'Client Gala',
            'client_name': 'Client One',
            'client_organisation': 'Client Org',
            'contact_email': 'client@example.com',
            'requested_start_date': '2026-07-10',
            'preferred_venue': str(venue_a.id),
            'expected_audience': 250,
            'ticketing_required': True,
            'technical_summary': 'Basic sound',
            'foh_notes': 'VIP guests',
            'accessibility_requirements': 'Wheelchair access',
        }, format='json')
        assert r.status_code == 201
        intake = IntakeRequest.objects.get(organisation=org_a)
        assert intake.status == 'submitted'
        assert intake.submitted_by == user_a
        assert AuditEvent.objects.filter(event_type='intake.request_submitted').exists()

    def test_client_external_sees_only_own_intake_requests(self, org_a, client_a, venue_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        client_user = User.objects.create_user(
            email='client@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='client_external',
        )
        other_client = User.objects.create_user(
            email='other-client@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='client_external',
        )
        IntakeRequest.objects.create(
            organisation=org_a,
            request_type='venue_booking',
            event_title='Own Request',
            client_name='Own Client',
            submitted_by=client_user,
            preferred_venue=venue_a,
        )
        IntakeRequest.objects.create(
            organisation=org_a,
            request_type='production_proposal',
            event_title='Other Request',
            client_name='Other Client',
            submitted_by=other_client,
        )
        api = APIClient()
        api.force_authenticate(user=client_user)

        r = api.get('/api/v1/programming/intake-requests/')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['event_title'] == 'Own Request'

    def test_external_supplier_cannot_access_private_intake(self, org_a):
        from apps.accounts.models import User
        from rest_framework.test import APIClient

        supplier = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            organisation=org_a,
            user_type='supplier_external',
        )
        api = APIClient()
        api.force_authenticate(user=supplier)
        r = api.get('/api/v1/programming/intake-requests/')
        assert r.status_code == 403

    def test_intake_review_and_leadership_decisions_are_audited(self, client_a, org_a):
        intake = IntakeRequest.objects.create(
            organisation=org_a,
            request_type='production_proposal',
            event_title='New Work',
            client_name='Producer',
        )
        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/start-review/',
            {'comment': 'Programming is reviewing'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'under_review'

        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/request-changes/',
            {'comment': 'Please add technical details'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'changes_requested'
        assert AuditEvent.objects.filter(event_type='intake.review_started').exists()
        assert AuditEvent.objects.filter(event_type='intake.changes_requested').exists()

    def test_decline_requires_comment(self, client_a, org_a):
        intake = IntakeRequest.objects.create(
            organisation=org_a,
            request_type='production_proposal',
            event_title='Risky Work',
            client_name='Producer',
            status='under_review',
        )
        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/decline/',
            {'comment': ''}, format='json',
        )
        assert r.status_code == 400
        assert 'comment' in r.data

    def test_approved_intake_converts_to_workspace_once(self, client_a, org_a, venue_a, site_a, user_a):
        intake = IntakeRequest.objects.create(
            organisation=org_a,
            request_type='venue_booking',
            event_title='Converted Gala',
            client_name='Client',
            status='approved',
            preferred_venue=venue_a,
            requested_start_date='2026-08-01',
            ticketing_required=True,
        )
        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/convert-to-workspace/',
            {'site': str(site_a.id), 'owner': str(user_a.id), 'priority': 'high'},
            format='json',
        )
        assert r.status_code == 201
        intake.refresh_from_db()
        assert intake.status == 'converted'
        assert intake.converted_context_id
        assert intake.converted_context.title == 'Converted Gala'
        assert intake.converted_context.context_type == 'venue_rental'
        assert AuditEvent.objects.filter(event_type='intake.converted_to_workspace').exists()

        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/convert-to-workspace/',
            {'site': str(site_a.id), 'owner': str(user_a.id)},
            format='json',
        )
        assert r.status_code == 400

    def test_unapproved_intake_cannot_convert(self, client_a, org_a, site_a, user_a):
        intake = IntakeRequest.objects.create(
            organisation=org_a,
            request_type='production_proposal',
            event_title='Draft Proposal',
            client_name='Client',
        )
        r = client_a.post(
            f'/api/v1/programming/intake-requests/{intake.id}/convert-to-workspace/',
            {'site': str(site_a.id), 'owner': str(user_a.id)},
            format='json',
        )
        assert r.status_code == 400

    def test_other_tenant_cannot_retrieve_intake_request(self, client_a, org_b):
        intake = IntakeRequest.objects.create(
            organisation=org_b,
            request_type='production_proposal',
            event_title='Other Tenant',
            client_name='Client',
        )
        r = client_a.get(f'/api/v1/programming/intake-requests/{intake.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestIntakeReviewCRUD:
    def test_list(self, client_a, intake_review_a):
        r = client_a.get('/api/v1/programming/intake-reviews/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a, user_a):
        r = client_a.post('/api/v1/programming/intake-reviews/', {
            'operating_context': str(context_a.id),
            'reviewed_by': str(user_a.id),
            'review_date': '2026-05-10',
            'recommendation': 'approve',
        }, format='json')
        assert r.status_code == 201
        assert IntakeReview.objects.filter(organisation=org_a).exists()

    def test_create_without_context_returns_400(self, client_a, user_a):
        r = client_a.post('/api/v1/programming/intake-reviews/', {
            'reviewed_by': str(user_a.id),
            'review_date': '2026-05-10',
            'recommendation': 'approve',
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, intake_review_a):
        r = client_a.get(f'/api/v1/programming/intake-reviews/{intake_review_a.id}/')
        assert r.status_code == 200

    def test_partial_update(self, client_a, intake_review_a):
        r = client_a.patch(
            f'/api/v1/programming/intake-reviews/{intake_review_a.id}/',
            {'notes': 'Updated review notes'}, format='json',
        )
        assert r.status_code == 200
        intake_review_a.refresh_from_db()
        assert intake_review_a.notes == 'Updated review notes'

    def test_direct_status_patch_rejected(self, client_a, intake_review_a):
        r = client_a.patch(
            f'/api/v1/programming/intake-reviews/{intake_review_a.id}/',
            {'status': 'reviewed'}, format='json',
        )
        assert r.status_code == 400

    def test_delete(self, client_a, intake_review_a):
        r = client_a.delete(f'/api/v1/programming/intake-reviews/{intake_review_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, intake_review_b):
        r = client_a.get(f'/api/v1/programming/intake-reviews/{intake_review_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/programming/intake-reviews/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestIntakeReviewUniqueEnforcement:
    def test_duplicate_context_returns_400(self, client_a, intake_review_a, context_a, user_a):
        r = client_a.post('/api/v1/programming/intake-reviews/', {
            'operating_context': str(context_a.id),
            'reviewed_by': str(user_a.id),
            'review_date': '2026-05-10',
            'recommendation': 'defer',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, context_b, user_a):
        r = client_a.post('/api/v1/programming/intake-reviews/', {
            'operating_context': str(context_b.id),
            'reviewed_by': str(user_a.id),
            'review_date': '2026-05-10',
            'recommendation': 'approve',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_reviewed_by_returns_400(self, client_a, context_a, user_b):
        r = client_a.post('/api/v1/programming/intake-reviews/', {
            'operating_context': str(context_a.id),
            'reviewed_by': str(user_b.id),
            'review_date': '2026-05-10',
            'recommendation': 'approve',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestProducerAssignmentCRUD:
    def test_create(self, client_a, org_a, context_a, user_a):
        r = client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_a.id),
        }, format='json')
        assert r.status_code == 201
        assert ProducerAssignment.objects.filter(organisation=org_a).exists()

    def test_create_emits_audit(self, client_a, context_a, user_a):
        client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_a.id),
        }, format='json')
        assert AuditEvent.objects.filter(event_type='producer.assigned').exists()

    def test_duplicate_producer_returns_400(self, client_a, context_a, user_a):
        client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_a.id),
        }, format='json')
        r = client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_producer_returns_400(self, client_a, context_a, user_b):
        r = client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_list_excludes_other_org(self, client_a, context_a, user_a, context_b, user_b, org_b):
        from apps.programming.models import ProducerAssignment
        ProducerAssignment.objects.create(
            organisation=org_b, operating_context=context_b, producer=user_b, assigned_by=user_b,
        )
        client_a.post('/api/v1/programming/producer-assignments/', {
            'operating_context': str(context_a.id),
            'producer': str(user_a.id),
        }, format='json')
        r = client_a.get('/api/v1/programming/producer-assignments/')
        assert r.status_code == 200
        assert r.data['count'] == 1


@pytest.mark.django_db
class TestVenueHoldCRUD:
    def test_list(self, client_a, venue_hold_a):
        r = client_a.get('/api/v1/programming/venue-holds/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a, venue_a):
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-07-01',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
        }, format='json')
        assert r.status_code == 201
        assert VenueHold.objects.filter(organisation=org_a, hold_date='2026-07-01').exists()

    def test_create_emits_audit(self, client_a, context_a, venue_a):
        client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-07-02',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='venue_hold.created').exists()

    def test_create_without_context_returns_400(self, client_a, venue_a):
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'venue': str(venue_a.id),
            'hold_date': '2026-07-01',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_venue_returns_400(self, client_a, context_a, venue_b):
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_b.id),
            'hold_date': '2026-07-01',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, venue_hold_b):
        r = client_a.get(f'/api/v1/programming/venue-holds/{venue_hold_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestVenueHoldConflict:
    def test_full_day_conflict_returns_409(self, client_a, venue_hold_a, context_a, venue_a):
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': str(venue_hold_a.hold_date),
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
        }, format='json')
        assert r.status_code == 409

    def test_timed_overlap_returns_409(self, client_a, org_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=org_a,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 1),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(14, 0),
            end_time=datetime.time(16, 0),
        )
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-01',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
            'start_time': '15:00',
            'end_time': '17:00',
        }, format='json')
        assert r.status_code == 409

    def test_non_overlapping_times_succeed(self, client_a, org_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=org_a,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 9, 1),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        r = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-09-01',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
            'start_time': '13:00',
            'end_time': '15:00',
        }, format='json')
        assert r.status_code == 201


@pytest.mark.django_db
class TestCalendarSlotCRUD:
    def test_list(self, client_a, calendar_slot_a):
        r = client_a.get('/api/v1/programming/calendar-slots/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a, venue_a):
        r = client_a.post('/api/v1/programming/calendar-slots/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'date': '2026-07-20',
            'slot_type': 'rehearsal',
        }, format='json')
        assert r.status_code == 201
        assert CalendarSlot.objects.filter(organisation=org_a, date='2026-07-20').exists()

    def test_partial_update(self, client_a, calendar_slot_a):
        r = client_a.patch(
            f'/api/v1/programming/calendar-slots/{calendar_slot_a.id}/',
            {'is_confirmed': True}, format='json',
        )
        assert r.status_code == 200
        calendar_slot_a.refresh_from_db()
        assert calendar_slot_a.is_confirmed is True

    def test_cannot_reach_other_org(self, client_a, calendar_slot_b):
        r = client_a.get(f'/api/v1/programming/calendar-slots/{calendar_slot_b.id}/')
        assert r.status_code == 404

    def test_cross_org_context_returns_400(self, client_a, context_b, venue_a):
        r = client_a.post('/api/v1/programming/calendar-slots/', {
            'operating_context': str(context_b.id),
            'venue': str(venue_a.id),
            'date': '2026-07-20',
            'slot_type': 'rehearsal',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestCalendarIssueWorkflow:
    def test_raise_issue_against_workspace_and_hold(self, client_a, org_a, context_a, venue_hold_a, department_a, user_a):
        r = client_a.post('/api/v1/programming/calendar-issues/', {
            'title': 'Venue hold conflict',
            'description': 'Potential overlap with rehearsal.',
            'operating_context': str(context_a.id),
            'venue_hold': str(venue_hold_a.id),
            'department': str(department_a.id),
            'severity': 'high',
            'due_date': '2026-06-01',
        }, format='json')
        assert r.status_code == 201
        issue = CalendarIssue.objects.get(organisation=org_a)
        assert issue.status == 'open'
        assert issue.raised_by == user_a
        assert AuditEvent.objects.filter(event_type='calendar.issue_raised').exists()

    def test_raise_issue_against_slot(self, client_a, org_a, context_a, calendar_slot_a):
        r = client_a.post('/api/v1/programming/calendar-issues/', {
            'title': 'Slot needs confirmation',
            'operating_context': str(context_a.id),
            'calendar_slot': str(calendar_slot_a.id),
            'severity': 'medium',
        }, format='json')
        assert r.status_code == 201
        assert CalendarIssue.objects.filter(organisation=org_a, calendar_slot=calendar_slot_a).exists()

    def test_issue_cross_org_links_rejected(self, client_a, context_a, venue_hold_b):
        r = client_a.post('/api/v1/programming/calendar-issues/', {
            'title': 'Wrong tenant hold',
            'operating_context': str(context_a.id),
            'venue_hold': str(venue_hold_b.id),
            'severity': 'high',
        }, format='json')
        assert r.status_code == 400

    def test_issue_hold_must_match_workspace(self, client_a, org_a, context_a, site_a, venue_a, user_a):
        from apps.contexts.models import OperatingContext

        other_context = OperatingContext.objects.create(
            organisation=org_a,
            title='Other Same Tenant',
            context_type='production',
            status='draft',
            priority='medium',
            risk_level='low',
            site=site_a,
            owner=user_a,
        )
        hold = VenueHold.objects.create(
            organisation=org_a,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 7, 1),
            hold_type='provisional',
            purpose='rehearsal',
            held_by=user_a,
        )
        r = client_a.post('/api/v1/programming/calendar-issues/', {
            'title': 'Mismatched workspace',
            'operating_context': str(other_context.id),
            'venue_hold': str(hold.id),
            'severity': 'high',
        }, format='json')
        assert r.status_code == 400

    def test_progress_and_resolve_issue_are_audited(self, client_a, org_a, context_a, user_a):
        issue = CalendarIssue.objects.create(
            organisation=org_a,
            title='Calendar blocker',
            operating_context=context_a,
            severity='critical',
            raised_by=user_a,
        )
        r = client_a.post(
            f'/api/v1/programming/calendar-issues/{issue.id}/progress/',
            {'note': 'GM reviewing'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'in_progress'

        r = client_a.post(
            f'/api/v1/programming/calendar-issues/{issue.id}/resolve/',
            {'note': 'Moved rehearsal to studio'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'resolved'
        issue.refresh_from_db()
        assert issue.resolved_by == user_a
        assert issue.resolution_note == 'Moved rehearsal to studio'
        assert AuditEvent.objects.filter(event_type='calendar.issue_in_progress').exists()
        assert AuditEvent.objects.filter(event_type='calendar.issue_resolved').exists()

    def test_resolve_requires_note(self, client_a, org_a, context_a, user_a):
        issue = CalendarIssue.objects.create(
            organisation=org_a,
            title='Needs note',
            operating_context=context_a,
            severity='medium',
            raised_by=user_a,
        )
        r = client_a.post(
            f'/api/v1/programming/calendar-issues/{issue.id}/resolve/',
            {'note': ''}, format='json',
        )
        assert r.status_code == 400
        assert 'note' in r.data

    def test_cannot_reach_other_org_issue(self, client_a, org_b, context_b, user_b):
        issue = CalendarIssue.objects.create(
            organisation=org_b,
            title='Other org issue',
            operating_context=context_b,
            severity='medium',
            raised_by=user_b,
        )
        r = client_a.get(f'/api/v1/programming/calendar-issues/{issue.id}/')
        assert r.status_code == 404
