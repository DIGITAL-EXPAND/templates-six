from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from .models import SetupStatus, SettlementStatus


def create_ticketing_setup(context, user, data):
    from .models import TicketingSetup
    setup = TicketingSetup.objects.create(
        organisation=context.organisation,
        operating_context=context,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='ticketing.setup_created',
        payload={
            'setup_id': str(setup.id),
            'context_id': str(context.id),
            'provider': setup.provider,
        },
    )
    return setup


def go_live(ticketing_setup, user):
    allowed = {SetupStatus.AWAITING_SETUP, SetupStatus.IN_PROGRESS}
    if ticketing_setup.setup_status not in allowed:
        raise ValidationError(
            {'detail': 'Can only go live from awaiting_setup or in_progress.'}
        )
    ticketing_setup.setup_status = SetupStatus.LIVE
    ticketing_setup.save(update_fields=['setup_status', 'updated_at'])
    AuditEvent.objects.create(
        organisation=ticketing_setup.organisation,
        actor=user,
        event_type='ticketing.live',
        payload={'setup_id': str(ticketing_setup.id)},
    )
    return ticketing_setup


def import_sales(ticketing_setup, user, data):
    from .models import SalesImport
    if ticketing_setup.setup_status != SetupStatus.LIVE:
        raise ValidationError(
            {'detail': 'Ticketing must be live before importing sales.'}
        )
    if data.get('source_file') is None:
        raise ValidationError({
            'source_file': 'A source file is required before ticket sales can be imported.'
        })
    tickets_sold = data['tickets_sold']
    revenue = data['revenue']
    sale = SalesImport.objects.create(
        organisation=ticketing_setup.organisation,
        ticketing_setup=ticketing_setup,
        tickets_sold=tickets_sold,
        revenue=revenue,
        imported_by=user,
        source_file=data.get('source_file'),
        notes=data.get('notes', ''),
    )
    ticketing_setup.tickets_sold += tickets_sold
    ticketing_setup.sales_imported = True
    ticketing_setup.save(update_fields=['tickets_sold', 'sales_imported', 'updated_at'])
    AuditEvent.objects.create(
        organisation=ticketing_setup.organisation,
        actor=user,
        event_type='ticketing.sales_imported',
        payload={
            'setup_id': str(ticketing_setup.id),
            'sales_import_id': str(sale.id),
            'tickets_sold': tickets_sold,
            'revenue': str(revenue),
        },
    )
    return sale


def settle_ticketing(ticketing_setup, user, amount):
    if not ticketing_setup.sales_imported:
        raise ValidationError(
            {'detail': 'Sales must be imported before settlement.'}
        )
    ticketing_setup.settlement_status = SettlementStatus.SETTLED
    ticketing_setup.settlement_amount = amount
    ticketing_setup.save(update_fields=['settlement_status', 'settlement_amount', 'updated_at'])
    AuditEvent.objects.create(
        organisation=ticketing_setup.organisation,
        actor=user,
        event_type='ticketing.settled',
        payload={
            'setup_id': str(ticketing_setup.id),
            'settlement_amount': str(amount),
        },
    )
    return ticketing_setup
