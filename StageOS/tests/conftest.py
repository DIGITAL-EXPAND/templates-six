import pytest
from rest_framework.test import APIClient
from apps.organisations.models import Organisation
from apps.accounts.models import User


@pytest.fixture
def org_a(db):
    return Organisation.objects.create(name='Org A', slug='org-a')


@pytest.fixture
def org_b(db):
    return Organisation.objects.create(name='Org B', slug='org-b')


@pytest.fixture
def user_a(db, org_a):
    return User.objects.create_user(
        email='user-a@example.com',
        password='testpass123',
        organisation=org_a,
        user_type='manager',
    )


@pytest.fixture
def user_b(db, org_b):
    return User.objects.create_user(
        email='user-b@example.com',
        password='testpass123',
        organisation=org_b,
        user_type='manager',
    )


@pytest.fixture
def client_a(user_a):
    client = APIClient()
    client.force_authenticate(user=user_a)
    return client


@pytest.fixture
def client_b(user_b):
    client = APIClient()
    client.force_authenticate(user=user_b)
    return client


# ── Structure fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def site_a(db, org_a):
    from apps.structure.models import Site
    return Site.objects.create(
        organisation=org_a,
        name='Site A',
        code='SA',
        city='Johannesburg',
        province='Gauteng',
        country='South Africa',
    )


@pytest.fixture
def site_b(db, org_b):
    from apps.structure.models import Site
    return Site.objects.create(
        organisation=org_b,
        name='Site B',
        code='SB',
        city='Cape Town',
        province='Western Cape',
        country='South Africa',
    )


@pytest.fixture
def venue_a(db, org_a, site_a):
    from apps.structure.models import Venue
    return Venue.objects.create(
        organisation=org_a,
        name='Main Theatre',
        site=site_a,
        venue_type='performance',
        capacity=500,
    )


@pytest.fixture
def venue_b(db, org_b, site_b):
    from apps.structure.models import Venue
    return Venue.objects.create(
        organisation=org_b,
        name='Studio Theatre',
        site=site_b,
        venue_type='performance',
        capacity=100,
    )


@pytest.fixture
def department_a(db, org_a):
    from apps.structure.models import Department
    return Department.objects.create(
        organisation=org_a,
        name='Technical Department',
        code='TECH',
        department_type='technical',
    )


@pytest.fixture
def department_b(db, org_b):
    from apps.structure.models import Department
    return Department.objects.create(
        organisation=org_b,
        name='Marketing Department',
        code='MKTG',
        department_type='marketing',
    )


# ── Context fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def context_a(db, org_a, site_a, user_a):
    from apps.contexts.models import OperatingContext
    return OperatingContext.objects.create(
        organisation=org_a,
        title='Production A',
        context_type='production',
        status='draft',
        priority='medium',
        risk_level='low',
        site=site_a,
        owner=user_a,
    )


@pytest.fixture
def context_b(db, org_b, site_b, user_b):
    from apps.contexts.models import OperatingContext
    return OperatingContext.objects.create(
        organisation=org_b,
        title='Production B',
        context_type='production',
        status='draft',
        priority='medium',
        risk_level='low',
        site=site_b,
        owner=user_b,
    )


# ── Task fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def task_a(db, org_a, context_a):
    from apps.tasks.models import Task
    return Task.objects.create(
        organisation=org_a,
        operating_context=context_a,
        title='Task A',
        priority='medium',
        status='open',
    )


@pytest.fixture
def task_b(db, org_b, context_b):
    from apps.tasks.models import Task
    return Task.objects.create(
        organisation=org_b,
        operating_context=context_b,
        title='Task B',
        priority='medium',
        status='open',
    )


# ── Document fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def document_a(db, org_a, context_a, user_a):
    from apps.documents.models import Document
    return Document.objects.create(
        organisation=org_a,
        operating_context=context_a,
        title='Document A',
        document_type='brief',
        file_name='brief_a.pdf',
        file_size=131072,
        uploaded_by=user_a,
    )


