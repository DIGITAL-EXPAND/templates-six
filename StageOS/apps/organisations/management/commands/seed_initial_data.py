"""
Management command to seed initial StageOS data.

Usage:
    python manage.py seed_initial_data
    python manage.py seed_initial_data --org-name "My Theatre" --org-email "admin@theatre.org"
    python manage.py seed_initial_data --admin-email admin@example.com --admin-password secret123

This command is idempotent — safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify


# GRAP Chart of Accounts to seed
GRAP_ACCOUNTS = [
    ('1001', 'Cash and Cash Equivalents', 'asset_current'),
    ('1100', 'Trade and Other Receivables', 'asset_current'),
    ('1200', 'Inventories', 'asset_current'),
    ('1300', 'Property, Plant and Equipment', 'asset_non_current'),
    ('1400', 'Intangible Assets', 'asset_non_current'),
    ('2001', 'Trade and Other Payables', 'liability_current'),
    ('2100', 'Provisions', 'liability_current'),
    ('2200', 'Deferred Income (Conditional Grants)', 'deferred_income'),
    ('3001', 'Accumulated Surplus/(Deficit)', 'equity'),
    ('3100', 'Revaluation Reserve', 'equity'),
    ('4001', 'Government Grants (GRAP 23)', 'revenue_non_exchange'),
    ('4100', 'Box Office Revenue (GRAP 9)', 'revenue_exchange'),
    ('4200', 'Rental Revenue', 'revenue_exchange'),
    ('4300', 'Sponsorship Revenue', 'revenue_exchange'),
    ('4400', 'Donor Funding', 'donations'),
    ('5001', 'Employee Costs', 'expense_employee'),
    ('5100', 'Production Costs', 'expense_goods'),
    ('5200', 'Maintenance and Repairs', 'expense_goods'),
    ('5300', 'Marketing and Advertising', 'expense_goods'),
    ('5400', 'Administration', 'expense_other'),
    ('5500', 'Depreciation', 'expense_depreciation'),
    ('5600', 'Professional Services', 'expense_goods'),
]


class Command(BaseCommand):
    help = 'Seed initial StageOS data: organisation, admin user, GL accounts, and default venue.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org-name',
            default='My Theatre',
            help='Name of the organisation to create',
        )
        parser.add_argument(
            '--org-email',
            default='admin@theatre.local',
            help='Email for the organisation admin contact',
        )
        parser.add_argument(
            '--admin-email',
            default=None,
            help='Email address of the admin user to create',
        )
        parser.add_argument(
            '--admin-password',
            default=None,
            help='Password for the admin user',
        )

    def handle(self, *args, **options):
        from apps.organisations.models import Organisation, TenantEntityConfig, EntityType

        created_items = []
        skipped_items = []

        # ── 1. Organisation ───────────────────────────────────────────────────
        org_name = options['org_name']
        org_slug = slugify(org_name)

        org = Organisation.objects.filter(slug=org_slug).first()
        if org is None:
            org = Organisation.objects.create(
                name=org_name,
                slug=org_slug,
                is_active=True,
            )
            created_items.append(f'Organisation: {org.name}')
        else:
            skipped_items.append(f'Organisation: {org.name} (already exists)')

        # ── Entity config ─────────────────────────────────────────────────────
        _, config_created = TenantEntityConfig.objects.get_or_create(
            organisation=org,
            defaults={
                'entity_type': EntityType.PFMA_SCHEDULE_3A,
                'auditor_general_client': True,
                'pfma_applicable': True,
                'grap_reporting': True,
                'treasury_reporting_required': True,
                'shareholder_compact_required': True,
                'delegation_framework_required': True,
            },
        )
        if config_created:
            created_items.append('TenantEntityConfig: PFMA Schedule 3A')
        else:
            skipped_items.append('TenantEntityConfig (already exists)')

        # ── 2. Admin user ─────────────────────────────────────────────────────
        admin_email = options.get('admin_email')
        admin_password = options.get('admin_password')

        if admin_email and admin_password:
            from apps.accounts.models import User, UserType
            user, user_created = User.objects.get_or_create(
                email=admin_email,
                defaults={
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'user_type': UserType.INTERNAL_ADMIN,
                    'organisation': org,
                    'is_staff': True,
                    'is_superuser': True,
                },
            )
            if user_created:
                user.set_password(admin_password)
                user.save()
                created_items.append(f'Admin user: {admin_email}')
            else:
                skipped_items.append(f'Admin user: {admin_email} (already exists)')
        elif admin_email or admin_password:
            self.stdout.write(
                self.style.WARNING(
                    'Both --admin-email and --admin-password are required to create an admin user. Skipping.'
                )
            )

        # ── 3. GRAP Chart of Accounts ─────────────────────────────────────────
        from apps.finance.models import GLAccount

        gl_created = 0
        gl_skipped = 0
        for code, name, category in GRAP_ACCOUNTS:
            _, account_created = GLAccount.objects.get_or_create(
                organisation=org,
                account_code=code,
                defaults={
                    'name': name,
                    'category': category,
                    'is_active': True,
                },
            )
            if account_created:
                gl_created += 1
            else:
                gl_skipped += 1

        if gl_created:
            created_items.append(f'GL Accounts: {gl_created} created')
        if gl_skipped:
            skipped_items.append(f'GL Accounts: {gl_skipped} already existed')

        # ── 4. Default Venue ──────────────────────────────────────────────────
        # Venue requires a Site (FK). Create a default site first if needed.
        from apps.structure.models import Site, Venue

        existing_venues = Venue.objects.filter(organisation=org).count()
        if existing_venues == 0:
            site, site_created = Site.objects.get_or_create(
                organisation=org,
                code='HQ',
                defaults={
                    'name': org_name,
                    'address': '',
                    'city': 'Johannesburg',
                    'province': 'Gauteng',
                    'country': 'South Africa',
                    'is_active': True,
                },
            )
            if site_created:
                created_items.append(f'Site: {site.name}')
            else:
                skipped_items.append(f'Site: {site.name} (already exists)')

            venue = Venue.objects.create(
                organisation=org,
                name='Main Theatre',
                site=site,
                venue_type='performance',
                capacity=500,
                is_active=True,
            )
            created_items.append(f'Venue: {venue.name} (capacity {venue.capacity})')
        else:
            skipped_items.append(f'Venue: organisation already has {existing_venues} venue(s)')

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== StageOS Seed Summary ==='))

        if created_items:
            self.stdout.write(self.style.SUCCESS('Created:'))
            for item in created_items:
                self.stdout.write(self.style.SUCCESS(f'  + {item}'))

        if skipped_items:
            self.stdout.write(self.style.WARNING('Skipped (already exist):'))
            for item in skipped_items:
                self.stdout.write(self.style.WARNING(f'  ~ {item}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done.'))
