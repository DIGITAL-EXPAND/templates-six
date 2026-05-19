"""
Seed command for Joburg City Theatres (JCT) pilot data.

Creates:
  - Organisation: Joburg City Theatres
  - 3 sites: Joburg Theatre, Roodepoort Theatre, Soweto Theatre
  - Venues per site (main auditorium, studio, foyer, rehearsal room)
  - All 11 departments with positions
  - ~35 users (manager + staff per dept + executive team + externals)
  - 3 demo workspaces at various readiness levels
  - Baseline records for every department module
"""
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User, UserType
from apps.artists.models import Artist, ArtistDocument, ArtistEngagement
from apps.audit.models import AuditEvent
from apps.contexts.models import OperatingContext
from apps.contracts.models import ContractRecord
from apps.documents.models import Document
from apps.governance.models import ExecutiveAction, KPI, Risk
from apps.marketing.models import Campaign, CampaignDeliverable
from apps.operations.models import FOHPlan, Incident, ShowDayChecklist
from apps.organisations.models import Organisation
from apps.programming.models import CalendarSlot, IntakeRequest, VenueHold
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
from apps.suppliers.models import Supplier, SupplierDocument, SupplierEngagement
from apps.tasks.models import Task
from apps.technical.models import TechnicalRider
from apps.ticketing.models import TicketingSetup
from apps.youth.models import ConsentRecord, LearnerGroup, YouthProject


PILOT_PASSWORD = 'JCTPilot2026!'