@pytest.fixture
def document_b(db, org_b, context_b, user_b):
    from apps.documents.models import Document
    return Document.objects.create(
        organisation=org_b,
        operating_context=context_b,
        title='Document B',
        document_type='plan',
        file_name='plan_b.pdf',
        file_size=262144,
        uploaded_by=user_b,
    )


# ── Programming fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def intake_review_a(db, org_a, context_a, user_a):
    import datetime
    from apps.programming.models import IntakeReview
    return IntakeReview.objects.create(
        organisation=org_a,
        operating_context=context_a,
        reviewed_by=user_a,
        review_date=datetime.date(2026, 5, 1),
        recommendation='approve',
        status='pending',
    )


@pytest.fixture
def intake_review_b(db, org_b, context_b, user_b):
    import datetime
    from apps.programming.models import IntakeReview
    return IntakeReview.objects.create(
        organisation=org_b,
        operating_context=context_b,
        reviewed_by=user_b,
        review_date=datetime.date(2026, 5, 1),
        recommendation='approve',
        status='pending',
    )


@pytest.fixture
def venue_hold_a(db, org_a, context_a, venue_a, user_a):
    import datetime
    from apps.programming.models import VenueHold
    return VenueHold.objects.create(
        organisation=org_a,
        operating_context=context_a,
        venue=venue_a,
        hold_date=datetime.date(2026, 6, 10),
        hold_type='confirmed',
        purpose='performance',
        held_by=user_a,
    )


@pytest.fixture
def venue_hold_b(db, org_b, context_b, venue_b, user_b):
    import datetime
    from apps.programming.models import VenueHold
    return VenueHold.objects.create(
        organisation=org_b,
        operating_context=context_b,
        venue=venue_b,
        hold_date=datetime.date(2026, 6, 10),
        hold_type='confirmed',
        purpose='performance',
        held_by=user_b,
    )


@pytest.fixture
def calendar_slot_a(db, org_a, context_a, venue_a):
    import datetime
    from apps.programming.models import CalendarSlot
    return CalendarSlot.objects.create(
        organisation=org_a,
        operating_context=context_a,
        venue=venue_a,
        date=datetime.date(2026, 6, 15),
        slot_type='performance',
        is_confirmed=False,
    )


@pytest.fixture
def calendar_slot_b(db, org_b, context_b, venue_b):
    import datetime
    from apps.programming.models import CalendarSlot
    return CalendarSlot.objects.create(
        organisation=org_b,
        operating_context=context_b,
        venue=venue_b,
        date=datetime.date(2026, 6, 15),
        slot_type='performance',
        is_confirmed=False,
    )


# ── Marketing fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def campaign_a(db, org_a, context_a, user_a):
    from apps.marketing.models import Campaign
    return Campaign.objects.create(
        organisation=org_a,
        operating_context=context_a,
        campaign_level='standard',
        status='planning',
        owner=user_a,
    )


@pytest.fixture
def campaign_b(db, org_b, context_b, user_b):
    from apps.marketing.models import Campaign
    return Campaign.objects.create(
        organisation=org_b,
        operating_context=context_b,
        campaign_level='basic',
        status='planning',
        owner=user_b,
    )


@pytest.fixture
def deliverable_a(db, org_a, campaign_a):
    import datetime
    from apps.marketing.models import CampaignDeliverable
    return CampaignDeliverable.objects.create(
        organisation=org_a,
        campaign=campaign_a,
        deliverable_type='poster_design',
        title='Main Poster',
        owner_name='Design Team',
        due_date=datetime.date(2026, 5, 20),
    )


@pytest.fixture
def deliverable_b(db, org_b, campaign_b):
    import datetime
    from apps.marketing.models import CampaignDeliverable
    return CampaignDeliverable.objects.create(
        organisation=org_b,
        campaign=campaign_b,
        deliverable_type='pr_plan',
        title='PR Plan B',
        owner_name='PR Team',
        due_date=datetime.date(2026, 5, 25),
    )


