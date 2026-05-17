import datetime

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from apps.programming.models import CalendarIssue, CalendarSlot, VenueHold
from apps.structure.models import Venue


def _api(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestCalendarConflictControls:
    def test_same_venue_overlapping_confirmed_hold_is_blocked(self, client_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 1),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(18, 0),
            end_time=datetime.time(22, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-01',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '19:00',
            'end_time': '21:00',
        }, format='json')

        assert response.status_code == 409
        assert CalendarIssue.objects.filter(title='Calendar conflict blocked').exists()
        assert AuditEvent.objects.filter(event_type='calendar.conflict_blocked').exists()

    def test_same_venue_non_overlapping_hold_is_allowed(self, client_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 2),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(11, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-02',
            'hold_type': 'confirmed',
            'purpose': 'rehearsal',
            'start_time': '11:00',
            'end_time': '13:00',
        }, format='json')

        assert response.status_code == 201

    def test_different_venue_same_time_is_allowed(self, client_a, context_a, site_a, venue_a, user_a):
        second_venue = Venue.objects.create(
            organisation=context_a.organisation,
            site=site_a,
            name='Second UAT Theatre',
            venue_type='performance',
            capacity=300,
        )
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 3),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(18, 0),
            end_time=datetime.time(22, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(second_venue.id),
            'hold_date': '2026-08-03',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '18:00',
            'end_time': '22:00',
        }, format='json')

        assert response.status_code == 201

    def test_confirmed_calendar_slot_overlapping_hold_is_blocked(self, client_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 4),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(18, 0),
            end_time=datetime.time(22, 0),
        )

        response = client_a.post('/api/v1/programming/calendar-slots/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'date': '2026-08-04',
            'slot_type': 'performance',
            'is_confirmed': True,
            'start_time': '19:00',
            'end_time': '21:00',
        }, format='json')

        assert response.status_code == 409

    def test_confirmed_hold_overlapping_calendar_slot_is_blocked(self, client_a, context_a, venue_a):
        CalendarSlot.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            date=datetime.date(2026, 8, 5),
            slot_type='performance',
            is_confirmed=True,
            start_time=datetime.time(18, 0),
            end_time=datetime.time(22, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-05',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '19:00',
            'end_time': '21:00',
        }, format='json')

        assert response.status_code == 409

    def test_provisional_overlap_creates_warning_issue(self, client_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 6),
            hold_type='provisional',
            purpose='rehearsal',
            held_by=user_a,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-06',
            'hold_type': 'provisional',
            'purpose': 'rehearsal',
            'start_time': '11:00',
            'end_time': '13:00',
        }, format='json')

        assert response.status_code == 201
        assert CalendarIssue.objects.filter(title='Provisional venue overlap warning').exists()

    def test_setup_and_strike_buffer_are_used_for_conflicts(self, client_a, context_a, venue_a, user_a):
        VenueHold.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            hold_date=datetime.date(2026, 8, 7),
            hold_type='confirmed',
            purpose='performance',
            held_by=user_a,
            start_time=datetime.time(19, 0),
            end_time=datetime.time(21, 0),
            setup_buffer_minutes=240,
            strike_buffer_minutes=60,
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-07',
            'hold_type': 'confirmed',
            'purpose': 'rehearsal',
            'start_time': '15:30',
            'end_time': '16:30',
        }, format='json')

        assert response.status_code == 409

    def test_blackout_slot_blocks_confirmed_hold(self, client_a, context_a, venue_a):
        CalendarSlot.objects.create(
            organisation=context_a.organisation,
            operating_context=context_a,
            venue=venue_a,
            date=datetime.date(2026, 8, 8),
            slot_type='blackout',
            is_confirmed=True,
            start_time=datetime.time(8, 0),
            end_time=datetime.time(18, 0),
        )

        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-08',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '12:00',
            'end_time': '14:00',
        }, format='json')

        assert response.status_code == 409

    def test_capacity_more_than_ten_percent_over_capacity_is_blocked(self, client_a, context_a, venue_a):
        response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context_a.id),
            'venue': str(venue_a.id),
            'hold_date': '2026-08-09',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '18:00',
            'end_time': '20:00',
            'expected_audience': 600,
        }, format='json')

        assert response.status_code == 409
        assert CalendarIssue.objects.filter(title='Venue capacity warning').exists()


@pytest.mark.django_db
class TestCalendarPermissionHardening:
    def test_marketing_manager_cannot_edit_programming_hold(self):
        call_command('seed_dev_data', verbosity=0)
        marketing = User.objects.get(email='marketing.manager@moukangwetheatre.test')
        context = OperatingContext.objects.filter(organisation=marketing.organisation).first()
        venue = Venue.objects.get(organisation=marketing.organisation, name='Tene Theatre')

        response = _api(marketing).post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context.id),
            'venue': str(venue.id),
            'hold_date': '2026-09-01',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '18:00',
            'end_time': '22:00',
        }, format='json')

        assert response.status_code == 403

    def test_programming_manager_can_edit_programming_hold(self):
        call_command('seed_dev_data', verbosity=0)
        programming = User.objects.get(email='programming.manager@moukangwetheatre.test')
        context = OperatingContext.objects.filter(organisation=programming.organisation).first()
        venue = Venue.objects.get(organisation=programming.organisation, name='Tene Theatre')

        response = _api(programming).post('/api/v1/programming/venue-holds/', {
            'operating_context': str(context.id),
            'venue': str(venue.id),
            'hold_date': '2026-09-02',
            'hold_type': 'confirmed',
            'purpose': 'performance',
            'start_time': '18:00',
            'end_time': '22:00',
        }, format='json')

        assert response.status_code == 201
