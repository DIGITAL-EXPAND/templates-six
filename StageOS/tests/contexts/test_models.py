import pytest
from decimal import Decimal
from apps.contexts.models import OperatingContext, TicketingProvider, CampaignLevel
from common.enums import ContextType, ContextStatus, Priority, RiskLevel


@pytest.mark.django_db
class TestOperatingContextModel:
    def test_create_minimal(self, org_a, site_a, user_a):
        ctx = OperatingContext.objects.create(
            organisation=org_a,
            title='Macbeth',
            site=site_a,
            owner=user_a,
        )
        assert ctx.pk is not None
        assert str(ctx) == 'Macbeth [Draft]'

    def test_create_full(self, org_a, site_a, venue_a, department_a, user_a):
        from apps.structure.models import Space
        space = Space.objects.create(
            organisation=org_a, name='Stage 1', venue=venue_a,
            space_type='stage', capacity=300,
        )
        ctx = OperatingContext.objects.create(
            organisation=org_a,
            title='Festival 2025',
            context_type=ContextType.FESTIVAL,
            status=ContextStatus.CONFIRMED,
            priority=Priority.HIGH,
            risk_level=RiskLevel.MEDIUM,
            synopsis='Annual arts festival',
            site=site_a,
            venue=venue_a,
            primary_space=space,
            department=department_a,
            owner=user_a,
            opening_date='2025-06-01',
            closing_date='2025-06-15',
            budget=Decimal('500000.00'),
            ticketing_provider=TicketingProvider.WEBTICKETS,
            campaign_level=CampaignLevel.FULL,
            kpi_link='KPI-001',
            readiness_score=75,
            is_public=True,
        )
        assert ctx.context_type == ContextType.FESTIVAL
        assert ctx.status == ContextStatus.CONFIRMED
        assert ctx.budget == Decimal('500000.00')
        assert ctx.is_public is True

    def test_defaults(self, org_a, site_a, user_a):
        ctx = OperatingContext.objects.create(
            organisation=org_a, title='T', site=site_a, owner=user_a,
        )
        assert ctx.status == ContextStatus.DRAFT
        assert ctx.priority == Priority.MEDIUM
        assert ctx.risk_level == RiskLevel.LOW
        assert ctx.readiness_score == 0
        assert ctx.is_public is False
        assert ctx.budget == Decimal('0')
        assert ctx.actual_spend == Decimal('0')

    def test_timestamps_auto_set(self, org_a, site_a, user_a):
        ctx = OperatingContext.objects.create(
            organisation=org_a, title='T', site=site_a, owner=user_a,
        )
        assert ctx.created_at is not None
        assert ctx.updated_at is not None

    def test_parent_context_self_fk(self, org_a, site_a, user_a):
        festival = OperatingContext.objects.create(
            organisation=org_a, title='Festival',
            context_type=ContextType.FESTIVAL, site=site_a, owner=user_a,
        )
        sub = OperatingContext.objects.create(
            organisation=org_a, title='Sub-Event',
            context_type=ContextType.PRODUCTION, site=site_a, owner=user_a,
            parent_context=festival,
        )
        assert sub.parent_context == festival
        assert festival.sub_contexts.count() == 1
        assert festival.sub_contexts.first() == sub

    def test_ordering_newest_first(self, org_a, site_a, user_a):
        c1 = OperatingContext.objects.create(
            organisation=org_a, title='First', site=site_a, owner=user_a,
        )
        c2 = OperatingContext.objects.create(
            organisation=org_a, title='Second', site=site_a, owner=user_a,
        )
        all_contexts = list(OperatingContext.objects.filter(organisation=org_a))
        assert all_contexts[0].pk == c2.pk

    def test_readiness_score_validates_range(self, org_a, site_a, user_a):
        from django.core.exceptions import ValidationError
        ctx = OperatingContext(
            organisation=org_a, title='T', site=site_a, owner=user_a,
            readiness_score=150,
        )
        with pytest.raises(ValidationError):
            ctx.full_clean()

    def test_all_context_type_choices(self, org_a, site_a, user_a):
        for ctype in ContextType:
            c = OperatingContext.objects.create(
                organisation=org_a, title=f'C-{ctype}', site=site_a,
                owner=user_a, context_type=ctype,
            )
            assert c.context_type == ctype

    def test_all_status_choices(self, org_a, site_a, user_a):
        for s in ContextStatus:
            c = OperatingContext.objects.create(
                organisation=org_a, title=f'S-{s}', site=site_a,
                owner=user_a, status=s,
            )
            assert c.status == s
