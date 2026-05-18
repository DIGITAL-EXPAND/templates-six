import uuid
from django.core.management.base import BaseCommand, CommandError
from apps.audit.models import AuditEvent


class Command(BaseCommand):
    help = 'Verify the audit event hash chain for a given organisation.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org-id',
            type=str,
            required=True,
            help='UUID of the organisation whose audit chain should be verified.',
        )

    def handle(self, *args, **options):
        org_id_str = options['org_id']
        try:
            org_id = uuid.UUID(org_id_str)
        except ValueError:
            raise CommandError(f'Invalid UUID: {org_id_str}')

        events = list(
            AuditEvent.objects.filter(organisation_id=org_id)
            .order_by('created_at')
        )

        if not events:
            self.stdout.write(self.style.WARNING('No audit records found for this organisation.'))
            return

        expected_previous = ''
        for event in events:
            recomputed = event.compute_hash(expected_previous)
            if recomputed != event.record_hash:
                self.stdout.write(
                    self.style.ERROR(f'MISMATCH at record {event.id}')
                )
                return
            expected_previous = event.record_hash

        self.stdout.write(
            self.style.SUCCESS(f'Chain valid: {len(events)} records checked')
        )
