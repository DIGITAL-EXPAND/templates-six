from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User, UserType
from apps.approvals.models import ApprovalRequest, ApprovalRoute, ApprovalStep
from apps.artists.models import Artist, ArtistDocument, ArtistEngagement
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from apps.contracts.models import ContractRecord, ContractTemplate
from apps.documents.models import Document, EvidenceSubmission
from apps.governance.models import CorrectiveAction, ExecutiveAction, KPI, KPIEvidence, Risk
from apps.marketing.models import Campaign, CampaignDeliverable
from apps.operations.models import FOHPlan, Incident, ShowDayChecklist
from apps.organisations.models import Organisation
from apps.programming.models import CalendarIssue, CalendarSlot, IntakeRequest, VenueHold
from apps.structure.models import (
    ApprovalPolicy,
    AuthorityLevel,
    Department,
    EvidenceRule,
    ModuleActivation,
    OrganisationOperatingModel,
    Position,
    PositionLevel,
    Site,
    SOPTemplate,
    Space,
    UserDepartmentMembership,
    Venue,
)
from apps.suppliers.models import PaymentPack, Supplier, SupplierDocument, SupplierEngagement
from apps.tasks.models import Notification, Task
from apps.technical.models import CrewRequirement, EquipmentRequirement, TechnicalRider
from apps.ticketing.models import SalesImport, TicketingSetup
from apps.youth.models import (
    Activity,
    Assessment,
    AttendanceRecord,
    ConsentRecord,
    FacilitatorAssignment,
    LearnerGroup,
    Session,
    ShowcaseOutput,
    YouthProject,
)


UAT_PASSWORD = 'MoukangweTest123!'


