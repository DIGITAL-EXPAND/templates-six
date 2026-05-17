import pytest
from apps.structure.models import Site, Venue, Space, Department, Position


@pytest.mark.django_db
class TestSiteAPI:
    def test_list(self, client_a, site_a):
        r = client_a.get('/api/v1/sites/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a):
        r = client_a.post('/api/v1/sites/', {
            'name': 'New Site', 'code': 'NS',
            'city': 'Durban', 'province': 'KZN', 'country': 'South Africa',
        }, format='json')
        assert r.status_code == 201
        assert Site.objects.filter(name='New Site', organisation=org_a).exists()

    def test_organisation_set_automatically(self, client_a, org_a):
        r = client_a.post('/api/v1/sites/', {
            'name': 'Auto Org', 'code': 'AO',
            'city': 'PE', 'province': 'EC', 'country': 'South Africa',
        }, format='json')
        assert r.status_code == 201
        site = Site.objects.get(name='Auto Org')
        assert site.organisation == org_a

    def test_retrieve(self, client_a, site_a):
        r = client_a.get(f'/api/v1/sites/{site_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == site_a.name

    def test_partial_update(self, client_a, site_a):
        r = client_a.patch(f'/api/v1/sites/{site_a.id}/', {'name': 'Updated'}, format='json')
        assert r.status_code == 200
        site_a.refresh_from_db()
        assert site_a.name == 'Updated'

    def test_delete(self, client_a, org_a):
        site = Site.objects.create(
            organisation=org_a, name='Temp', code='TMP',
            city='X', province='Y', country='Z',
        )
        r = client_a.delete(f'/api/v1/sites/{site.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org_site(self, client_a, site_b):
        r = client_a.get(f'/api/v1/sites/{site_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/sites/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestVenueAPI:
    def test_list(self, client_a, venue_a):
        r = client_a.get('/api/v1/venues/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, site_a):
        r = client_a.post('/api/v1/venues/', {
            'name': 'Rehearsal Room', 'site': str(site_a.id),
            'venue_type': 'rehearsal', 'capacity': 50,
        }, format='json')
        assert r.status_code == 201
        assert Venue.objects.filter(name='Rehearsal Room', organisation=org_a).exists()

    def test_create_rejected_with_other_org_site(self, client_a, site_b):
        r = client_a.post('/api/v1/venues/', {
            'name': 'Bad Venue', 'site': str(site_b.id),
            'venue_type': 'performance', 'capacity': 100,
        }, format='json')
        assert r.status_code == 400

    def test_response_includes_site_name(self, client_a, venue_a, site_a):
        r = client_a.get(f'/api/v1/venues/{venue_a.id}/')
        assert r.status_code == 200
        assert r.data['site_name'] == site_a.name

    def test_cannot_reach_other_org_venue(self, client_a, venue_b):
        r = client_a.get(f'/api/v1/venues/{venue_b.id}/')
        assert r.status_code == 404

    def test_partial_update(self, client_a, venue_a):
        r = client_a.patch(f'/api/v1/venues/{venue_a.id}/', {'capacity': 600}, format='json')
        assert r.status_code == 200
        venue_a.refresh_from_db()
        assert venue_a.capacity == 600


@pytest.mark.django_db
class TestSpaceAPI:
    def test_list(self, client_a, org_a, venue_a):
        from apps.structure.models import Space
        Space.objects.create(
            organisation=org_a, name='Stage 1', venue=venue_a,
            space_type='stage', capacity=300,
        )
        r = client_a.get('/api/v1/spaces/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, venue_a):
        r = client_a.post('/api/v1/spaces/', {
            'name': 'Foyer', 'venue': str(venue_a.id),
            'space_type': 'foyer', 'capacity': 200,
        }, format='json')
        assert r.status_code == 201
        assert Space.objects.filter(name='Foyer', organisation=org_a).exists()

    def test_create_rejected_with_other_org_venue(self, client_a, venue_b):
        r = client_a.post('/api/v1/spaces/', {
            'name': 'Bad Space', 'venue': str(venue_b.id),
            'space_type': 'stage', 'capacity': 100,
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org_space(self, client_a, org_b, venue_b):
        space = Space.objects.create(
            organisation=org_b, name='Other Space', venue=venue_b,
            space_type='studio', capacity=50,
        )
        r = client_a.get(f'/api/v1/spaces/{space.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestDepartmentAPI:
    def test_list(self, client_a, department_a):
        r = client_a.get('/api/v1/departments/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create_org_wide(self, client_a, org_a):
        r = client_a.post('/api/v1/departments/', {
            'name': 'Finance', 'code': 'FIN', 'department_type': 'finance',
        }, format='json')
        assert r.status_code == 201
        assert Department.objects.filter(name='Finance', organisation=org_a).exists()

    def test_create_site_scoped(self, client_a, org_a, site_a):
        r = client_a.post('/api/v1/departments/', {
            'name': 'FOH', 'code': 'FOH',
            'department_type': 'operations', 'site': str(site_a.id),
        }, format='json')
        assert r.status_code == 201

    def test_create_rejected_with_other_org_site(self, client_a, site_b):
        r = client_a.post('/api/v1/departments/', {
            'name': 'Bad Dept', 'code': 'BD',
            'department_type': 'technical', 'site': str(site_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org_department(self, client_a, department_b):
        r = client_a.get(f'/api/v1/departments/{department_b.id}/')
        assert r.status_code == 404

    def test_partial_update(self, client_a, department_a):
        r = client_a.patch(f'/api/v1/departments/{department_a.id}/', {'name': 'Updated Tech'}, format='json')
        assert r.status_code == 200
        department_a.refresh_from_db()
        assert department_a.name == 'Updated Tech'


@pytest.mark.django_db
class TestPositionAPI:
    def test_list(self, client_a, org_a, department_a):
        Position.objects.create(
            organisation=org_a, title='Stage Manager',
            department=department_a, level='manager',
        )
        r = client_a.get('/api/v1/positions/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, department_a):
        r = client_a.post('/api/v1/positions/', {
            'title': 'Lighting Tech', 'department': str(department_a.id),
            'level': 'officer',
        }, format='json')
        assert r.status_code == 201
        assert Position.objects.filter(title='Lighting Tech', organisation=org_a).exists()

    def test_create_with_reports_to(self, client_a, org_a, department_a):
        manager = Position.objects.create(
            organisation=org_a, title='HOD',
            department=department_a, level='senior_manager',
        )
        r = client_a.post('/api/v1/positions/', {
            'title': 'Tech Officer', 'department': str(department_a.id),
            'level': 'officer', 'reports_to': str(manager.id),
        }, format='json')
        assert r.status_code == 201
        pos = Position.objects.get(title='Tech Officer')
        assert pos.reports_to == manager

    def test_create_rejected_with_other_org_department(self, client_a, department_b):
        r = client_a.post('/api/v1/positions/', {
            'title': 'Bad Pos', 'department': str(department_b.id),
            'level': 'staff',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org_position(self, client_a, org_b, department_b):
        pos = Position.objects.create(
            organisation=org_b, title='Other Pos',
            department=department_b, level='officer',
        )
        r = client_a.get(f'/api/v1/positions/{pos.id}/')
        assert r.status_code == 404

    def test_response_includes_department_name(self, client_a, org_a, department_a):
        pos = Position.objects.create(
            organisation=org_a, title='Coord',
            department=department_a, level='coordinator',
        )
        r = client_a.get(f'/api/v1/positions/{pos.id}/')
        assert r.status_code == 200
        assert r.data['department_name'] == department_a.name
