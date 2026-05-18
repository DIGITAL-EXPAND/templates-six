import uuid
from django.db import models
from common.models import TenantOwnedModel


class RequestType(models.TextChoices):
    VIP_HOSTING = 'vip_hosting', 'VIP Hosting'
    CATERING = 'catering', 'Catering'
    PRIVATE_DINING = 'private_dining', 'Private Dining'
    RESTAURANT_RESERVATION = 'restaurant_reservation', 'Restaurant Reservation'
    OTHER = 'other', 'Other'


class HospitalityStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    CONFIRMED = 'confirmed', 'Confirmed'
    DECLINED = 'declined', 'Declined'
    COMPLETED = 'completed', 'Completed'


class NoteType(models.TextChoices):
    INTERNAL = 'internal', 'Internal'
    CLIENT_FACING = 'client_facing', 'Client Facing'


class HospitalityRequest(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hospitality_requests',
    )
    request_type = models.CharField(max_length=30, choices=RequestType.choices)
    event_date = models.DateField()
    guest_count = models.PositiveIntegerField(default=1)
    special_requirements = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=20, choices=HospitalityStatus.choices, default=HospitalityStatus.DRAFT,
    )
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hospitality_assignments',
    )
    notes_text = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT,
        related_name='created_hospitality_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date', '-created_at']

    def __str__(self):
        return f'{self.get_request_type_display()} — {self.contact_name} ({self.event_date})'


class HospitalityNote(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitality_request = models.ForeignKey(
        HospitalityRequest, on_delete=models.CASCADE, related_name='notes',
    )
    note_text = models.TextField()
    note_type = models.CharField(
        max_length=20, choices=NoteType.choices, default=NoteType.INTERNAL,
    )
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT,
        related_name='hospitality_notes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Note on {self.hospitality_request}'