# ── Technical fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def rider_a(db, org_a, context_a):
    from apps.technical.models import TechnicalRider
    return TechnicalRider.objects.create(
        organisation=org_a,
        operating_context=context_a,
        status='draft',
    )


@pytest.fixture
def rider_b(db, org_b, context_b):
    from apps.technical.models import TechnicalRider
    return TechnicalRider.objects.create(
        organisation=org_b,
        operating_context=context_b,
        status='draft',
    )


# ── Operations fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def foh_plan_a(db, org_a, context_a):
    from apps.operations.models import FOHPlan
    return FOHPlan.objects.create(
        organisation=org_a,
        operating_context=context_a,
        ushers=5,
        security=3,
        status='planning',
    )


@pytest.fixture
def foh_plan_b(db, org_b, context_b):
    from apps.operations.models import FOHPlan
    return FOHPlan.objects.create(
        organisation=org_b,
        operating_context=context_b,
        ushers=4,
        security=2,
        status='planning',
    )


# ── Contracts fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def contract_template_a(db, org_a):
    from apps.contracts.models import ContractTemplate
    return ContractTemplate.objects.create(
        organisation=org_a,
        name='Artist Performance Template',
        contract_type='artist_performance',
        is_active=True,
        version=1,
    )


@pytest.fixture
def contract_template_b(db, org_b):
    from apps.contracts.models import ContractTemplate
    return ContractTemplate.objects.create(
        organisation=org_b,
        name='Venue Hire Template B',
        contract_type='venue_hire',
        is_active=True,
        version=1,
    )


@pytest.fixture
def contract_a(db, org_a, context_a):
    from apps.contracts.models import ContractRecord
    return ContractRecord.objects.create(
        organisation=org_a,
        operating_context=context_a,
        contract_type='artist_performance',
        counterparty_name='Big Artist',
        counterparty_type='artist',
        status='draft',
    )


@pytest.fixture
def contract_b(db, org_b, context_b):
    from apps.contracts.models import ContractRecord
    return ContractRecord.objects.create(
        organisation=org_b,
        operating_context=context_b,
        contract_type='venue_hire',
        counterparty_name='Venue B Owner',
        counterparty_type='partner',
        status='draft',
    )


@pytest.fixture
def signature_a(db, org_a, contract_a):
    from apps.contracts.models import SignatureRecord
    return SignatureRecord.objects.create(
        organisation=org_a,
        contract=contract_a,
        signatory_name='John Doe',
        signatory_role='CEO',
        signature_type='wet',
        signature_order=1,
    )


@pytest.fixture
def signature_b(db, org_b, contract_b):
    from apps.contracts.models import SignatureRecord
    return SignatureRecord.objects.create(
        organisation=org_b,
        contract=contract_b,
        signatory_name='Jane Smith',
        signatory_role='Director',
        signature_type='electronic',
        signature_order=1,
    )


# ── Supplier fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def supplier_a(db, org_a):
    from apps.suppliers.models import Supplier
    return Supplier.objects.create(
        organisation=org_a,
        name='Lights & Sound Co',
        category='Technical',
        status='documents_incomplete',
    )


@pytest.fixture
def supplier_b(db, org_b):
    from apps.suppliers.models import Supplier
    return Supplier.objects.create(
        organisation=org_b,
        name='Supplier B Corp',
        category='Marketing',
        status='documents_incomplete',
    )


@pytest.fixture
def supplier_engagement_a(db, org_a, supplier_a, context_a):
    from apps.suppliers.models import SupplierEngagement
    return SupplierEngagement.objects.create(
        organisation=org_a,
        supplier=supplier_a,
        operating_context=context_a,
        role='Lighting provider',
        status='proposed',
    )


