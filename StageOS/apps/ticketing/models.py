import uuid
from django.db import models
from common.models import TenantOwnedModel


class TicketingProvider(models.TextChoices):
    WEBTICKETS = 'webtickets', 'Webtickets'
    COMPUTICKET = 'computicket', 'Computicket'
    TICKETPRO = 'ticketpro', 'Ticketpro'
    INTERNAL_RSVP = 'internal_rsvp', 'Internal RSVP'
    NOT_TICKETED = 'not_ticketed', 'Not Ticketed'


class SetupStatus(models.TextChoices):
    AWAITING_SETUP = 'awaiting_setup', 'Awaiting Setup'
    IN_PROGRESS = 'in_progress', 'In Progress'
    LIVE = 'live', 'Live'
    CLOSED = 'closed', 'Closed'


class SettlementStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    SETTLED = 'settled', 'Settled'
    NOT_APPLICABLE = 'not_applicable', 'Not Applicable'


class TicketingSetup(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='ticketing_setup',
    )
    provider = models.CharField(max_length=20, choices=TicketingProvider.choices)
    booking_link = models.URLField(blank=True)
    pricing_description = models.TextField(blank=True)
    comps_allocated = models.IntegerField(default=0)
    comps_used = models.IntegerField(default=0)
    setup_status = models.CharField(
        max_length=20, choices=SetupStatus.choices,
        default=SetupStatus.AWAITING_SETUP,
    )
    sales_imported = models.BooleanField(default=False)
    tickets_sold = models.IntegerField(default=0)
    tickets_available = models.IntegerField(default=0)
    settlement_status = models.CharField(
        max_length=20, choices=SettlementStatus.choices,
        default=SettlementStatus.PENDING,
    )
    settlement_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Ticketing: {self.operating_context}'


class SalesImport(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticketing_setup = models.ForeignKey(
        TicketingSetup, on_delete=models.CASCADE, related_name='sales_imports',
    )
    import_date = models.DateField(auto_now_add=True)
    tickets_sold = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    imported_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='sales_imports',
    )
    source_file = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sales_imports',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-import_date']

    def __str__(self):
        return f'SalesImport {self.import_date}: {self.tickets_sold} tickets'