class Command(BaseCommand):
    help = 'Seed Joburg City Theatres pilot data for StageOS.'

    def handle(self, *args, **options):
        today = date.today()

        org, _ = Organisation.objects.update_or_create(
            slug='joburg-city-theatres',
            defaults={
                'name': 'Joburg City Theatres',
                'is_active': True,
                'popia_privacy_notice_url': 'https://www.jct.org.za/privacy',
                'default_retention_days': 365,
            },
        )

        sites = self._seed_sites(org)
        venues = self._seed_venues(org, sites)
        departments = self._seed_departments(org, sites)
        self._seed_operating_models(org)
        self._seed_module_activations(org)
        positions = self._seed_positions(org, sites, departments)
        users = self._seed_users(org)
        self._seed_memberships(org, sites, departments, positions, users)
        self._seed_policy_foundations(org, departments)
        workspaces = self._seed_workspaces(org, sites, venues, departments, users, today)
        self._seed_intake(org, venues, users, today)
        self._seed_calendar(org, venues, departments, users, workspaces, today)
        self._seed_department_records(org, venues, departments, users, workspaces, today)
        self._seed_governance(org, departments, users, today)
        self._seed_tasks(org, departments, users, workspaces, today)
        self._seed_audit(org, users)

        self.stdout.write(self.style.SUCCESS('\nJoburg City Theatres pilot data seeded.'))
        self.stdout.write(f'Organisation : {org.name} ({org.slug})')
        self.stdout.write(f'Sites        : {", ".join(s.name for s in sites.values())}')
        self.stdout.write(f'Pilot password: {PILOT_PASSWORD}')
        self.stdout.write('Primary admin : admin@jct.pilot')
        self.stdout.write('\nUser quick-reference:')
        self.stdout.write('  admin@jct.pilot                    — System Admin')
        self.stdout.write('  ceo@jct.pilot                      — CEO (Executive)')
        self.stdout.write('  coo@jct.pilot                      — COO (Executive)')
        self.stdout.write('  gm.joburg@jct.pilot                — GM – Joburg Theatre')
        self.stdout.write('  gm.roodepoort@jct.pilot            — GM – Roodepoort Theatre')
        self.stdout.write('  gm.soweto@jct.pilot                — GM – Soweto Theatre')
        self.stdout.write('  board@jct.pilot                    — Board Member (read-only)')
        self.stdout.write('  programming.manager@jct.pilot      — Programming Manager')
        self.stdout.write('  marketing.manager@jct.pilot        — Marketing Manager')
        self.stdout.write('  technical.manager@jct.pilot        — Technical Manager')
        self.stdout.write('  foh.manager@jct.pilot              — FOH Manager')
        self.stdout.write('  contracts.manager@jct.pilot        — Contracts Manager')
        self.stdout.write('  scm.manager@jct.pilot              — SCM Manager')
        self.stdout.write('  ticketing.manager@jct.pilot        — Ticketing Manager')
        self.stdout.write('  youth.manager@jct.pilot            — Youth Development Manager')
        self.stdout.write('  governance.manager@jct.pilot       — Governance Manager')
        self.stdout.write('  hospitality.manager@jct.pilot      — Hospitality Manager')
        self.stdout.write('  client@jct.pilot                   — External Client')
        self.stdout.write('  supplier@jct.pilot                 — External Supplier')
        self.stdout.write('  artist@jct.pilot                   — External Artist')

    # ------------------------------------------------------------------
    # Sites
    # ------------------------------------------------------------------

    def _seed_sites(self, org):
        rows = [
            ('JT',  'Joburg Theatre',      'Braamfontein Precinct, Johannesburg'),
            ('RT',  'Roodepoort Theatre',  '100 Ontdekkers Rd, Roodepoort'),
            ('ST',  'Soweto Theatre',      'Jabulani, Soweto'),
        ]
        sites = {}
        for code, name, address in rows:
            site, _ = Site.objects.update_or_create(
                organisation=org,
                code=code,
                defaults={
                    'name': name,
                    'address': address,
                    'city': 'Johannesburg',
                    'province': 'Gauteng',
                    'country': 'South Africa',
                    'is_active': True,
                },
            )
            sites[code] = site
        return sites

    # ------------------------------------------------------------------
    # Venues
    # ------------------------------------------------------------------

    def _seed_venues(self, org, sites):
        # (site_code, name, venue_type, space_type, capacity)
        rows = [
            ('JT', 'Joburg Theatre – Main Auditorium', 'performance', 'auditorium', 1000),
            ('JT', 'Joburg Theatre – Amphitheatre',    'performance', 'auditorium',  350),
            ('JT', 'Joburg Theatre – Basement Theatre','performance', 'studio',       80),
            ('JT', 'Joburg Theatre – Studio',          'performance', 'studio',       30),
            ('JT', 'Joburg Theatre – Foyer',           'multipurpose','foyer',        200),
            ('JT', 'Joburg Theatre – Rehearsal Room',  'rehearsal',   'workshop',     60),
            ('RT', 'Roodepoort – Main Theatre',        'performance', 'auditorium',  500),
            ('RT', 'Roodepoort – Studio',              'performance', 'studio',       80),
            ('RT', 'Roodepoort – Foyer',               'multipurpose','foyer',        150),
            ('RT', 'Roodepoort – Rehearsal Room',      'rehearsal',   'workshop',     40),
            ('ST', 'Soweto Theatre – Main Auditorium', 'performance', 'auditorium',  480),
            ('ST', 'Soweto Theatre – Rehearsal Room',  'rehearsal',   'workshop',     50),
            ('ST', 'Soweto Theatre – Foyer',           'multipurpose','foyer',        120),
        ]
        venues = {}
        for site_code, name, venue_type, space_type, capacity in rows:
            site = sites[site_code]
            venue, _ = Venue.objects.update_or_create(
                organisation=org,
                site=site,
                name=name,
                defaults={
                    'venue_type': venue_type,
                    'capacity': capacity,
                    'is_active': True,
                },
            )
            Space.objects.update_or_create(
                organisation=org,
                venue=venue,
                name=name,
                defaults={
                    'space_type': space_type,
                    'capacity': capacity,
                    'is_bookable': True,
                },
            )
            venues[name] = venue
        return venues

    # ------------------------------------------------------------------
    # Departments  (shared across all sites)
    # ------------------------------------------------------------------

    def _seed_departments(self, org, sites):
        primary = sites['JT']
        rows = [
            ('EXEC', 'Executive Office',                   'executive',   primary),
            ('PROG', 'Programming',                        'programming', primary),
            ('MKT',  'Marketing and Communications',       'marketing',   primary),
            ('TECH', 'Technical and Stage Management',     'technical',   primary),
            ('FOH',  'FOH / Operations',                   'operations',  primary),
            ('CON',  'Contracts / Legal',                  'contracts',   primary),
            ('SCM',  'SCM / Finance',                      'finance',     primary),
            ('TIX',  'Ticketing / Audience Coordination',  'ticketing',   primary),
            ('YTH',  'Youth Development',                  'youth',       primary),
            ('GOV',  'Governance / M&E',                   'governance',  primary),
            ('HOSP', 'Hospitality / Restaurant Operations','operations',  primary),
        ]
        departments = {}
        for code, name, dept_type, site in rows:
            dept, _ = Department.objects.update_or_create(
                organisation=org,
                code=code,
                defaults={
                    'name': name,
                    'department_type': dept_type,
                    'site': site,
                    'is_active': True,
                },
            )
            departments[name] = dept
        return departments

    # ------------------------------------------------------------------
    # Operating models
    # ------------------------------------------------------------------

    def _seed_operating_models(self, org):
        OrganisationOperatingModel.objects.update_or_create(
            organisation=org,
            name='JCT Multi-Theatre Operating Model',
            defaults={
                'model_type': 'multi_theatre',
                'description': (
                    'Three-theatre structure with Head Office shared services (SCM, Legal, Governance) '
                    'and site-level GMs (Joburg Theatre, Roodepoort Theatre, Soweto Theatre).'
                ),
                'is_active': True,
                'is_default': True,
                'configuration': {
                    'sites': ['Joburg Theatre', 'Roodepoort Theatre', 'Soweto Theatre'],
                    'shared_services': ['SCM / Finance', 'Contracts / Legal', 'Governance / M&E'],
                    'reporting_line': 'Theatre GMs → COO → CEO → Board',
                },
            },
        )

    # ------------------------------------------------------------------
    # Module activations
    # ------------------------------------------------------------------

    def _seed_module_activations(self, org):
        rows = [
            ('dashboard',   'Dashboard'),
            ('calendar',    'Calendar'),
            ('workspaces',  'Shows & Events'),
            ('programming', 'Programming'),
            ('marketing',   'Marketing & Publicity'),
            ('technical',   'Technical Production'),
            ('operations',  'FOH / Operations'),
            ('contracts',   'Contracts & Agreements'),
            ('suppliers',   'Suppliers'),
            ('artists',     'Performers'),
            ('ticketing',   'Box Office'),
            ('youth',       'Youth Programmes'),
            ('governance',  'Performance & Oversight'),
            ('hospitality', 'VIP & Hospitality'),
            ('documents',   'Files & Evidence'),
            ('reports',     'Reports'),
            ('audit',       'Audit Trail'),
            ('settings',    'Settings'),
        ]
        for module_key, label in rows:
            ModuleActivation.objects.update_or_create(
                organisation=org,
                module_key=module_key,
                defaults={'label': label, 'is_enabled': True, 'configuration': {}},
            )

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def _position_defaults(self, department, title, authority, site):
        is_manager = authority in {
            AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER
        }
        level_map = {
            AuthorityLevel.EXECUTIVE:         PositionLevel.EXECUTIVE,
            AuthorityLevel.GM:                PositionLevel.SENIOR_MANAGER,
            AuthorityLevel.DEPARTMENT_MANAGER:PositionLevel.MANAGER,
            AuthorityLevel.DEPARTMENT_USER:   PositionLevel.OFFICER,
            AuthorityLevel.SPECIALIST:        PositionLevel.COORDINATOR,
            AuthorityLevel.READ_ONLY:         PositionLevel.EXTERNAL,
            AuthorityLevel.EXTERNAL:          PositionLevel.EXTERNAL,
        }
        return {
            'department': department,
            'site': site,
            'level': level_map[authority],
            'authority_level': authority,
            'code': title.lower().replace(' / ', '-').replace(' ', '-').replace('&', 'and'),
            'description': f'{title} position for {department.name}.',
            'is_manager_position': is_manager,
            'is_specialist_position': authority == AuthorityLevel.SPECIALIST,
            'is_external_position': authority == AuthorityLevel.EXTERNAL,
            'is_active': True,
        }

    def _seed_positions(self, org, sites, departments):
        primary = sites['JT']
        rows = {
            'Executive Office': [
                ('System Administrator',                    AuthorityLevel.EXECUTIVE),
                ('Chief Executive Officer',                 AuthorityLevel.EXECUTIVE),
                ('Chief Operating Officer',                 AuthorityLevel.EXECUTIVE),
                ('General Manager – Joburg Theatre',        AuthorityLevel.GM),
                ('General Manager – Roodepoort Theatre',    AuthorityLevel.GM),
                ('General Manager – Soweto Theatre',        AuthorityLevel.GM),
                ('Executive Assistant',                     AuthorityLevel.DEPARTMENT_USER),
                ('Board Member',                            AuthorityLevel.READ_ONLY),
            ],
            'Programming': [
                ('Programming Manager',      AuthorityLevel.DEPARTMENT_MANAGER),
                ('Programming Officer',      AuthorityLevel.DEPARTMENT_USER),
                ('Producer',                 AuthorityLevel.SPECIALIST),
                ('Venue Programmer',         AuthorityLevel.SPECIALIST),
            ],
            'Marketing and Communications': [
                ('Marketing Manager',              AuthorityLevel.DEPARTMENT_MANAGER),
                ('Marketing Officer',              AuthorityLevel.DEPARTMENT_USER),
                ('Graphic Designer',               AuthorityLevel.SPECIALIST),
                ('Publicist',                      AuthorityLevel.SPECIALIST),
                ('Digital / Social Media Officer', AuthorityLevel.SPECIALIST),
                ('Photographer / Videographer',    AuthorityLevel.SPECIALIST),
            ],
            'Technical and Stage Management': [
                ('Technical Manager',       AuthorityLevel.DEPARTMENT_MANAGER),
                ('Stage Manager',           AuthorityLevel.SPECIALIST),
                ('Lighting Technician',     AuthorityLevel.SPECIALIST),
                ('Sound Technician',        AuthorityLevel.SPECIALIST),
                ('AV Technician',           AuthorityLevel.SPECIALIST),
                ('Technical Assistant',     AuthorityLevel.DEPARTMENT_USER),
            ],
            'FOH / Operations': [
                ('FOH Manager',             AuthorityLevel.DEPARTMENT_MANAGER),
                ('House Manager',           AuthorityLevel.SPECIALIST),
                ('Operations Officer',      AuthorityLevel.DEPARTMENT_USER),
                ('Security Coordinator',    AuthorityLevel.SPECIALIST),
                ('Cleaning Coordinator',    AuthorityLevel.SPECIALIST),
            ],
            'Contracts / Legal': [
                ('Contracts Manager',   AuthorityLevel.DEPARTMENT_MANAGER),
                ('Contracts Officer',   AuthorityLevel.DEPARTMENT_USER),
                ('Legal Reviewer',      AuthorityLevel.SPECIALIST),
            ],
            'SCM / Finance': [
                ('SCM Manager',             AuthorityLevel.DEPARTMENT_MANAGER),
                ('SCM Officer',             AuthorityLevel.DEPARTMENT_USER),
                ('Finance Officer',         AuthorityLevel.DEPARTMENT_USER),
                ('Payment Pack Reviewer',   AuthorityLevel.SPECIALIST),
            ],
            'Ticketing / Audience Coordination': [
                ('Ticketing Manager',    AuthorityLevel.DEPARTMENT_MANAGER),
                ('Ticketing Officer',    AuthorityLevel.DEPARTMENT_USER),
                ('Audience Coordinator', AuthorityLevel.SPECIALIST),
            ],
            'Youth Development': [
                ('Youth Development Manager', AuthorityLevel.DEPARTMENT_MANAGER),
                ('Youth Officer',             AuthorityLevel.DEPARTMENT_USER),
                ('Facilitator',               AuthorityLevel.SPECIALIST),
            ],
            'Governance / M&E': [
                ('Governance Manager',     AuthorityLevel.DEPARTMENT_MANAGER),
                ('M&E Officer',            AuthorityLevel.DEPARTMENT_USER),
                ('Risk Officer',           AuthorityLevel.SPECIALIST),
                ('KPI Evidence Reviewer',  AuthorityLevel.SPECIALIST),
            ],
            'Hospitality / Restaurant Operations': [
                ('Hospitality Manager',      AuthorityLevel.DEPARTMENT_MANAGER),
                ('Restaurant Supervisor',    AuthorityLevel.SPECIALIST),
                ('Hospitality Assistant',    AuthorityLevel.DEPARTMENT_USER),
            ],
        }
        positions = {}
        for dept_name, dept_rows in rows.items():
            dept = departments[dept_name]
            for title, authority in dept_rows:
                defaults = self._position_defaults(dept, title, authority, primary)
                position, _ = Position.objects.update_or_create(
                    organisation=org,
                    department=dept,
                    title=title,
                    defaults=defaults,
                )
                positions[(dept_name, title)] = position
        return positions

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _seed_users(self, org):
        rows = [
            # email, user_type, first_name, last_name, is_staff, is_superuser
            ('admin@jct.pilot',     UserType.INTERNAL_ADMIN, 'StageOS',    'Admin',         True, True),
            ('ceo@jct.pilot',       UserType.EXECUTIVE,      'Nomsa',      'Dlamini',        False, False),
            ('coo@jct.pilot',       UserType.EXECUTIVE,      'Sipho',      'Nkosi',          False, False),
            ('gm.joburg@jct.pilot', UserType.MANAGER,        'Thandi',     'Molefe',         False, False),
            ('gm.roodepoort@jct.pilot', UserType.MANAGER,    'Andre',      'Du Plessis',     False, False),
            ('gm.soweto@jct.pilot', UserType.MANAGER,        'Zanele',     'Sithole',        False, False),
            ('board@jct.pilot',     UserType.READ_ONLY,      'Board',      'Member',         False, False),
            # Department managers
            ('programming.manager@jct.pilot',  UserType.MANAGER, 'Lebo',   'Dube',      False, False),
            ('marketing.manager@jct.pilot',    UserType.MANAGER, 'Refilwe','Mthembu',   False, False),
            ('technical.manager@jct.pilot',    UserType.MANAGER, 'Johan',  'van Wyk',   False, False),
            ('foh.manager@jct.pilot',          UserType.MANAGER, 'Priya',  'Naidoo',    False, False),
            ('contracts.manager@jct.pilot',    UserType.MANAGER, 'Kabelo', 'Modise',    False, False),
            ('scm.manager@jct.pilot',          UserType.MANAGER, 'Ayesha', 'Khan',      False, False),
            ('ticketing.manager@jct.pilot',    UserType.MANAGER, 'Lungelo','Zulu',      False, False),
            ('youth.manager@jct.pilot',        UserType.MANAGER, 'Faith',  'Mokoena',   False, False),
            ('governance.manager@jct.pilot',   UserType.MANAGER, 'Siyanda','Cele',      False, False),
            ('hospitality.manager@jct.pilot',  UserType.MANAGER, 'Tebogo', 'Khumalo',   False, False),
            # Department staff
            ('programming.user@jct.pilot',     UserType.STAFF, 'Programming','Officer', False, False),
            ('marketing.user@jct.pilot',       UserType.STAFF, 'Marketing',  'Officer', False, False),
            ('technical.user@jct.pilot',       UserType.STAFF, 'Technical',  'Assistant',False, False),
            ('foh.user@jct.pilot',             UserType.STAFF, 'FOH',        'Officer', False, False),
            ('contracts.user@jct.pilot',       UserType.STAFF, 'Contracts',  'Officer', False, False),
            ('scm.user@jct.pilot',             UserType.STAFF, 'SCM',        'Officer', False, False),
            ('ticketing.user@jct.pilot',       UserType.STAFF, 'Ticketing',  'Officer', False, False),
            ('youth.user@jct.pilot',           UserType.STAFF, 'Youth',      'Officer', False, False),
            ('governance.user@jct.pilot',      UserType.STAFF, 'ME',         'Officer', False, False),
            ('hospitality.user@jct.pilot',     UserType.STAFF, 'Hospitality','Assistant',False, False),
            # Externals
            ('client@jct.pilot',    UserType.CLIENT_EXTERNAL,   'Client',   'Requester', False, False),
            ('supplier@jct.pilot',  UserType.SUPPLIER_EXTERNAL, 'Supplier', 'External',  False, False),
            ('artist@jct.pilot',    UserType.ARTIST_EXTERNAL,   'Artist',   'External',  False, False),
        ]
        users = {}
        for email, user_type, first_name, last_name, is_staff, is_superuser in rows:
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
            user.set_password(PILOT_PASSWORD)
            user.save()
            users[email] = user
        return users

    # ------------------------------------------------------------------
    # Memberships
    # ------------------------------------------------------------------

    def _seed_memberships(self, org, sites, departments, positions, users):
        primary = sites['JT']
        # (email, dept_name, position_title, authority)
        mappings = [
            ('admin@jct.pilot',     'Executive Office', 'System Administrator',              AuthorityLevel.EXECUTIVE),
            ('ceo@jct.pilot',       'Executive Office', 'Chief Executive Officer',            AuthorityLevel.EXECUTIVE),
            ('coo@jct.pilot',       'Executive Office', 'Chief Operating Officer',            AuthorityLevel.EXECUTIVE),
            ('gm.joburg@jct.pilot', 'Executive Office', 'General Manager – Joburg Theatre',   AuthorityLevel.GM),
            ('gm.roodepoort@jct.pilot','Executive Office','General Manager – Roodepoort Theatre', AuthorityLevel.GM),
            ('gm.soweto@jct.pilot', 'Executive Office', 'General Manager – Soweto Theatre',   AuthorityLevel.GM),
            ('board@jct.pilot',     'Executive Office', 'Board Member',                       AuthorityLevel.READ_ONLY),
            # Dept managers
            ('programming.manager@jct.pilot',  'Programming',                      'Programming Manager',       AuthorityLevel.DEPARTMENT_MANAGER),
            ('marketing.manager@jct.pilot',    'Marketing and Communications',     'Marketing Manager',         AuthorityLevel.DEPARTMENT_MANAGER),
            ('technical.manager@jct.pilot',    'Technical and Stage Management',   'Technical Manager',         AuthorityLevel.DEPARTMENT_MANAGER),
            ('foh.manager@jct.pilot',          'FOH / Operations',                 'FOH Manager',               AuthorityLevel.DEPARTMENT_MANAGER),
            ('contracts.manager@jct.pilot',    'Contracts / Legal',                'Contracts Manager',         AuthorityLevel.DEPARTMENT_MANAGER),
            ('scm.manager@jct.pilot',          'SCM / Finance',                    'SCM Manager',               AuthorityLevel.DEPARTMENT_MANAGER),
            ('ticketing.manager@jct.pilot',    'Ticketing / Audience Coordination','Ticketing Manager',         AuthorityLevel.DEPARTMENT_MANAGER),
            ('youth.manager@jct.pilot',        'Youth Development',                'Youth Development Manager', AuthorityLevel.DEPARTMENT_MANAGER),
            ('governance.manager@jct.pilot',   'Governance / M&E',                 'Governance Manager',        AuthorityLevel.DEPARTMENT_MANAGER),
            ('hospitality.manager@jct.pilot',  'Hospitality / Restaurant Operations','Hospitality Manager',     AuthorityLevel.DEPARTMENT_MANAGER),
            # Dept staff
            ('programming.user@jct.pilot',     'Programming',                      'Programming Officer',       AuthorityLevel.DEPARTMENT_USER),
            ('marketing.user@jct.pilot',       'Marketing and Communications',     'Marketing Officer',         AuthorityLevel.DEPARTMENT_USER),
            ('technical.user@jct.pilot',       'Technical and Stage Management',   'Technical Assistant',       AuthorityLevel.DEPARTMENT_USER),
            ('foh.user@jct.pilot',             'FOH / Operations',                 'Operations Officer',        AuthorityLevel.DEPARTMENT_USER),
            ('contracts.user@jct.pilot',       'Contracts / Legal',                'Contracts Officer',         AuthorityLevel.DEPARTMENT_USER),
            ('scm.user@jct.pilot',             'SCM / Finance',                    'SCM Officer',               AuthorityLevel.DEPARTMENT_USER),
            ('ticketing.user@jct.pilot',       'Ticketing / Audience Coordination','Ticketing Officer',         AuthorityLevel.DEPARTMENT_USER),
            ('youth.user@jct.pilot',           'Youth Development',                'Youth Officer',             AuthorityLevel.DEPARTMENT_USER),
            ('governance.user@jct.pilot',      'Governance / M&E',                 'M&E Officer',              AuthorityLevel.DEPARTMENT_USER),
            ('hospitality.user@jct.pilot',     'Hospitality / Restaurant Operations','Hospitality Assistant',   AuthorityLevel.DEPARTMENT_USER),
            # Externals — minimal executive dept membership so they can log in
            ('client@jct.pilot',   'Executive Office', 'Board Member', AuthorityLevel.EXTERNAL),
            ('supplier@jct.pilot', 'Executive Office', 'Board Member', AuthorityLevel.EXTERNAL),
            ('artist@jct.pilot',   'Executive Office', 'Board Member', AuthorityLevel.EXTERNAL),
        ]
        for email, dept_name, position_title, authority in mappings:
            dept = departments[dept_name]
            position = positions.get((dept_name, position_title)) or positions[('Executive Office', 'Board Member')]
            can_manage = authority in {AuthorityLevel.EXECUTIVE, AuthorityLevel.GM, AuthorityLevel.DEPARTMENT_MANAGER}
            can_assign = can_manage
            can_approve = can_manage
            can_view = authority != AuthorityLevel.EXTERNAL
            can_raise = authority in {
                AuthorityLevel.EXECUTIVE,
                AuthorityLevel.GM,
                AuthorityLevel.DEPARTMENT_MANAGER,
                AuthorityLevel.DEPARTMENT_USER,
                AuthorityLevel.SPECIALIST,
            }
            UserDepartmentMembership.objects.update_or_create(
                organisation=org,
                user=users[email],
                department=dept,
                position=position,
                defaults={
                    'site': primary,
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

    # ------------------------------------------------------------------
    # Policy foundations
    # ------------------------------------------------------------------

    def _seed_policy_foundations(self, org, departments):
        policy_rows = [
            ('Marketing and Communications',     'marketing',   'marketing_readiness'),
            ('Technical and Stage Management',   'technical',   'technical_readiness'),
            ('FOH / Operations',                 'operations',  'foh_readiness'),
            ('Contracts / Legal',                'contracts',   'contract_review'),
            ('SCM / Finance',                    'suppliers',   'supplier_readiness'),
            ('Youth Development',                'youth',       'youth_sensitive'),
            ('Governance / M&E',                 'governance',  'governance_action'),
            ('Hospitality / Restaurant Operations','hospitality','hospitality_readiness'),
        ]
        for dept_name, module_key, scope in policy_rows:
            dept = departments[dept_name]
            ApprovalPolicy.objects.update_or_create(
                organisation=org,
                department=dept,
                module_key=module_key,
                record_type='',
                approval_scope=scope,
                defaults={
                    'required_authority_level': AuthorityLevel.DEPARTMENT_MANAGER,
                    'allow_executive_override': True,
                    'override_requires_reason': True,
                    'is_active': True,
                },
            )
            EvidenceRule.objects.update_or_create(
                organisation=org,
                department=dept,
                module_key=module_key,
                record_type='department_work',
                work_type='',
                defaults={
                    'evidence_required': True,
                    'accepted_mime_types': ['application/pdf', 'image/png', 'image/jpeg', 'text/csv'],
                    'requires_review': True,
                    'reviewer_authority_level': AuthorityLevel.DEPARTMENT_MANAGER,
                    'is_active': True,
                },
            )

    # ------------------------------------------------------------------
    # Workspaces (OperatingContext)
    # ------------------------------------------------------------------

    def _seed_workspaces(self, org, sites, venues, departments, users, today):
        jt_main = venues['Joburg Theatre – Main Auditorium']
        rt_main = venues['Roodepoort – Main Theatre']
        st_main = venues['Soweto Theatre – Main Auditorium']
        jt_site = sites['JT']
        rt_site = sites['RT']
        st_site = sites['ST']

        rows = [
            # title, type, venue, site, dept, owner, readiness, start_offset, end_offset, status
            (
                'The Big Bad Musical',
                'production',
                jt_main, jt_site,
                departments['Programming'],
                users['programming.manager@jct.pilot'],
                82,
                30, 60, 'confirmed',
            ),
            (
                'Schools Activation Tour',
                'workshop_series',
                rt_main, rt_site,
                departments['Youth Development'],
                users['youth.manager@jct.pilot'],
                55,
                14, 90, 'confirmed',
            ),
            (
                'Corporate Event – Client ABC',
                'venue_rental',
                st_main, st_site,
                departments['Programming'],
                users['gm.soweto@jct.pilot'],
                38,
                7, 7, 'provisional',
            ),
        ]
        workspaces = {}
        for title, ctx_type, venue, site, dept, owner, readiness, start_off, end_off, ws_status in rows:
            ws, _ = OperatingContext.objects.update_or_create(
                organisation=org,
                title=title,
                defaults={
                    'context_type': ctx_type,
                    'status': ws_status,
                    'priority': 'high' if readiness > 70 else 'medium',
                    'risk_level': 'low' if readiness > 70 else ('medium' if readiness > 45 else 'high'),
                    'site': site,
                    'venue': venue,
                    'department': dept,
                    'owner': owner,
                    'synopsis': f'JCT Pilot workspace: {title}.',
                    'start_date': today + timedelta(days=start_off),
                    'end_date': today + timedelta(days=end_off),
                    'opening_date': today + timedelta(days=start_off),
                    'readiness_score': readiness,
                    'ticketing_provider': 'webtickets',
                    'campaign_level': 'standard',
                },
            )
            workspaces[title] = ws
        return workspaces

    # ------------------------------------------------------------------
    # Intake
    # ------------------------------------------------------------------

    def _seed_intake(self, org, venues, users, today):
        IntakeRequest.objects.update_or_create(
            organisation=org,
            event_title='JCT Community Concert',
            defaults={
                'request_type': 'venue_booking',
                'status': 'submitted',
                'client_name': 'Hillbrow Arts Collective',
                'client_organisation': 'Hillbrow Arts Collective',
                'contact_email': 'client@jct.pilot',
                'contact_phone': '+27 11 000 1234',
                'requested_start_date': today + timedelta(days=50),
                'requested_end_date': today + timedelta(days=50),
                'preferred_venue': venues['Joburg Theatre – Main Auditorium'],
                'expected_audience': 800,
                'ticketing_required': True,
                'technical_summary': 'Full concert PA, LED stage wash, follow spots.',
                'foh_notes': 'VIP section required at front of house.',
                'accessibility_requirements': 'Wheelchair bays and loop system required.',
                'notes': 'Pilot intake request for Programming and Executive UAT.',
                'submitted_by': users['client@jct.pilot'],
            },
        )

    # ------------------------------------------------------------------
    # Calendar
    # ------------------------------------------------------------------

    def _seed_calendar(self, org, venues, departments, users, workspaces, today):
        rows = [
            (workspaces['The Big Bad Musical'], venues['Joburg Theatre – Main Auditorium'],
             'confirmed', 'performance', 30, time(18, 30), time(22, 0), 240, 90, 900),
            (workspaces['Schools Activation Tour'], venues['Roodepoort – Main Theatre'],
             'confirmed', 'workshop', 14, time(9, 0), time(13, 0), 30, 30, 200),
            (workspaces['Corporate Event – Client ABC'], venues['Soweto Theatre – Main Auditorium'],
             'provisional', 'other', 7, time(17, 0), time(22, 0), 120, 60, 400),
        ]
        for ws, venue, hold_type, purpose, days, start, end, setup, strike, audience in rows:
            VenueHold.objects.update_or_create(
                organisation=org,
                operating_context=ws,
                venue=venue,
                hold_date=today + timedelta(days=days),
                defaults={
                    'hold_type': hold_type,
                    'start_time': start,
                    'end_time': end,
                    'setup_buffer_minutes': setup,
                    'strike_buffer_minutes': strike,
                    'expected_audience': audience,
                    'purpose': purpose,
                    'notes': f'Pilot {hold_type} hold for {venue.name}.',
                    'held_by': users['programming.manager@jct.pilot'],
                },
            )
            CalendarSlot.objects.update_or_create(
                organisation=org,
                operating_context=ws,
                venue=venue,
                date=today + timedelta(days=days),
                defaults={
                    'slot_type': 'performance' if purpose == 'performance' else 'rehearsal',
                    'is_confirmed': hold_type == 'confirmed',
                    'start_time': start,
                    'end_time': end,
                    'setup_buffer_minutes': setup,
                    'strike_buffer_minutes': strike,
                    'expected_audience': audience,
                },
            )

    # ------------------------------------------------------------------
    # Department records
    # ------------------------------------------------------------------

    def _seed_department_records(self, org, venues, departments, users, workspaces, today):
        main = workspaces['The Big Bad Musical']
        tour = workspaces['Schools Activation Tour']
        corp = workspaces['Corporate Event – Client ABC']

        # Marketing — Campaign is OneToOne with operating_context; no title field
        campaign, _ = Campaign.objects.update_or_create(
            organisation=org,
            operating_context=main,
            defaults={
                'campaign_level': 'full',
                'budget': 85000,
                'status': 'active',
                'owner': users['marketing.manager@jct.pilot'],
                'notes': 'Launch campaign: digital, print and PR for The Big Bad Musical.',
            },
        )
        CampaignDeliverable.objects.update_or_create(
            organisation=org,
            campaign=campaign,
            title='Social media countdown reels',
            defaults={
                'deliverable_type': 'social_post',
                'status': 'in_progress',
                'due_date': today + timedelta(days=7),
                'owner_name': users['marketing.user@jct.pilot'].full_name,
            },
        )

        # Technical — TechnicalRider is OneToOne with operating_context
        TechnicalRider.objects.update_or_create(
            organisation=org,
            operating_context=main,
            defaults={
                'lighting': 'L-Acoustics K2 PA, 32-universe rig, LED wash and followspots.',
                'sound': 'Full concert PA front-of-house and monitoring.',
                'av': '4K projection on upstage screen.',
                'crew_size': 12,
                'status': 'submitted',
                'special_requirements': 'All equipment must be pre-rigged 48h before opening night.',
            },
        )

        # FOH — FOHPlan is OneToOne with operating_context
        foh_plan, _ = FOHPlan.objects.update_or_create(
            organisation=org,
            operating_context=main,
            defaults={
                'ushers': 12,
                'security': 4,
                'cleaning': 2,
                'vip_count': 30,
                'accessibility_provisions': 'Wheelchair bays mapped, loop system active.',
                'hospitality_notes': 'VIP entrance via Stage Door, bar stations x3 in foyer.',
                'status': 'planning',
            },
        )
        Incident.objects.update_or_create(
            organisation=org,
            operating_context=main,
            incident_type='health_safety',
            defaults={
                'foh_plan': foh_plan,
                'occurred_at': timezone.now(),
                'description': 'Main foyer may become congested at interval. Additional queue management staff recommended.',
                'response': 'FOH Manager to brief ushers on crowd flow procedures before each performance.',
                'reported_by': users['foh.manager@jct.pilot'],
                'severity': 'low',
            },
        )

        # Contracts
        ContractRecord.objects.update_or_create(
            organisation=org,
            operating_context=main,
            counterparty_name='Big Bad Productions (Pty) Ltd',
            contract_type='performance',
            defaults={
                'counterparty_type': 'artist',
                'value': 220000,
                'status': 'active',
                'effective_date': today - timedelta(days=7),
                'expiry_date': today + timedelta(days=65),
                'signatures_required': 2,
                'signatures_received': 2,
            },
        )
        ContractRecord.objects.update_or_create(
            organisation=org,
            operating_context=corp,
            counterparty_name='Client ABC Holdings',
            contract_type='venue_hire',
            defaults={
                'counterparty_type': 'client',
                'value': 95000,
                'status': 'draft',
                'effective_date': today + timedelta(days=5),
                'expiry_date': today + timedelta(days=10),
                'signatures_required': 2,
                'signatures_received': 0,
            },
        )

        # Supplier
        supplier, _ = Supplier.objects.update_or_create(
            organisation=org,
            name='ProLight Audio (Pty) Ltd',
            defaults={
                'category': 'Technical Equipment',
                'csd_number': 'MAAA0123456',
                'csd_verified': True,
                'bee_level': 'level_2',
                'contact_email': 'supplier@jct.pilot',
                'status': 'approved',
                'notes': 'Primary AV supplier. CSD verified.',
            },
        )
        SupplierDocument.objects.update_or_create(
            organisation=org,
            supplier=supplier,
            document_type='csd_registration',
            defaults={
                'status': 'approved',
                'file_name': 'prolight-csd-pack.pdf',
            },
        )
        SupplierEngagement.objects.update_or_create(
            organisation=org,
            supplier=supplier,
            operating_context=main,
            defaults={
                'role': 'AV equipment hire and technical crew',
                'value': 75000,
                'status': 'active',
            },
        )

        # Artist
        artist, _ = Artist.objects.update_or_create(
            organisation=org,
            legal_name='Big Bad Ensemble (Pty) Ltd',
            defaults={
                'professional_name': 'Big Bad Ensemble',
                'discipline': 'Musical Theatre',
                'contact_email': 'artist@jct.pilot',
                'standard_fee': 180000,
                'status': 'approved',
                'notes': 'Company artist. Technical rider accepted.',
            },
        )
        ArtistDocument.objects.update_or_create(
            organisation=org,
            artist=artist,
            document_type='technical_rider',
            defaults={
                'status': 'approved',
                'file_name': 'big-bad-technical-rider.pdf',
            },
        )
        ArtistEngagement.objects.update_or_create(
            organisation=org,
            artist=artist,
            operating_context=main,
            defaults={
                'role': 'Headline Production Company',
                'fee': 180000,
                'status': 'confirmed',
            },
        )

        # Ticketing — TicketingSetup is OneToOne with operating_context
        TicketingSetup.objects.update_or_create(
            organisation=org,
            operating_context=main,
            defaults={
                'provider': 'webtickets',
                'tickets_available': 900,
                'comps_allocated': 50,
                'setup_status': 'live',
                'notes': 'Webtickets integration active. Hold 50 seats for comp list.',
                'pricing_description': 'Standard R250 | Concession R150 | VIP R450',
            },
        )

        # Youth — YouthProject is OneToOne with operating_context
        youth_project, _ = YouthProject.objects.update_or_create(
            organisation=org,
            operating_context=tour,
            defaults={
                'target_learners': 600,
                'target_schools': 12,
                'age_range_min': 13,
                'age_range_max': 18,
                'safeguarding_notes': 'All facilitators DBS-checked. Consent forms required per learner.',
                'status': 'active',
            },
        )
        LearnerGroup.objects.update_or_create(
            organisation=org,
            youth_project=youth_project,
            name='Soweto Schools Cohort A',
            defaults={
                'description': 'Orlando East Secondary School — Grade 8–10 learners.',
            },
        )

        # Documents
        doc_rows = [
            (main,  users['marketing.manager@jct.pilot'],  'Big Bad Musical – Artwork Proof',     'marketing_asset', 'big-bad-artwork.pdf'),
            (main,  users['contracts.manager@jct.pilot'],  'Venue Use Agreement – Signed',        'contract',        'venue-use-agreement-signed.pdf'),
            (main,  users['scm.manager@jct.pilot'],        'ProLight Audio CSD Pack',             'csd_pack',        'prolight-csd-pack.pdf'),
            (main,  users['ticketing.manager@jct.pilot'],  'Ticketing Sales Import – Week 1',     'report',          'ticketing-sales-w1.csv'),
            (tour,  users['youth.manager@jct.pilot'],      'Schools Tour Consent Forms Batch 1',  'consent_form',    'school-consent-batch1.pdf'),
            (corp,  users['governance.manager@jct.pilot'], 'Corporate Event Risk Assessment',     'evidence',        'corp-risk-assessment.pdf'),
        ]
        for ws, uploader, title, doc_type, filename in doc_rows:
            self._document(org, ws, uploader, title, doc_type, filename)

    def _document(self, org, operating_context, uploaded_by, title, document_type, filename, mime_type='application/pdf', locked=False):
        doc, _ = Document.objects.update_or_create(
            organisation=org,
            title=title,
            defaults={
                'operating_context': operating_context,
                'document_type': document_type,
                'file_name': filename,
                'mime_type': mime_type,
                'uploaded_by': uploaded_by,
                'is_locked': locked,
            },
        )
        return doc

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    def _seed_governance(self, org, departments, users, today):
        Risk.objects.update_or_create(
            organisation=org,
            title='Ticket revenue below breakeven for The Big Bad Musical',
            defaults={
                'risk_level': 'high',
                'owner': users['governance.manager@jct.pilot'],
                'status': 'open',
                'description': 'Advance ticket sales are running 22% below target for Week 1.',
                'mitigation_plan': 'Accelerate social media campaign spend; review comp ticket allocations.',
            },
        )
        Risk.objects.update_or_create(
            organisation=org,
            title='Corporate Event contract not finalised in time',
            defaults={
                'risk_level': 'medium',
                'owner': users['contracts.manager@jct.pilot'],
                'status': 'open',
                'description': 'Client ABC contract draft not yet signed; event is 7 days away.',
                'mitigation_plan': 'Escalate to COO if draft not signed within 48 hours.',
            },
        )
        KPI.objects.update_or_create(
            organisation=org,
            name='Box office revenue – Q2',
            defaults={
                'owner_department': departments['Governance / M&E'],
                'target_value': 1500000,
                'unit': 'ZAR',
                'reporting_period': 'quarterly',
                'is_active': True,
            },
        )
        KPI.objects.update_or_create(
            organisation=org,
            name='Youth beneficiaries reached – Q2',
            defaults={
                'owner_department': departments['Youth Development'],
                'target_value': 600,
                'unit': 'learners',
                'reporting_period': 'quarterly',
                'is_active': True,
            },
        )
        ExecutiveAction.objects.update_or_create(
            organisation=org,
            title='Approve budget increase for Big Bad Musical marketing',
            defaults={
                'action_type': 'decision',
                'status': 'open',
                'department': departments['Executive Office'],
                'assigned_to': users['coo@jct.pilot'],
                'due_date': today + timedelta(days=5),
                'created_by': users['marketing.manager@jct.pilot'],
                'reason': 'Marketing manager requests R40k uplift to campaign budget due to low advance ticket sales.',
            },
        )

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def _seed_tasks(self, org, departments, users, workspaces, today):
        main = workspaces['The Big Bad Musical']
        task_rows = [
            (
                'Confirm technical rider with artist',
                departments['Technical and Stage Management'],
                users['technical.manager@jct.pilot'],
                users['technical.user@jct.pilot'],
                'high', 'in_progress', today + timedelta(days=5),
            ),
            (
                'Upload signed venue use agreement',
                departments['Contracts / Legal'],
                users['contracts.manager@jct.pilot'],
                users['contracts.user@jct.pilot'],
                'high', 'open', today + timedelta(days=2),
            ),
            (
                'Send press release to media list',
                departments['Marketing and Communications'],
                users['marketing.manager@jct.pilot'],
                users['marketing.user@jct.pilot'],
                'medium', 'open', today + timedelta(days=3),
            ),
            (
                'Finalise FOH staffing schedule',
                departments['FOH / Operations'],
                users['foh.manager@jct.pilot'],
                users['foh.user@jct.pilot'],
                'high', 'open', today + timedelta(days=7),
            ),
            (
                'Submit payment pack for ProLight Audio',
                departments['SCM / Finance'],
                users['scm.manager@jct.pilot'],
                users['scm.user@jct.pilot'],
                'medium', 'open', today + timedelta(days=10),
            ),
            (
                'Open ticket sales on Webtickets',
                departments['Ticketing / Audience Coordination'],
                users['ticketing.manager@jct.pilot'],
                users['ticketing.user@jct.pilot'],
                'high', 'done', today - timedelta(days=7),
            ),
            (
                'Collect learner consent forms – Soweto Schools Cohort A',
                departments['Youth Development'],
                users['youth.manager@jct.pilot'],
                users['youth.user@jct.pilot'],
                'high', 'in_progress', today + timedelta(days=12),
            ),
            (
                'Update Q2 KPI evidence pack',
                departments['Governance / M&E'],
                users['governance.manager@jct.pilot'],
                users['governance.user@jct.pilot'],
                'medium', 'open', today + timedelta(days=14),
            ),
            (
                'VIP pre-show hospitality setup plan',
                departments['Hospitality / Restaurant Operations'],
                users['hospitality.manager@jct.pilot'],
                users['hospitality.user@jct.pilot'],
                'medium', 'open', today + timedelta(days=20),
            ),
        ]
        for title, dept, assigned_by, assignee, priority, task_status, due_date in task_rows:
            Task.objects.update_or_create(
                organisation=org,
                title=title,
                defaults={
                    'operating_context': main,
                    'department': dept,
                    'assigned_by': assigned_by,
                    'assigned_to': assignee,
                    'priority': priority,
                    'status': task_status,
                    'due_date': due_date,
                },
            )

    # ------------------------------------------------------------------
    # Audit trail seed events
    # ------------------------------------------------------------------

    def _seed_audit(self, org, users):
        events = [
            ('org.created',       'Organisation', org.id,         {'name': org.name}),
            ('workspace.created', 'OperatingContext', None,        {'title': 'The Big Bad Musical'}),
            ('workspace.created', 'OperatingContext', None,        {'title': 'Schools Activation Tour'}),
            ('workspace.created', 'OperatingContext', None,        {'title': 'Corporate Event – Client ABC'}),
            ('contract.created',  'ContractRecord', None,          {'title': 'The Big Bad Musical – Venue Use Agreement'}),
            ('supplier.approved', 'Supplier', None,                {'name': 'ProLight Audio (Pty) Ltd'}),
            ('artist.confirmed',  'ArtistEngagement', None,        {'artist': 'Big Bad Ensemble'}),
            ('ticketing.activated','TicketingSetup', None,         {'provider': 'webtickets'}),
            ('risk.raised',       'Risk', None,                    {'title': 'Ticket revenue below breakeven'}),
            ('kpi.created',       'KPI', None,                     {'title': 'Box office revenue – Q2'}),
        ]
        actor = users['admin@jct.pilot']
        for event_type, target_type, target_id, payload in events:
            AuditEvent.objects.create(
                organisation=org,
                actor=actor,
                event_type=event_type,
                target_type=target_type,
                target_id=str(target_id) if target_id else '',
                payload=payload,
            )