class Command(BaseCommand):
    help = 'Seed idempotent Moukangwe Theatre UAT data for StageOS.'

    def handle(self, *args, **options):
        today = date.today()

        org, _ = Organisation.objects.update_or_create(
            slug='moukangwe-theatre',
            defaults={'name': 'Moukangwe Theatre', 'is_active': True},
        )
        site, _ = Site.objects.update_or_create(
            organisation=org,
            code='MTC',
            defaults={
                'name': 'Moukangwe Theatre Complex',
                'address': 'Moukangwe Theatre Complex',
                'city': 'Johannesburg',
                'province': 'Gauteng',
                'country': 'South Africa',
                'is_active': True,
            },
        )

        venues = self._seed_venues(org, site)
        departments = self._seed_departments(org, site)
        operating_models = self._seed_operating_models(org)
        modules = self._seed_module_activations(org)
        positions = self._seed_positions(org, site, departments)
        users = self._seed_users(org)
        memberships = self._seed_memberships(org, site, departments, positions, users)
        self._seed_policy_foundations(org, departments, operating_models)
        documents = {}
        workspaces = self._seed_workspaces(org, site, venues, departments, users, today)

        self._seed_intake(org, venues, users, today)
        self._seed_calendar(org, venues, departments, users, workspaces, today)
        self._seed_department_records(org, venues, departments, users, workspaces, documents, today)
        self._seed_audit(org, users, workspaces)

        self.stdout.write(self.style.SUCCESS('Seeded Moukangwe Theatre UAT data.'))
        self.stdout.write(f'Organisation: {org.name} ({org.slug})')
        self.stdout.write(f'Site: {site.name}')
        self.stdout.write(f'UAT password: {UAT_PASSWORD}')
        self.stdout.write('Primary admin: admin@moukangwetheatre.test')

    def _seed_venues(self, org, site):
        venue_rows = [
            ('Tene Theatre', 'performance', 'Main performance venue', 600),
            ('Tumisho Theatre', 'performance', 'Second largest performance venue', 350),
            ('Koketso Theatre', 'performance', 'Smaller performance and rehearsal venue', 150),
            ('Dikeledi Restaurant', 'other', 'Restaurant and hospitality space linked to visitor experience', 120),
            (
                'Moukangwe Foyer',
                'multipurpose',
                'Foyer, launches, receptions, networking, exhibition and small public events',
                200,
            ),
            ('Rehearsal Room', 'rehearsal', 'Rehearsals, workshops, youth classes and training sessions', 80),
        ]
        space_types = {
            'Tene Theatre': 'auditorium',
            'Tumisho Theatre': 'auditorium',
            'Koketso Theatre': 'studio',
            'Dikeledi Restaurant': 'restaurant',
            'Moukangwe Foyer': 'foyer',
            'Rehearsal Room': 'workshop',
        }
        venues = {}
        for name, venue_type, description, capacity in venue_rows:
            venue, _ = Venue.objects.update_or_create(
                organisation=org,
                site=site,
                name=name,
                defaults={
                    'venue_type': venue_type,
                    'description': description,
                    'capacity': capacity,
                    'is_active': True,
                },
            )
            Space.objects.update_or_create(
                organisation=org,
                venue=venue,
                name=name,
                defaults={
                    'space_type': space_types[name],
                    'capacity': capacity,
                    'is_bookable': True,
                },
            )
            venues[name] = venue
        return venues

    def _seed_departments(self, org, site):
        rows = [
            ('EXEC', 'Executive Office', 'executive'),
            ('PROG', 'Programming', 'programming'),
            ('MKT', 'Marketing and Communications', 'marketing'),
            ('TECH', 'Technical and Stage Management', 'technical'),
            ('FOH', 'FOH / Operations', 'operations'),
            ('CON', 'Contracts / Legal', 'contracts'),
            ('SCM', 'SCM / Finance', 'finance'),
            ('TIX', 'Ticketing / Audience Coordination', 'ticketing'),
            ('YTH', 'Youth Development', 'youth'),
            ('GOV', 'Governance / M&E', 'governance'),
            ('HOSP', 'Hospitality / Restaurant Operations', 'operations'),
        ]
        departments = {}
        for code, name, department_type in rows:
            department, _ = Department.objects.update_or_create(
                organisation=org,
                code=code,
                defaults={
                    'name': name,
                    'department_type': department_type,
                    'site': site,
                    'is_active': True,
                },
            )
            departments[name] = department
        return departments

    def _seed_operating_models(self, org):
        rows = [
            (
                'Moukangwe Theatre Operating Model',
                'multi_venue',
                True,
                True,
                'Moukangwe Theatre multi-venue operating model.',
                {
                    'sites': ['Moukangwe Theatre Complex'],
                    'shared_services': ['SCM / Finance', 'Contracts / Legal', 'Governance / M&E'],
                    'department_authority': 'department-led with executive oversight',
                },
            ),
            (
                'JCT Multi-Theatre Operating Model',
                'multi_theatre',
                False,
                False,
                'Template for a multi-theatre structure with central shared services and theatre-level GMs.',
                {
                    'template': True,
                    'sites': ['Joburg Theatre', 'Roodepoort Theatre', 'Soweto Theatre', 'Head Office'],
                    'features': [
                        'Head Office',
                        'Multiple theatre sites',
                        'Shared services',
                        'Theatre-level GMs',
                        'Central executive oversight',
                        'Central SCM/Finance',
                        'Venue-specific FOH and Technical',
                        'Theatre-specific programming',
                        'Corporate reporting',
                    ],
                },
            ),
            (
                'State Theatre Institutional Operating Model',
                'institutional',
                False,
                False,
                'Template for a single large institution with formal approvals, board reporting and public-sector controls.',
                {
                    'template': True,
                    'features': [
                        'Single large institution',
                        'Multiple internal venues',
                        'Central departments',
                        'Formal executive approval',
                        'Board reporting',
                        'Artistic/programming governance',
                        'Technical feasibility checks',
                        'Public-sector SCM and finance controls',
                    ],
                },
            ),
        ]
        models = {}
        for name, model_type, is_active, is_default, description, configuration in rows:
            operating_model, _ = OrganisationOperatingModel.objects.update_or_create(
                organisation=org,
                name=name,
                defaults={
                    'model_type': model_type,
                    'description': description,
                    'is_active': is_active,
                    'is_default': is_default,
                    'configuration': configuration,
                },
            )
            models[name] = operating_model
        return models

    def _seed_module_activations(self, org):
        rows = [
            ('dashboard', 'Dashboard'),
            ('calendar', 'Calendar'),
            ('workspaces', 'Workspaces'),
            ('programming', 'Programming'),
            ('marketing', 'Marketing'),
            ('technical', 'Technical'),
            ('operations', 'FOH / Operations'),
            ('contracts', 'Contracts'),
            ('suppliers', 'Suppliers'),
            ('artists', 'Artists'),
            ('ticketing', 'Ticketing'),
            ('youth', 'Youth Development'),
            ('governance', 'Governance'),
            ('hospitality', 'Hospitality'),
            ('documents', 'Documents / Evidence'),
            ('reports', 'Reports'),
            ('audit', 'Audit Trail'),
            ('settings', 'Settings'),
        ]
        modules = {}
        for module_key, label in rows:
            module, _ = ModuleActivation.objects.update_or_create(
                organisation=org,
                module_key=module_key,
                defaults={'label': label, 'is_enabled': True, 'configuration': {}},
            )
            modules[module_key] = module
        return modules

    def _position_defaults(self, department, title, authority):
        is_manager = authority in {AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER}
        is_specialist = authority == AuthorityLevel.SPECIALIST
        is_external = authority == AuthorityLevel.EXTERNAL
        level_map = {
            AuthorityLevel.EXECUTIVE: PositionLevel.EXECUTIVE,
            AuthorityLevel.GM: PositionLevel.SENIOR_MANAGER,
            AuthorityLevel.DEPARTMENT_MANAGER: PositionLevel.MANAGER,
            AuthorityLevel.DEPARTMENT_USER: PositionLevel.OFFICER,
            AuthorityLevel.SPECIALIST: PositionLevel.COORDINATOR,
            AuthorityLevel.READ_ONLY: PositionLevel.EXTERNAL,
            AuthorityLevel.EXTERNAL: PositionLevel.EXTERNAL,
        }
        return {
            'department': department,
            'level': level_map[authority],
            'authority_level': authority,
            'code': title.lower().replace(' / ', '-').replace(' ', '-'),
            'description': f'{title} position for {department.name}.',
            'is_manager_position': is_manager,
            'is_specialist_position': is_specialist,
            'is_external_position': is_external,
            'is_active': True,
        }

    def _seed_positions(self, org, site, departments):
        rows = {
            'Executive Office': [
                ('System Administrator', AuthorityLevel.EXECUTIVE),
                ('Chief Executive Officer', AuthorityLevel.EXECUTIVE),
                ('Chief Operating Officer', AuthorityLevel.EXECUTIVE),
                ('General Manager', AuthorityLevel.GM),
                ('Executive Assistant', AuthorityLevel.DEPARTMENT_USER),
                ('Board Member / Read-only Oversight', AuthorityLevel.READ_ONLY),
                ('Read-only User', AuthorityLevel.READ_ONLY),
            ],
            'Programming': [
                ('Programming Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Programming Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Producer', AuthorityLevel.SPECIALIST),
            ],
            'Marketing and Communications': [
                ('Marketing Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Marketing Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Graphic Designer', AuthorityLevel.SPECIALIST),
                ('Publicist', AuthorityLevel.SPECIALIST),
                ('Digital / Social Media Officer', AuthorityLevel.SPECIALIST),
                ('Marketing Assistant', AuthorityLevel.DEPARTMENT_USER),
                ('Photographer / Videographer', AuthorityLevel.SPECIALIST),
            ],
            'Technical and Stage Management': [
                ('Technical Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Stage Manager', AuthorityLevel.SPECIALIST),
                ('Lighting Technician', AuthorityLevel.SPECIALIST),
                ('Sound Technician', AuthorityLevel.SPECIALIST),
                ('AV Technician', AuthorityLevel.SPECIALIST),
                ('Wardrobe / Props Officer', AuthorityLevel.SPECIALIST),
                ('Technical Assistant', AuthorityLevel.DEPARTMENT_USER),
            ],
            'FOH / Operations': [
                ('FOH Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('House Manager', AuthorityLevel.SPECIALIST),
                ('Operations Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Security Coordinator', AuthorityLevel.SPECIALIST),
                ('Cleaning Coordinator', AuthorityLevel.SPECIALIST),
                ('Hospitality Coordinator', AuthorityLevel.SPECIALIST),
            ],
            'Contracts / Legal': [
                ('Contracts Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Contracts Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Legal Reviewer', AuthorityLevel.SPECIALIST),
            ],
            'SCM / Finance': [
                ('SCM Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('SCM Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Finance Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Payment Pack Reviewer', AuthorityLevel.SPECIALIST),
            ],
            'Ticketing / Audience Coordination': [
                ('Ticketing Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Ticketing Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Audience Coordinator', AuthorityLevel.SPECIALIST),
            ],
            'Youth Development': [
                ('Youth Development Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Youth Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Facilitator', AuthorityLevel.SPECIALIST),
                ('Attendance Capturer', AuthorityLevel.DEPARTMENT_USER),
            ],
            'Governance / M&E': [
                ('Governance Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('M&E Officer', AuthorityLevel.DEPARTMENT_USER),
                ('Risk Officer', AuthorityLevel.SPECIALIST),
                ('KPI Evidence Reviewer', AuthorityLevel.SPECIALIST),
            ],
            'Hospitality / Restaurant Operations': [
                ('Hospitality Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Restaurant Supervisor', AuthorityLevel.SPECIALIST),
                ('Hospitality Assistant', AuthorityLevel.DEPARTMENT_USER),
            ],
        }
        positions = {}
        for department_name, department_positions in rows.items():
            department = departments[department_name]
            for title, authority in department_positions:
                defaults = self._position_defaults(department, title, authority)
                defaults['site'] = site
                position, _ = Position.objects.update_or_create(
                    organisation=org,
                    department=department,
                    title=title,
                    defaults=defaults,
                )
                positions[(department_name, title)] = position
        return positions

    def _seed_users(self, org):
        user_rows = [
            ('admin@moukangwetheatre.test', UserType.INTERNAL_ADMIN, 'StageOS', 'Admin', True, True),
            ('ceo@moukangwetheatre.test', UserType.EXECUTIVE, 'Chief', 'Executive Officer', False, False),
            ('coo@moukangwetheatre.test', UserType.EXECUTIVE, 'Chief', 'Operating Officer', False, False),
            ('gm@moukangwetheatre.test', UserType.MANAGER, 'General', 'Manager', False, False),
            ('board@moukangwetheatre.test', UserType.READ_ONLY, 'Board', 'Member', False, False),
            ('readonly@moukangwetheatre.test', UserType.READ_ONLY, 'Read Only', 'User', False, False),
            ('designer@moukangwetheatre.test', UserType.STAFF, 'Graphic', 'Designer', False, False),
            ('publicist@moukangwetheatre.test', UserType.STAFF, 'Marketing', 'Publicist', False, False),
            ('photographer@moukangwetheatre.test', UserType.STAFF, 'Photo', 'Videographer', False, False),
            ('stage.manager@moukangwetheatre.test', UserType.STAFF, 'Stage', 'Manager', False, False),
            ('lighting.technician@moukangwetheatre.test', UserType.STAFF, 'Lighting', 'Technician', False, False),
            ('sound.technician@moukangwetheatre.test', UserType.STAFF, 'Sound', 'Technician', False, False),
            ('house.manager@moukangwetheatre.test', UserType.STAFF, 'House', 'Manager', False, False),
            ('client@moukangwetheatre.test', UserType.CLIENT_EXTERNAL, 'Client', 'Requester', False, False),
            ('supplier@moukangwetheatre.test', UserType.SUPPLIER_EXTERNAL, 'Supplier', 'External', False, False),
            ('artist@moukangwetheatre.test', UserType.ARTIST_EXTERNAL, 'Artist', 'External', False, False),
        ]
        department_prefixes = [
            ('programming', 'Programming'),
            ('marketing', 'Marketing'),
            ('technical', 'Technical'),
            ('foh', 'FOH'),
            ('contracts', 'Contracts'),
            ('scm', 'SCM'),
            ('ticketing', 'Ticketing'),
            ('youth', 'Youth'),
            ('governance', 'Governance'),
            ('hospitality', 'Hospitality'),
        ]
        for prefix, label in department_prefixes:
            user_rows.append((
                f'{prefix}.manager@moukangwetheatre.test',
                UserType.MANAGER,
                label,
                'Manager',
                False,
                False,
            ))
            user_rows.append((
                f'{prefix}.user@moukangwetheatre.test',
                UserType.STAFF,
                label,
                'User',
                False,
                False,
            ))

        users = {}
        for email, user_type, first_name, last_name, is_staff, is_superuser in user_rows:
            user, _ = User.objects.update_or_create(
                email=email,
                defaults={
                    'organisation': org,
                    'user_type': user_type,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                },
            )
            user.set_password(UAT_PASSWORD)
            user.save()
            users[email] = user
        return users

    def _seed_memberships(self, org, site, departments, positions, users):
        mappings = [
            ('admin@moukangwetheatre.test', 'Executive Office', 'System Administrator', AuthorityLevel.EXECUTIVE),
            ('ceo@moukangwetheatre.test', 'Executive Office', 'Chief Executive Officer', AuthorityLevel.EXECUTIVE),
            ('coo@moukangwetheatre.test', 'Executive Office', 'Chief Operating Officer', AuthorityLevel.EXECUTIVE),
            ('gm@moukangwetheatre.test', 'Executive Office', 'General Manager', AuthorityLevel.GM),
            ('board@moukangwetheatre.test', 'Executive Office', 'Board Member / Read-only Oversight', AuthorityLevel.READ_ONLY),
            ('readonly@moukangwetheatre.test', 'Executive Office', 'Read-only User', AuthorityLevel.READ_ONLY),
            ('programming.manager@moukangwetheatre.test', 'Programming', 'Programming Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('programming.user@moukangwetheatre.test', 'Programming', 'Programming Officer', AuthorityLevel.DEPARTMENT_USER),
            ('marketing.manager@moukangwetheatre.test', 'Marketing and Communications', 'Marketing Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('marketing.user@moukangwetheatre.test', 'Marketing and Communications', 'Marketing Officer', AuthorityLevel.DEPARTMENT_USER),
            ('designer@moukangwetheatre.test', 'Marketing and Communications', 'Graphic Designer', AuthorityLevel.SPECIALIST),
            ('publicist@moukangwetheatre.test', 'Marketing and Communications', 'Publicist', AuthorityLevel.SPECIALIST),
            ('photographer@moukangwetheatre.test', 'Marketing and Communications', 'Photographer / Videographer', AuthorityLevel.SPECIALIST),
            ('technical.manager@moukangwetheatre.test', 'Technical and Stage Management', 'Technical Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('technical.user@moukangwetheatre.test', 'Technical and Stage Management', 'Technical Assistant', AuthorityLevel.DEPARTMENT_USER),
            ('stage.manager@moukangwetheatre.test', 'Technical and Stage Management', 'Stage Manager', AuthorityLevel.SPECIALIST),
            ('lighting.technician@moukangwetheatre.test', 'Technical and Stage Management', 'Lighting Technician', AuthorityLevel.SPECIALIST),
            ('sound.technician@moukangwetheatre.test', 'Technical and Stage Management', 'Sound Technician', AuthorityLevel.SPECIALIST),
            ('foh.manager@moukangwetheatre.test', 'FOH / Operations', 'FOH Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('foh.user@moukangwetheatre.test', 'FOH / Operations', 'Operations Officer', AuthorityLevel.DEPARTMENT_USER),
            ('house.manager@moukangwetheatre.test', 'FOH / Operations', 'House Manager', AuthorityLevel.SPECIALIST),
            ('contracts.manager@moukangwetheatre.test', 'Contracts / Legal', 'Contracts Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('contracts.user@moukangwetheatre.test', 'Contracts / Legal', 'Contracts Officer', AuthorityLevel.DEPARTMENT_USER),
            ('scm.manager@moukangwetheatre.test', 'SCM / Finance', 'SCM Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('scm.user@moukangwetheatre.test', 'SCM / Finance', 'SCM Officer', AuthorityLevel.DEPARTMENT_USER),
            ('ticketing.manager@moukangwetheatre.test', 'Ticketing / Audience Coordination', 'Ticketing Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('ticketing.user@moukangwetheatre.test', 'Ticketing / Audience Coordination', 'Ticketing Officer', AuthorityLevel.DEPARTMENT_USER),
            ('youth.manager@moukangwetheatre.test', 'Youth Development', 'Youth Development Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('youth.user@moukangwetheatre.test', 'Youth Development', 'Youth Officer', AuthorityLevel.DEPARTMENT_USER),
            ('governance.manager@moukangwetheatre.test', 'Governance / M&E', 'Governance Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('governance.user@moukangwetheatre.test', 'Governance / M&E', 'M&E Officer', AuthorityLevel.DEPARTMENT_USER),
            ('hospitality.manager@moukangwetheatre.test', 'Hospitality / Restaurant Operations', 'Hospitality Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('hospitality.user@moukangwetheatre.test', 'Hospitality / Restaurant Operations', 'Hospitality Assistant', AuthorityLevel.DEPARTMENT_USER),
            ('client@moukangwetheatre.test', 'Executive Office', 'Read-only User', AuthorityLevel.EXTERNAL),
            ('supplier@moukangwetheatre.test', 'Executive Office', 'Read-only User', AuthorityLevel.EXTERNAL),
            ('artist@moukangwetheatre.test', 'Executive Office', 'Read-only User', AuthorityLevel.EXTERNAL),
        ]
        memberships = {}
        for email, department_name, position_title, authority in mappings:
            department = departments[department_name]
            position = positions.get((department_name, position_title)) or positions[('Executive Office', 'Read-only User')]
            can_manage = authority in {AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER}
            can_assign = authority in {AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER}
            can_approve = authority in {AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER}
            can_view = authority != AuthorityLevel.EXTERNAL
            can_raise = authority in {
                AuthorityLevel.EXECUTIVE,
                AuthorityLevel.GM,
                AuthorityLevel.DEPARTMENT_MANAGER,
                AuthorityLevel.DEPARTMENT_USER,
                AuthorityLevel.SPECIALIST,
            }
            membership, _ = UserDepartmentMembership.objects.update_or_create(
                organisation=org,
                user=users[email],
                department=department,
                position=position,
                defaults={
                    'site': site,
                    'authority_level': authority,
                    'is_primary': True,
                    'can_manage_department': can_manage,
                    'can_assign_work': can_assign,
                    'can_approve_work': can_approve,
                    'can_view_department_summary': can_view,
                    'can_raise_department_issue': can_raise,
                    'is_active': True,
                },
            )
            memberships[email] = membership
        return memberships

    def _seed_policy_foundations(self, org, departments, operating_models):
        policy_rows = [
            ('Marketing and Communications', 'marketing', 'marketing_readiness', AuthorityLevel.DEPARTMENT_MANAGER),
            ('Technical and Stage Management', 'technical', 'technical_readiness', AuthorityLevel.DEPARTMENT_MANAGER),
            ('FOH / Operations', 'operations', 'foh_readiness', AuthorityLevel.DEPARTMENT_MANAGER),
            ('Contracts / Legal', 'contracts', 'contract_review', AuthorityLevel.DEPARTMENT_MANAGER),
            ('SCM / Finance', 'suppliers', 'supplier_readiness', AuthorityLevel.DEPARTMENT_MANAGER),
            ('Youth Development', 'youth', 'youth_sensitive', AuthorityLevel.DEPARTMENT_MANAGER),
            ('Governance / M&E', 'governance', 'governance_action', AuthorityLevel.DEPARTMENT_MANAGER),
        ]
        for department_name, module_key, scope, authority in policy_rows:
            department = departments[department_name]
            ApprovalPolicy.objects.update_or_create(
                organisation=org,
                department=department,
                module_key=module_key,
                record_type='',
                approval_scope=scope,
                defaults={
                    'required_authority_level': authority,
                    'allow_executive_override': True,
                    'override_requires_reason': True,
                    'is_active': True,
                },
            )
            EvidenceRule.objects.update_or_create(
                organisation=org,
                department=department,
                module_key=module_key,
                record_type='department_work',
                work_type='',
                defaults={
                    'evidence_required': True,
                    'accepted_mime_types': ['application/pdf', 'image/png', 'image/jpeg', 'text/csv'],
                    'requires_review': True,
                    'reviewer_authority_level': authority,
                    'is_active': True,
                },
            )
            SOPTemplate.objects.update_or_create(
                organisation=org,
                operating_model=operating_models['Moukangwe Theatre Operating Model'],
                workspace_type='production',
                department=department,
                title=f'{department.name} production readiness SOP',
                defaults={
                    'description': f'Foundation SOP for {department.name} production readiness.',
                    'sequence': 1,
                    'is_active': True,
                },
            )

    def _seed_workspaces(self, org, site, venues, departments, users, today):
        owner = users['gm@moukangwetheatre.test']
        rows = [
            (
                'The Main Stage Production',
                'production',
                venues['Tene Theatre'],
                departments['Programming'],
                users['programming.manager@moukangwetheatre.test'],
                78,
                today + timedelta(days=20),
                today + timedelta(days=35),
            ),
            (
                'Tumisho Theatre Comedy Night',
                'venue_rental',
                venues['Tumisho Theatre'],
                departments['Programming'],
                users['programming.manager@moukangwetheatre.test'],
                64,
                today + timedelta(days=14),
                today + timedelta(days=14),
            ),
            (
                'Koketso Theatre Workshop Series',
                'workshop_series',
                venues['Koketso Theatre'],
                departments['Programming'],
                owner,
                52,
                today + timedelta(days=7),
                today + timedelta(days=28),
            ),
            (
                'Moukangwe Youth Development Programme',
                'youth_project',
                venues['Rehearsal Room'],
                departments['Youth Development'],
                users['youth.manager@moukangwetheatre.test'],
                45,
                today + timedelta(days=3),
                today + timedelta(days=90),
            ),
            (
                'Stakeholder Reception',
                'governance_item',
                venues['Moukangwe Foyer'],
                departments['Governance / M&E'],
                users['governance.manager@moukangwetheatre.test'],
                68,
                today + timedelta(days=18),
                today + timedelta(days=18),
            ),
            (
                'Dikeledi Restaurant Hospitality Support',
                'civic_event',
                venues['Dikeledi Restaurant'],
                departments['Hospitality / Restaurant Operations'],
                users['hospitality.manager@moukangwetheatre.test'],
                61,
                today + timedelta(days=12),
                today + timedelta(days=12),
            ),
        ]
        workspaces = {}
        for title, context_type, venue, department, workspace_owner, readiness, start_date, end_date in rows:
            workspace, _ = OperatingContext.objects.update_or_create(
                organisation=org,
                title=title,
                defaults={
                    'context_type': context_type,
                    'status': 'confirmed',
                    'priority': 'medium',
                    'risk_level': 'medium' if readiness < 60 else 'low',
                    'site': site,
                    'venue': venue,
                    'department': department,
                    'owner': workspace_owner,
                    'synopsis': f'UAT Workspace seeded for {title}.',
                    'start_date': start_date,
                    'end_date': end_date,
                    'opening_date': start_date,
                    'readiness_score': readiness,
                    'ticketing_provider': 'webtickets' if title != 'Moukangwe Youth Development Programme' else '',
                    'campaign_level': 'standard',
                },
            )
            workspaces[title] = workspace
        return workspaces

    def _seed_intake(self, org, venues, users, today):
        IntakeRequest.objects.update_or_create(
            organisation=org,
            event_title='Moukangwe Community Concert',
            defaults={
                'request_type': 'venue_booking',
                'status': 'submitted',
                'client_name': 'Moukangwe Community Arts Forum',
                'client_organisation': 'Moukangwe Community Arts Forum',
                'contact_email': 'client@moukangwetheatre.test',
                'contact_phone': '+27 10 000 0001',
                'requested_start_date': today + timedelta(days=45),
                'requested_end_date': today + timedelta(days=45),
                'preferred_venue': venues['Tene Theatre'],
                'expected_audience': 450,
                'ticketing_required': True,
                'technical_summary': 'Concert sound, basic lighting and lectern.',
                'foh_notes': 'Public community concert with VIP greeting table.',
                'accessibility_requirements': 'Wheelchair seating and accessible entrance support.',
                'attachments_note': 'Client can upload proposal PDF during browser UAT.',
                'notes': 'Seeded private intake request for Programming and Executive UAT.',
                'submitted_by': users['client@moukangwetheatre.test'],
            },
        )

    def _seed_calendar(self, org, venues, departments, users, workspaces, today):
        calendar_rows = [
            (workspaces['The Main Stage Production'], venues['Tene Theatre'], 'confirmed', 'performance', 20, time(18, 0), time(22, 0), 240, 60, 520),
            (workspaces['Tumisho Theatre Comedy Night'], venues['Tumisho Theatre'], 'confirmed', 'performance', 14, time(18, 0), time(22, 0), 180, 45, 300),
            (workspaces['Koketso Theatre Workshop Series'], venues['Koketso Theatre'], 'provisional', 'workshop', 7, time(10, 0), time(13, 0), 30, 30, 80),
            (workspaces['Dikeledi Restaurant Hospitality Support'], venues['Dikeledi Restaurant'], 'confirmed', 'other', 12, time(16, 0), time(21, 0), 60, 45, 90),
            (workspaces['Stakeholder Reception'], venues['Moukangwe Foyer'], 'confirmed', 'meeting', 18, time(17, 0), time(20, 0), 60, 30, 160),
            (workspaces['Moukangwe Youth Development Programme'], venues['Rehearsal Room'], 'confirmed', 'class', 5, time(9, 0), time(12, 0), 15, 15, 40),
        ]
        holds = {}
        for workspace, venue, hold_type, purpose, days, start, end, setup_buffer, strike_buffer, expected_audience in calendar_rows:
            hold, _ = VenueHold.objects.update_or_create(
                organisation=org,
                operating_context=workspace,
                venue=venue,
                hold_date=today + timedelta(days=days),
                defaults={
                    'hold_type': hold_type,
                    'start_time': start,
                    'end_time': end,
                    'setup_buffer_minutes': setup_buffer,
                    'strike_buffer_minutes': strike_buffer,
                    'expected_audience': expected_audience,
                    'purpose': purpose,
                    'notes': f'UAT {hold_type} hold for {venue.name}.',
                    'held_by': users['programming.manager@moukangwetheatre.test'],
                },
            )
            holds[venue.name] = hold
            CalendarSlot.objects.update_or_create(
                organisation=org,
                operating_context=workspace,
                venue=venue,
                date=today + timedelta(days=days),
                defaults={
                    'slot_type': 'performance' if purpose == 'performance' else 'rehearsal',
                    'is_confirmed': hold_type == 'confirmed',
                    'start_time': start,
                    'end_time': end,
                    'setup_buffer_minutes': setup_buffer,
                    'strike_buffer_minutes': strike_buffer,
                    'expected_audience': expected_audience,
                },
            )

        CalendarIssue.objects.update_or_create(
            organisation=org,
            title='Tene Theatre load-in clash check',
            defaults={
                'description': 'Confirm that main stage load-in does not conflict with hospitality setup.',
                'operating_context': workspaces['The Main Stage Production'],
                'venue_hold': holds['Tene Theatre'],
                'department': departments['Technical and Stage Management'],
                'severity': 'high',
                'status': 'open',
                'due_date': today + timedelta(days=10),
                'raised_by': users['gm@moukangwetheatre.test'],
            },
        )

    def _seed_department_records(self, org, venues, departments, users, workspaces, documents, today):
        main = workspaces['The Main Stage Production']
        youth_workspace = workspaces['Moukangwe Youth Development Programme']
        foyer = workspaces['Stakeholder Reception']

        documents['marketing'] = self._document(
            org, main, users['marketing.manager@moukangwetheatre.test'],
            'Main Stage artwork proof', 'marketing_asset', 'main-stage-artwork.pdf',
        )
        documents['supplier'] = self._document(
            org, main, users['scm.manager@moukangwetheatre.test'],
            'Moukangwe supplier CSD pack', 'csd_pack', 'supplier-csd-pack.pdf',
        )
        documents['contract'] = self._document(
            org, main, users['contracts.manager@moukangwetheatre.test'],
            'Signed Main Stage contract', 'contract', 'signed-main-stage-contract.pdf',
            locked=True,
        )
        documents['sales'] = self._document(
            org, main, users['ticketing.manager@moukangwetheatre.test'],
            'Ticketing sales import', 'report', 'ticketing-sales-import.csv',
            mime_type='text/csv',
        )
        documents['consent'] = self._document(
            org, youth_workspace, users['youth.manager@moukangwetheatre.test'],
            'Youth consent evidence', 'consent_form', 'youth-consent.pdf',
        )
        documents['governance'] = self._document(
            org, foyer, users['governance.manager@moukangwetheatre.test'],
            'Stakeholder KPI evidence', 'evidence', 'stakeholder-kpi-evidence.pdf',
        )

        self._seed_marketing(org, departments, users, main, documents['marketing'], today)
        self._seed_technical(org, users, main, today)
        self._seed_operations(org, users, main, venues, today)
        self._seed_contracts(org, users, main, documents['contract'], today)
        self._seed_suppliers(org, users, main, documents['supplier'])
        contract = ContractRecord.objects.get(organisation=org, operating_context=main, counterparty_name='Moukangwe Lead Artist')
        self._seed_artists(org, users, main, contract)
        self._seed_ticketing(org, users, main, documents['sales'])
        self._seed_youth(org, users, youth_workspace, venues, documents['consent'], today)
        self._seed_governance(org, departments, users, foyer, documents['governance'], today)

        self._task(
            org, main, departments['Marketing and Communications'],
            users['marketing.manager@moukangwetheatre.test'],
            'Marketing handover for The Main Stage Production',
            today + timedelta(days=5),
            True,
            documents['marketing'],
            work_type='approval_prep',
            assigned_by=users['marketing.manager@moukangwetheatre.test'],
        )
        self._task(
            org, main, departments['Marketing and Communications'],
            users['designer@moukangwetheatre.test'],
            'Design final poster artwork',
            today + timedelta(days=3),
            True,
            None,
            work_type='evidence',
            assigned_by=users['marketing.manager@moukangwetheatre.test'],
        )
        self._task(
            org, main, departments['Marketing and Communications'],
            users['publicist@moukangwetheatre.test'],
            'Prepare PR media list',
            today + timedelta(days=4),
            False,
            None,
            work_type='readiness',
            assigned_by=users['marketing.manager@moukangwetheatre.test'],
        )
        self._task(
            org, main, departments['Marketing and Communications'],
            users['photographer@moukangwetheatre.test'],
            'Capture production rehearsal visuals',
            today + timedelta(days=8),
            True,
            None,
            work_type='evidence',
            assigned_by=users['marketing.manager@moukangwetheatre.test'],
        )
        self._task(
            org, main, departments['Technical and Stage Management'],
            users['lighting.technician@moukangwetheatre.test'],
            'Technical rider readiness for The Main Stage Production',
            today + timedelta(days=6),
            False,
            None,
            work_type='readiness',
            assigned_by=users['technical.manager@moukangwetheatre.test'],
        )
        self._task(org, main, departments['Technical and Stage Management'], users['sound.technician@moukangwetheatre.test'], 'Confirm sound patch list', today + timedelta(days=6), False, None, work_type='readiness', assigned_by=users['technical.manager@moukangwetheatre.test'])
        self._task(org, main, departments['FOH / Operations'], users['house.manager@moukangwetheatre.test'], 'Confirm show-day house plan', today + timedelta(days=7), False, None, work_type='readiness', assigned_by=users['foh.manager@moukangwetheatre.test'])
        self._task(org, main, departments['Contracts / Legal'], users['contracts.user@moukangwetheatre.test'], 'Review artist contract pack', today + timedelta(days=4), True, documents['contract'], work_type='approval_prep', assigned_by=users['contracts.manager@moukangwetheatre.test'])
        self._task(org, main, departments['SCM / Finance'], users['scm.user@moukangwetheatre.test'], 'Verify supplier CSD evidence', today + timedelta(days=4), True, documents['supplier'], work_type='evidence', assigned_by=users['scm.manager@moukangwetheatre.test'])
        self._task(org, main, departments['Ticketing / Audience Coordination'], users['ticketing.user@moukangwetheatre.test'], 'Confirm ticketing booking link', today + timedelta(days=5), False, None, work_type='readiness', assigned_by=users['ticketing.manager@moukangwetheatre.test'])
        self._task(org, youth_workspace, departments['Youth Development'], users['youth.user@moukangwetheatre.test'], 'Capture youth attendance follow-up', today + timedelta(days=2), True, documents['consent'], work_type='evidence', assigned_by=users['youth.manager@moukangwetheatre.test'])
        self._task(org, foyer, departments['Governance / M&E'], users['governance.user@moukangwetheatre.test'], 'Prepare KPI evidence summary', today + timedelta(days=5), True, documents['governance'], work_type='evidence', assigned_by=users['governance.manager@moukangwetheatre.test'])
        self._task(org, foyer, departments['Hospitality / Restaurant Operations'], users['hospitality.user@moukangwetheatre.test'], 'Prepare Dikeledi hospitality checklist', today + timedelta(days=5), False, None, work_type='readiness', assigned_by=users['hospitality.manager@moukangwetheatre.test'])
        self._seed_approval(org, departments, users, main, documents['contract'])
        self._seed_executive_action(org, departments, users, main, today)

    def _document(self, org, workspace, user, title, document_type, file_name, mime_type='application/pdf', locked=False):
        return Document.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            title=title,
            defaults={
                'document_type': document_type,
                'file_name': file_name,
                'file_size': 0,
                'mime_type': mime_type,
                'storage_ref': f'uat/{file_name}',
                'uploaded_by': user,
                'is_locked': locked,
            },
        )[0]

    def _task(self, org, workspace, department, assigned_to, title, due_date, evidence_required, evidence_doc, work_type='general', assigned_by=None):
        task, _ = Task.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            title=title,
            defaults={
                'description': f'UAT task for {department.name}.',
                'department': department,
                'assigned_to': assigned_to,
                'assigned_by': assigned_by,
                'work_type': work_type,
                'due_date': due_date,
                'priority': 'high',
                'status': 'open',
                'evidence_required': evidence_required,
                'evidence_provided': evidence_doc is not None,
            },
        )
        if evidence_doc:
            EvidenceSubmission.objects.update_or_create(
                organisation=org,
                operating_context=workspace,
                task=task,
                document=evidence_doc,
                defaults={
                    'submitted_by': assigned_to,
                    'submission_note': f'UAT evidence for {title}.',
                    'accepted': True,
                    'accepted_by': assigned_to,
                    'accepted_at': timezone.now(),
                    'rejected': False,
                    'rejection_reason': '',
                },
            )
        if assigned_to:
            Notification.objects.update_or_create(
                organisation=org,
                recipient=assigned_to,
                task=task,
                notification_type='task_assigned',
                defaults={
                    'actor': assigned_by,
                    'department': department,
                    'title': 'Task assigned',
                    'message': title,
                },
            )
        return task

    def _seed_marketing(self, org, departments, users, workspace, document, today):
        campaign, _ = Campaign.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            defaults={
                'campaign_level': 'standard',
                'budget': 25000,
                'status': 'active',
                'owner': users['marketing.manager@moukangwetheatre.test'],
                'notes': 'UAT campaign for main stage public launch.',
            },
        )
        CampaignDeliverable.objects.update_or_create(
            organisation=org,
            campaign=campaign,
            title='Main Stage poster artwork',
            defaults={
                'deliverable_type': 'poster_design',
                'owner_name': 'Marketing and Communications',
                'due_date': today + timedelta(days=4),
                'status': 'review',
                'evidence_document': document,
            },
        )

    def _seed_technical(self, org, users, workspace, today):
        rider, _ = TechnicalRider.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            defaults={
                'lighting': 'Main theatre wash, specials and follow spot.',
                'sound': 'Concert PA, four vocal mics and playback.',
                'av': 'Projector and confidence monitor.',
                'crew_size': 8,
                'load_in_date': today + timedelta(days=18),
                'strike_date': today + timedelta(days=21),
                'status': 'submitted',
                'special_requirements': 'Props table and wardrobe quick-change area.',
            },
        )
        CrewRequirement.objects.update_or_create(
            organisation=org,
            rider=rider,
            role='Stage crew',
            defaults={'quantity': 6, 'notes': 'Main stage production crew.'},
        )
        EquipmentRequirement.objects.update_or_create(
            organisation=org,
            rider=rider,
            item='Wireless microphones',
            defaults={'quantity': 4, 'source': 'in_house', 'notes': 'Confirm batteries before show day.'},
        )

    def _seed_operations(self, org, users, workspace, venues, today):
        foh_plan, _ = FOHPlan.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            defaults={
                'ushers': 12,
                'security': 4,
                'cleaning': 3,
                'vip_count': 20,
                'accessibility_provisions': 'Accessible seating and foyer assistance.',
                'hospitality_notes': 'Dikeledi Restaurant pre-show hospitality for invited guests.',
                'status': 'planning',
            },
        )
        ShowDayChecklist.objects.update_or_create(
            organisation=org,
            foh_plan=foh_plan,
            item='Confirm Dikeledi Restaurant hospitality setup',
            defaults={
                'is_checked': False,
                'checked_by': None,
                'checked_at': None,
            },
        )
        Incident.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            description='UAT accessibility route check required before opening.',
            defaults={
                'foh_plan': foh_plan,
                'incident_type': 'accessibility_issue',
                'occurred_at': timezone.now(),
                'response': 'FOH to confirm ramp signage and usher briefing.',
                'reported_by': users['foh.manager@moukangwetheatre.test'],
                'severity': 'medium',
            },
        )

    def _seed_contracts(self, org, users, workspace, signed_doc, today):
        template, _ = ContractTemplate.objects.update_or_create(
            organisation=org,
            name='Moukangwe Artist Performance Agreement',
            defaults={
                'contract_type': 'artist_performance',
                'description': 'UAT artist performance agreement template.',
                'is_active': True,
                'version': 1,
            },
        )
        ContractRecord.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            counterparty_name='Moukangwe Lead Artist',
            defaults={
                'template': template,
                'contract_type': 'artist_performance',
                'counterparty_type': 'artist',
                'value': 45000,
                'currency': 'ZAR',
                'status': 'signed',
                'issued_date': today,
                'effective_date': today,
                'expiry_date': today + timedelta(days=60),
                'signatures_required': 2,
                'signatures_received': 2,
                'signed_document': signed_doc,
                'notes': 'UAT signed contract for artist engagement.',
            },
        )

    def _seed_suppliers(self, org, users, workspace, supplier_doc):
        supplier, _ = Supplier.objects.update_or_create(
            organisation=org,
            name='Moukangwe Technical Services',
            defaults={
                'category': 'Technical supplier',
                'panel': 'Approved Stage Services',
                'csd_number': 'CSD-MOUK-001',
                'csd_verified': True,
                'csd_verified_by': users['scm.manager@moukangwetheatre.test'],
                'csd_verified_at': timezone.now(),
                'bee_level': 'level_1',
                'contact_name': 'Supplier External',
                'contact_email': 'supplier@moukangwetheatre.test',
                'contact_phone': '+27 10 000 0002',
                'status': 'ready',
                'notes': 'UAT supplier linked to main stage production.',
            },
        )
        SupplierDocument.objects.update_or_create(
            organisation=org,
            supplier=supplier,
            document_type='csd_report',
            defaults={
                'document': supplier_doc,
                'file_name': supplier_doc.file_name,
                'status': 'verified',
                'verified_by': users['scm.manager@moukangwetheatre.test'],
                'verified_at': timezone.now(),
            },
        )
        engagement, _ = SupplierEngagement.objects.update_or_create(
            organisation=org,
            supplier=supplier,
            operating_context=workspace,
            defaults={'role': 'Lighting and sound support', 'value': 30000, 'status': 'confirmed'},
        )
        PaymentPack.objects.update_or_create(
            organisation=org,
            supplier_engagement=engagement,
            operating_context=workspace,
            defaults={
                'amount': 30000,
                'status': 'ready_for_erp',
                'erp_reference': 'ERP-UAT-001',
                'notes': 'UAT payment pack for supplier readiness testing.',
            },
        )

    def _seed_artists(self, org, users, workspace, contract):
        artist, _ = Artist.objects.update_or_create(
            organisation=org,
            legal_name='Moukangwe Lead Artist',
            defaults={
                'professional_name': 'Moukangwe Star',
                'discipline': 'Theatre performance',
                'contact_email': 'artist@moukangwetheatre.test',
                'contact_phone': '+27 10 000 0003',
                'standard_fee': 45000,
                'status': 'contracted',
                'notes': 'UAT artist for external artist access checks.',
            },
        )
        ArtistDocument.objects.update_or_create(
            organisation=org,
            artist=artist,
            document_type='contract',
            defaults={
                'document': contract.signed_document,
                'file_name': contract.signed_document.file_name,
                'status': 'verified',
                'verified_by': users['contracts.manager@moukangwetheatre.test'],
                'verified_at': timezone.now(),
            },
        )
        ArtistEngagement.objects.update_or_create(
            organisation=org,
            artist=artist,
            operating_context=workspace,
            defaults={
                'role': 'Lead performer',
                'fee': 45000,
                'contract': contract,
                'status': 'contracted',
            },
        )

    def _seed_ticketing(self, org, users, workspace, sales_doc):
        setup, _ = TicketingSetup.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            defaults={
                'provider': 'webtickets',
                'booking_link': 'https://tickets.example.test/main-stage-production',
                'pricing_description': 'R120 standard, R80 concession.',
                'comps_allocated': 30,
                'comps_used': 12,
                'setup_status': 'live',
                'sales_imported': True,
                'tickets_sold': 180,
                'tickets_available': 600,
                'settlement_status': 'in_progress',
                'settlement_amount': 0,
                'notes': 'UAT ticketing setup, not live ticketing integration.',
            },
        )
        SalesImport.objects.update_or_create(
            organisation=org,
            ticketing_setup=setup,
            source_file=sales_doc,
            defaults={
                'tickets_sold': 180,
                'revenue': 21600,
                'imported_by': users['ticketing.manager@moukangwetheatre.test'],
                'notes': 'UAT sales import evidence.',
            },
        )

    def _seed_youth(self, org, users, workspace, venues, consent_doc, today):
        project, _ = YouthProject.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            defaults={
                'target_learners': 40,
                'target_schools': 4,
                'age_range_min': 12,
                'age_range_max': 18,
                'safeguarding_notes': 'Sensitive UAT safeguarding note. Verify restricted access.',
                'status': 'active',
            },
        )
        activity, _ = Activity.objects.update_or_create(
            organisation=org,
            youth_project=project,
            name='Moukangwe Youth Rehearsal',
            defaults={
                'activity_type': 'class_session',
                'venue': venues['Rehearsal Room'],
                'space': venues['Rehearsal Room'].spaces.first(),
                'recurrence': 'weekly',
                'start_date': today + timedelta(days=3),
                'end_date': today + timedelta(days=45),
                'day_of_week': 'Saturday',
                'start_time': time(10, 0),
                'end_time': time(12, 0),
                'facilitator_count': 2,
                'max_learners': 40,
                'description': 'Youth theatre training and rehearsal session.',
            },
        )
        session, _ = Session.objects.update_or_create(
            organisation=org,
            activity=activity,
            session_date=today + timedelta(days=3),
            defaults={
                'start_time': time(10, 0),
                'end_time': time(12, 0),
                'venue': venues['Rehearsal Room'],
                'status': 'scheduled',
                'facilitator_notes': 'First UAT youth session.',
                'attendance_captured': True,
            },
        )
        group, _ = LearnerGroup.objects.update_or_create(
            organisation=org,
            youth_project=project,
            name='Moukangwe Youth Group A',
            defaults={'description': 'Seeded learner group for UAT.'},
        )
        FacilitatorAssignment.objects.update_or_create(
            organisation=org,
            youth_project=project,
            facilitator=users['youth.manager@moukangwetheatre.test'],
            activity=activity,
            defaults={
                'role': 'Lead facilitator',
                'start_date': today,
                'end_date': today + timedelta(days=90),
                'is_vetted': True,
                'vetting_date': today,
                'vetting_notes': 'UAT vetting complete.',
            },
        )
        ConsentRecord.objects.update_or_create(
            organisation=org,
            youth_project=project,
            learner_identifier='YTH-UAT-001',
            defaults={
                'learner_group': group,
                'guardian_consent_received': True,
                'consent_date': today,
                'consent_document': consent_doc,
                'photo_consent': True,
                'data_processing_consent': True,
                'notes': 'UAT consent record.',
            },
        )
        AttendanceRecord.objects.update_or_create(
            organisation=org,
            session=session,
            learner_identifier='YTH-UAT-001',
            defaults={
                'learner_group': group,
                'present': True,
                'arrival_time': time(9, 55),
                'notes': 'UAT attendance captured.',
            },
        )
        Assessment.objects.update_or_create(
            organisation=org,
            youth_project=project,
            learner_identifier='YTH-UAT-001',
            assessment_type='formative',
            defaults={
                'activity': activity,
                'score': 'Ready',
                'assessor': users['youth.manager@moukangwetheatre.test'],
                'assessment_date': today,
                'notes': 'UAT formative assessment.',
                'evidence_document': consent_doc,
            },
        )
        ShowcaseOutput.objects.update_or_create(
            organisation=org,
            youth_project=project,
            title='Moukangwe Youth Showcase',
            defaults={
                'output_type': 'performance',
                'date': today + timedelta(days=80),
                'description': 'Seeded youth showcase output.',
                'evidence_document': consent_doc,
            },
        )

    def _seed_governance(self, org, departments, users, workspace, evidence_doc, today):
        kpi, _ = KPI.objects.update_or_create(
            organisation=org,
            name='Stakeholder engagement readiness',
            defaults={
                'owner_department': departments['Governance / M&E'],
                'owner_description': 'Governance / M&E',
                'target_value': 100,
                'actual_value': 75,
                'unit': '%',
                'evidence_description': 'Evidence required for stakeholder readiness KPI.',
                'reporting_period': 'quarterly',
                'is_active': True,
            },
        )
        KPIEvidence.objects.update_or_create(
            organisation=org,
            kpi=kpi,
            operating_context=workspace,
            defaults={
                'value_reported': 75,
                'evidence_document': evidence_doc,
                'reported_by': users['governance.manager@moukangwetheatre.test'],
                'notes': 'UAT KPI evidence.',
            },
        )
        risk, _ = Risk.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            title='Stakeholder reception readiness risk',
            defaults={
                'description': 'Catering and protocol confirmation required.',
                'risk_level': 'medium',
                'owner': users['governance.manager@moukangwetheatre.test'],
                'status': 'open',
                'mitigation_plan': 'Confirm Dikeledi Restaurant hospitality plan and guest list.',
            },
        )
        CorrectiveAction.objects.update_or_create(
            organisation=org,
            risk=risk,
            action='Confirm Dikeledi Restaurant hospitality plan',
            defaults={
                'owner': users['hospitality.manager@moukangwetheatre.test'],
                'due_date': today + timedelta(days=6),
                'status': 'open',
                'evidence_document': evidence_doc,
            },
        )

    def _seed_approval(self, org, departments, users, workspace, evidence_doc):
        route, _ = ApprovalRoute.objects.update_or_create(
            organisation=org,
            name='Moukangwe Production Approval Route',
            defaults={
                'context_type': 'production',
                'description': 'UAT route for main stage production approval.',
                'is_active': True,
            },
        )
        step, _ = ApprovalStep.objects.update_or_create(
            organisation=org,
            route=route,
            step_number=1,
            defaults={
                'name': 'Executive production approval',
                'approver_department': departments['Executive Office'],
                'approver_role_description': 'CEO or COO',
                'can_delegate': True,
            },
        )
        ApprovalRequest.objects.update_or_create(
            organisation=org,
            operating_context=workspace,
            approval_step=step,
            defaults={
                'decision': 'pending',
                'requested_by': users['programming.manager@moukangwetheatre.test'],
                'evidence_reviewed': evidence_doc,
                'decision_comment': 'UAT approval request for main stage production.',
            },
        )

    def _seed_executive_action(self, org, departments, users, workspace, today):
        ExecutiveAction.objects.update_or_create(
            organisation=org,
            title='Revise main stage artwork before publishing',
            defaults={
                'action_type': 'request_change',
                'status': 'open',
                'reason': 'Artwork must include approved institutional positioning and funder logo.',
                'instruction': 'Correct event title, add approved funder logo and resubmit artwork evidence.',
                'operating_context': workspace,
                'target_type': 'marketing.campaign',
                'target_id': str(getattr(workspace, 'campaign', workspace).id),
                'department': departments['Marketing and Communications'],
                'assigned_to': users['marketing.manager@moukangwetheatre.test'],
                'due_date': today + timedelta(days=3),
                'created_by': users['ceo@moukangwetheatre.test'],
            },
        )

    def _seed_audit(self, org, users, workspaces):
        workspace = workspaces['The Main Stage Production']
        AuditEvent.objects.get_or_create(
            organisation=org,
            event_type='uat.seed',
            target_type='workspace',
            target_id=str(workspace.id),
            defaults={
                'actor': users['admin@moukangwetheatre.test'],
                'reason': 'Idempotent Moukangwe Theatre UAT seed.',
                'payload': {'command': 'seed_dev_data', 'organisation': 'Moukangwe Theatre'},
            },
        )
