import pytest
from apps.structure.models import (
    Site, Venue, Space, Department, Position,
    VenueType, SpaceType, DepartmentType, PositionLevel,
)


@pytest.mark.django_db
class TestSiteModel:
    def test_create(self, org_a):
        site = Site.objects.create(
            organisation=org_a, name='Grand Theatre', code='GT',
            city='Pretoria', province='Gauteng', country='South Africa',
        )
        assert site.pk is not None
        assert str(site) == 'Grand Theatre (GT)'

    def test_is_active_defaults_true(self, org_a):
        site = Site.objects.create(
            organisation=org_a, name='S', code='S',
            city='C', province='P', country='ZA',
        )
        assert site.is_active is True


@pytest.mark.django_db
class TestVenueModel:
    def test_create(self, org_a, site_a):
        venue = Venue.objects.create(
            organisation=org_a, name='Lyric Theatre', site=site_a,
            venue_type=VenueType.PERFORMANCE, capacity=800,
        )
        assert venue.pk is not None
        assert str(venue) == f'Lyric Theatre — {site_a.name}'

    def test_default_venue_type(self, org_a, site_a):
        venue = Venue.objects.create(
            organisation=org_a, name='V', site=site_a, capacity=100,
        )
        assert venue.venue_type == VenueType.PERFORMANCE

    def test_all_venue_type_choices(self, org_a, site_a):
        for vtype in VenueType:
            v = Venue.objects.create(
                organisation=org_a, name=f'V-{vtype}', site=site_a,
                venue_type=vtype, capacity=10,
            )
            assert v.venue_type == vtype


@pytest.mark.django_db
class TestSpaceModel:
    def test_create(self, org_a, venue_a):
        space = Space.objects.create(
            organisation=org_a, name='Stage 1', venue=venue_a,
            space_type=SpaceType.STAGE, capacity=300,
        )
        assert space.pk is not None
        assert str(space) == f'Stage 1 — {venue_a.name}'

    def test_is_bookable_defaults_true(self, org_a, venue_a):
        space = Space.objects.create(
            organisation=org_a, name='S', venue=venue_a,
            space_type=SpaceType.FOYER, capacity=50,
        )
        assert space.is_bookable is True


@pytest.mark.django_db
class TestDepartmentModel:
    def test_create_org_wide(self, org_a):
        dept = Department.objects.create(
            organisation=org_a, name='Executive', code='EXEC',
            department_type=DepartmentType.EXECUTIVE,
        )
        assert dept.site is None
        assert str(dept) == 'Executive (EXEC)'

    def test_create_site_scoped(self, org_a, site_a):
        dept = Department.objects.create(
            organisation=org_a, name='Tech', code='TECH',
            department_type=DepartmentType.TECHNICAL, site=site_a,
        )
        assert dept.site == site_a

    def test_all_department_type_choices(self, org_a):
        for dtype in DepartmentType:
            d = Department.objects.create(
                organisation=org_a, name=f'D-{dtype}', code=dtype.value[:10],
                department_type=dtype,
            )
            assert d.department_type == dtype


@pytest.mark.django_db
class TestPositionModel:
    def test_create(self, org_a, department_a):
        pos = Position.objects.create(
            organisation=org_a, title='Stage Manager',
            department=department_a, level=PositionLevel.MANAGER,
        )
        assert pos.pk is not None
        assert str(pos) == f'Stage Manager — {department_a.name}'

    def test_reports_to_self_fk(self, org_a, department_a):
        manager = Position.objects.create(
            organisation=org_a, title='Head of Technical',
            department=department_a, level=PositionLevel.SENIOR_MANAGER,
        )
        report = Position.objects.create(
            organisation=org_a, title='Stage Manager',
            department=department_a, level=PositionLevel.MANAGER,
            reports_to=manager,
        )
        assert report.reports_to == manager
        assert manager.direct_reports.count() == 1

    def test_site_is_optional(self, org_a, department_a):
        pos = Position.objects.create(
            organisation=org_a, title='CEO',
            department=department_a, level=PositionLevel.EXECUTIVE,
        )
        assert pos.site is None

    def test_all_level_choices(self, org_a, department_a):
        for level in PositionLevel:
            p = Position.objects.create(
                organisation=org_a, title=f'P-{level}',
                department=department_a, level=level,
            )
            assert p.level == level