@pytest.fixture
def supplier_engagement_b(db, org_b, supplier_b, context_b):
    from apps.suppliers.models import SupplierEngagement
    return SupplierEngagement.objects.create(
        organisation=org_b,
        supplier=supplier_b,
        operating_context=context_b,
        role='Security',
        status='proposed',
    )


# ── Artist fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def artist_a(db, org_a):
    from apps.artists.models import Artist
    return Artist.objects.create(
        organisation=org_a,
        legal_name='Alice Performer',
        professional_name='Alice P',
        discipline='Theatre',
        status='documents_incomplete',
    )


@pytest.fixture
def artist_b(db, org_b):
    from apps.artists.models import Artist
    return Artist.objects.create(
        organisation=org_b,
        legal_name='Bob Artist',
        discipline='Dance',
        status='documents_incomplete',
    )


@pytest.fixture
def artist_engagement_a(db, org_a, artist_a, context_a):
    from apps.artists.models import ArtistEngagement
    return ArtistEngagement.objects.create(
        organisation=org_a,
        artist=artist_a,
        operating_context=context_a,
        role='Lead Actor',
        status='proposed',
    )


@pytest.fixture
def artist_engagement_b(db, org_b, artist_b, context_b):
    from apps.artists.models import ArtistEngagement
    return ArtistEngagement.objects.create(
        organisation=org_b,
        artist=artist_b,
        operating_context=context_b,
        role='Dancer',
        status='proposed',
    )


# ── Youth fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def youth_context_a(db, org_a, site_a, user_a):
    from apps.contexts.models import OperatingContext
    return OperatingContext.objects.create(
        organisation=org_a,
        title='Youth Orchestra Project A',
        context_type='youth_project',
        status='draft',
        priority='medium',
        risk_level='low',
        site=site_a,
        owner=user_a,
    )


@pytest.fixture
def youth_context_b(db, org_b, site_b, user_b):
    from apps.contexts.models import OperatingContext
    return OperatingContext.objects.create(
        organisation=org_b,
        title='Youth Theatre Project B',
        context_type='youth_project',
        status='draft',
        priority='medium',
        risk_level='low',
        site=site_b,
        owner=user_b,
    )


@pytest.fixture
def youth_project_a(db, org_a, youth_context_a):
    from apps.youth.models import YouthProject
    return YouthProject.objects.create(
        organisation=org_a,
        operating_context=youth_context_a,
        target_learners=50,
        target_schools=5,
        status='planning',
    )


@pytest.fixture
def youth_project_b(db, org_b, youth_context_b):
    from apps.youth.models import YouthProject
    return YouthProject.objects.create(
        organisation=org_b,
        operating_context=youth_context_b,
        target_learners=30,
        target_schools=3,
        status='planning',
    )


@pytest.fixture
def activity_a(db, org_a, youth_project_a):
    from apps.youth.models import Activity
    return Activity.objects.create(
        organisation=org_a,
        youth_project=youth_project_a,
        name='Violin Rehearsal',
        activity_type='sectional_rehearsal',
        recurrence='weekly',
    )


@pytest.fixture
def activity_b(db, org_b, youth_project_b):
    from apps.youth.models import Activity
    return Activity.objects.create(
        organisation=org_b,
        youth_project=youth_project_b,
        name='Acting Class',
        activity_type='class_session',
        recurrence='weekly',
    )


@pytest.fixture
def session_a(db, org_a, activity_a):
    import datetime
    from apps.youth.models import Session
    return Session.objects.create(
        organisation=org_a,
        activity=activity_a,
        session_date=datetime.date(2026, 6, 1),
        status='scheduled',
    )


@pytest.fixture
def session_b(db, org_b, activity_b):
    import datetime
    from apps.youth.models import Session
    return Session.objects.create(
        organisation=org_b,
        activity=activity_b,
        session_date=datetime.date(2026, 6, 1),
        status='scheduled',
    )


@pytest.fixture
def learner_group_a(db, org_a, youth_project_a):
    from apps.youth.models import LearnerGroup
    return LearnerGroup.objects.create(
        organisation=org_a,
        youth_project=youth_project_a,
        name='String Section',
    )


