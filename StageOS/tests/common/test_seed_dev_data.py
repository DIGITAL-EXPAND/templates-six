from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User, UserType
from apps.artists.models import Artist, ArtistEngagement
from apps.contexts.models import OperatingContext
from apps.governance.models import CorrectiveAction, ExecutiveAction, KPI, Risk
from apps.marketing.models import Campaign
from apps.operations.models import FOHPlan
from apps.organisations.models import Organisation
from apps.programming.models import CalendarIssue, IntakeRequest, VenueHold
from apps.structure.models import Department, Site, Space, Venue
from apps.suppliers.models import Supplier, SupplierDocument
from apps.technical.models import TechnicalRider
from apps.ticketing.models import TicketingSetup
from apps.youth.models import Activity, AttendanceRecord, ConsentRecord, Session, YouthProject


PASSWORD = 'MoukangweTest123!'
ORG_SLUG = 'moukangwe-theatre'


def seed():
    call_command('seed_dev_data', stdout=StringIO())


@pytest.mark.django_db
def test_seed_dev_data_creates_moukangwe_uat_structure():
    seed()

    org = Organisation.objects.get(slug=ORG_SLUG)
    assert org.name == 'Moukangwe Theatre'
    assert Site.objects.filter(organisation=org, name='Moukangwe Theatre Complex').exists()

    venue_names = {
        'Tene Theatre',
        'Tumisho Theatre',
        'Koketso Theatre',
        'Dikeledi Restaurant',
        'Moukangwe Foyer',
        'Rehearsal Room',
    }
    assert set(Venue.objects.filter(organisation=org).values_list('name', flat=True)) >= venue_names
    assert set(Space.objects.filter(organisation=org).values_list('name', flat=True)) >= venue_names

    department_names = {
        'Executive Office',
        'Programming',
        'Marketing and Communications',
        'Technical and Stage Management',
        'FOH / Operations',
        'Contracts / Legal',
        'SCM / Finance',
        'Ticketing / Audience Coordination',
        'Youth Development',
        'Governance / M&E',
        'Hospitality / Restaurant Operations',
    }
    assert set(Department.objects.filter(organisation=org).values_list('name', flat=True)) >= department_names


@pytest.mark.django_db
def test_seed_dev_data_is_idempotent_for_core_records():
    seed()
    counts = {
        'users': User.objects.filter(organisation__slug=ORG_SLUG).count(),
        'departments': Department.objects.filter(organisation__slug=ORG_SLUG).count(),
        'venues': Venue.objects.filter(organisation__slug=ORG_SLUG).count(),
        'spaces': Space.objects.filter(organisation__slug=ORG_SLUG).count(),
        'workspaces': OperatingContext.objects.filter(organisation__slug=ORG_SLUG).count(),
        'intake': IntakeRequest.objects.filter(organisation__slug=ORG_SLUG).count(),
        'holds': VenueHold.objects.filter(organisation__slug=ORG_SLUG).count(),
    }

    seed()

    assert User.objects.filter(organisation__slug=ORG_SLUG).count() == counts['users']
    assert Department.objects.filter(organisation__slug=ORG_SLUG).count() == counts['departments']
    assert Venue.objects.filter(organisation__slug=ORG_SLUG).count() == counts['venues']
    assert Space.objects.filter(organisation__slug=ORG_SLUG).count() == counts['spaces']
    assert OperatingContext.objects.filter(organisation__slug=ORG_SLUG).count() == counts['workspaces']
    assert IntakeRequest.objects.filter(organisation__slug=ORG_SLUG).count() == counts['intake']
    assert VenueHold.objects.filter(organisation__slug=ORG_SLUG).count() == counts['holds']


