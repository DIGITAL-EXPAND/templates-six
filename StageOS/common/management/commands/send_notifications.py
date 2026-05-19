"""
Management command: send_notifications
Checks for overdue/expiring items and creates in-app notifications.
Run daily via cron or celery beat: python manage.py send_notifications
"""
import logging
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate in-app notifications for overdue tasks, expiring contracts, pending approvals'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview without creating notifications')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = date.today()
        thirty_days = today + timedelta(days=30)
        created = 0

        self.stdout.write('=== send_notifications ===')

        # --- Overdue tasks ---
        try:
            from apps.tasks.models import Task
            overdue = Task.objects.filter(
                status__in=['open', 'in_progress'],
                due_date__lt=today,
                assigned_to__isnull=False,
            ).select_related('assigned_to', 'organisation')

            for task in overdue:
                msg = f'Task overdue: "{task.title}" was due {task.due_date}'
                if not dry_run:
                    created += self._notify(
                        task.assigned_to, task.title, msg,
                        'task_overdue', task.organisation_id, str(task.id),
                    )
                else:
                    self.stdout.write(f'  [DRY] Overdue task → {task.assigned_to}: {msg}')
        except Exception as e:
            logger.warning(f'Overdue tasks check failed: {e}')

        # --- Contracts expiring in 30 days ---
        try:
            from apps.contracts.models import ContractRecord
            expiring = ContractRecord.objects.filter(
                expiry_date__lte=thirty_days,
                expiry_date__gte=today,
                status__in=['signed', 'counter_signed'],
            ).select_related('organisation')

            for contract in expiring:
                days_left = (contract.expiry_date - today).days
                msg = f'Contract with {contract.counterparty_name} expires in {days_left} days ({contract.expiry_date})'
                title = f'Contract expiring: {contract.counterparty_name}'
                # Notify organisation managers/admins
                from apps.accounts.models import User
                managers = User.objects.filter(
                    organisation_id=contract.organisation_id,
                    user_type__in=['internal_admin', 'executive', 'manager'],
                    is_active=True,
                )
                for user in managers:
                    if not dry_run:
                        created += self._notify(
                            user, title, msg,
                            'contract_expiring', contract.organisation_id, str(contract.id),
                        )
                    else:
                        self.stdout.write(f'  [DRY] Expiring contract → {user}: {msg}')
        except Exception as e:
            logger.warning(f'Contract expiry check failed: {e}')

        # --- Approvals pending > 48h ---
        try:
            from apps.approvals.models import ApprovalRequest
            cutoff = timezone.now() - timedelta(hours=48)
            stale = ApprovalRequest.objects.filter(
                decision='pending',
                requested_at__lt=cutoff,
                requested_by__isnull=False,
            ).select_related('requested_by', 'organisation')

            for approval in stale:
                msg = f'Approval pending for over 48 hours: {approval}'
                title = 'Approval stale: awaiting decision'
                if not dry_run:
                    created += self._notify(
                        approval.requested_by, title, msg,
                        'approval_stale', approval.organisation_id, str(approval.id),
                    )
                else:
                    self.stdout.write(f'  [DRY] Stale approval → {approval.requested_by}: {msg}')
        except Exception as e:
            logger.warning(f'Stale approvals check failed: {e}')

        self.stdout.write(self.style.SUCCESS(f'Done. {created} notifications created.'))

    def _notify(self, user, title, message, notification_type, organisation_id, reference_id=''):
        try:
            from apps.tasks.models import Notification
            obj, was_created = Notification.objects.get_or_create(
                recipient=user,
                organisation_id=organisation_id,
                notification_type=notification_type,
                related_id=reference_id,
                read_at__isnull=True,
                defaults={
                    'title': title,
                    'message': message,
                },
            )
            return 1 if was_created else 0
        except Exception as e:
            logger.warning(f'Could not create notification: {e}')
            return 0