@pytest.fixture
def learner_group_b(db, org_b, youth_project_b):
    from apps.youth.models import LearnerGroup
    return LearnerGroup.objects.create(
        organisation=org_b,
        youth_project=youth_project_b,
        name='Group B',
    )


# ── Workflow fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def workflow_template_a(db, org_a):
    from apps.workflows.models import WorkflowTemplate
    return WorkflowTemplate.objects.create(
        organisation=org_a,
        name='Production Workflow A',
        context_type='production',
    )


@pytest.fixture
def workflow_template_b(db, org_b):
    from apps.workflows.models import WorkflowTemplate
    return WorkflowTemplate.objects.create(
        organisation=org_b,
        name='Production Workflow B',
        context_type='production',
    )


# ── Approval fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def approval_route_a(db, org_a):
    from apps.approvals.models import ApprovalRoute
    return ApprovalRoute.objects.create(
        organisation=org_a,
        name='Standard Route A',
    )


@pytest.fixture
def approval_route_b(db, org_b):
    from apps.approvals.models import ApprovalRoute
    return ApprovalRoute.objects.create(
        organisation=org_b,
        name='Standard Route B',
    )


# ── Ticketing fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def ticketing_setup_a(db, org_a, context_a, user_a):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_a, user_a, {
        'provider': 'webtickets',
        'tickets_available': 500,
    })


@pytest.fixture
def ticketing_setup_b(db, org_b, context_b, user_b):
    from apps.ticketing.services import create_ticketing_setup
    return create_ticketing_setup(context_b, user_b, {
        'provider': 'computicket',
        'tickets_available': 200,
    })


# ── Governance fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def kpi_a(db, org_a):
    from apps.governance.models import KPI
    return KPI.objects.create(
        organisation=org_a,
        name='Attendance Rate A',
        target_value='80.00',
        unit='%',
        reporting_period='quarterly',
    )


@pytest.fixture
def kpi_b(db, org_b):
    from apps.governance.models import KPI
    return KPI.objects.create(
        organisation=org_b,
        name='Attendance Rate B',
        target_value='75.00',
        unit='%',
        reporting_period='monthly',
    )


@pytest.fixture
def risk_a(db, org_a, user_a):
    from apps.governance.models import Risk
    return Risk.objects.create(
        organisation=org_a,
        title='Budget Risk A',
        risk_level='high',
        owner=user_a,
    )


@pytest.fixture
def risk_b(db, org_b, user_b):
    from apps.governance.models import Risk
    return Risk.objects.create(
        organisation=org_b,
        title='Budget Risk B',
        risk_level='medium',
        owner=user_b,
    )


# ── Integration fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def integration_provider_a(db, org_a):
    from apps.integrations.models import IntegrationProvider
    return IntegrationProvider.objects.create(
        organisation=org_a,
        name='Webtickets',
        provider_type='ticketing',
        is_enabled=True,
    )


@pytest.fixture
def integration_provider_b(db, org_b):
    from apps.integrations.models import IntegrationProvider
    return IntegrationProvider.objects.create(
        organisation=org_b,
        name='Computicket',
        provider_type='ticketing',
        is_enabled=False,
    )


@pytest.fixture
def external_reference_a(db, org_a, integration_provider_a, context_a):
    from apps.integrations.models import ExternalReference
    return ExternalReference.objects.create(
        organisation=org_a,
        provider=integration_provider_a,
        operating_context=context_a,
        reference_type='event_id',
        external_id='EVT-001',
    )


@pytest.fixture
def external_reference_b(db, org_b, integration_provider_b, context_b):
    from apps.integrations.models import ExternalReference
    return ExternalReference.objects.create(
        organisation=org_b,
        provider=integration_provider_b,
        operating_context=context_b,
        reference_type='event_id',
        external_id='EVT-002',
    )