@pytest.mark.django_db
def test_seed_dev_data_creates_expected_uat_users_and_roles():
    seed()
    org = Organisation.objects.get(slug=ORG_SLUG)

    expected_roles = {
        'admin@moukangwetheatre.test': UserType.INTERNAL_ADMIN,
        'ceo@moukangwetheatre.test': UserType.EXECUTIVE,
        'coo@moukangwetheatre.test': UserType.EXECUTIVE,
        'gm@moukangwetheatre.test': UserType.MANAGER,
        'board@moukangwetheatre.test': UserType.READ_ONLY,
        'readonly@moukangwetheatre.test': UserType.READ_ONLY,
        'client@moukangwetheatre.test': UserType.CLIENT_EXTERNAL,
        'supplier@moukangwetheatre.test': UserType.SUPPLIER_EXTERNAL,
        'artist@moukangwetheatre.test': UserType.ARTIST_EXTERNAL,
    }
    for email, user_type in expected_roles.items():
        user = User.objects.get(email=email)
        assert user.organisation == org
        assert user.is_active
        assert user.user_type == user_type
        assert user.check_password(PASSWORD)

    department_prefixes = [
        'programming',
        'marketing',
        'technical',
        'foh',
        'contracts',
        'scm',
        'ticketing',
        'youth',
        'governance',
        'hospitality',
    ]
    for prefix in department_prefixes:
        manager = User.objects.get(email=f'{prefix}.manager@moukangwetheatre.test')
        standard = User.objects.get(email=f'{prefix}.user@moukangwetheatre.test')
        assert manager.organisation == org
        assert manager.user_type == UserType.MANAGER
        assert manager.is_active
        assert standard.organisation == org
        assert standard.user_type == UserType.STAFF
        assert standard.is_active


@pytest.mark.django_db
def test_seed_dev_data_creates_demo_workspaces_and_department_records():
    seed()
    org = Organisation.objects.get(slug=ORG_SLUG)

    workspace_titles = {
        'The Main Stage Production',
        'Tumisho Theatre Comedy Night',
        'Koketso Theatre Workshop Series',
        'Moukangwe Youth Development Programme',
        'Stakeholder Reception',
    }
    assert set(OperatingContext.objects.filter(organisation=org).values_list('title', flat=True)) >= workspace_titles
    assert IntakeRequest.objects.filter(organisation=org, event_title='Moukangwe Community Concert').exists()
    assert CalendarIssue.objects.filter(organisation=org, title='Tene Theatre load-in clash check').exists()
    assert Campaign.objects.filter(organisation=org).exists()
    assert TechnicalRider.objects.filter(organisation=org).exists()
    assert FOHPlan.objects.filter(organisation=org).exists()
    assert Supplier.objects.filter(organisation=org).exists()
    assert SupplierDocument.objects.filter(organisation=org).exists()
    assert Artist.objects.filter(organisation=org).exists()
    assert ArtistEngagement.objects.filter(organisation=org).exists()
    assert TicketingSetup.objects.filter(organisation=org).exists()
    assert YouthProject.objects.filter(organisation=org).exists()
    assert Activity.objects.filter(organisation=org).exists()
    assert Session.objects.filter(organisation=org).exists()
    assert ConsentRecord.objects.filter(organisation=org).exists()
    assert AttendanceRecord.objects.filter(organisation=org).exists()
    assert Risk.objects.filter(organisation=org).exists()
    assert KPI.objects.filter(organisation=org).exists()
    assert CorrectiveAction.objects.filter(organisation=org).exists()
    assert ExecutiveAction.objects.filter(organisation=org).exists()


@pytest.mark.django_db
def test_seed_dev_data_login_token_works_for_representative_uat_users():
    seed()
    client = APIClient()
    emails = [
        'admin@moukangwetheatre.test',
        'ceo@moukangwetheatre.test',
        'gm@moukangwetheatre.test',
        'marketing.manager@moukangwetheatre.test',
        'board@moukangwetheatre.test',
        'client@moukangwetheatre.test',
    ]
    for email in emails:
        response = client.post('/api/token/', {'email': email, 'password': PASSWORD}, format='json')
        assert response.status_code == 200
        assert response.data['access']
