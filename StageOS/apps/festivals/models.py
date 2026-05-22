import uuid
from django.db import models
from common.models import TenantOwnedModel


class FestivalStatus(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    OPEN_SUBMISSIONS = 'open_submissions', 'Open for Programme Submissions'
    PROGRAMME_FINALISED = 'programme_finalised', 'Programme Finalised'
    ACCREDITATION_OPEN = 'accreditation_open', 'Accreditation Open'
    IN_PROGRESS = 'in_progress', 'Festival in Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Festival(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    edition = models.CharField(max_length=50, blank=True, help_text='e.g. 2025 or 12th Edition')
    status = models.CharField(max_length=25, choices=FestivalStatus.choices, default=FestivalStatus.PLANNING)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    artistic_director = models.CharField(max_length=255, blank=True)
    expected_attendance = models.PositiveIntegerField(default=0)
    max_accreditation = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FestivalVenue(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name='venues')
    venue = models.ForeignKey('structure.Venue', on_delete=models.PROTECT, related_name='festival_venues')
    venue_code = models.CharField(max_length=10, blank=True, help_text='Short code e.g. MH, ST')
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


class FestivalPassType(models.TextChoices):
    FULL_FESTIVAL = 'full_festival', 'Full Festival Pass'
    DAY_PASS = 'day_pass', 'Day Pass'
    ARTIST = 'artist', 'Artist / Performer'
    PRESS = 'press', 'Press / Media'
    ACCREDITATION = 'accreditation', 'Industry Accreditation'
    VIP = 'vip', 'VIP / Sponsor'
    CREW = 'crew', 'Crew / Production'
    VOLUNTEER = 'volunteer', 'Volunteer'


class FestivalPass(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name='passes')
    pass_type = models.CharField(max_length=20, choices=FestivalPassType.choices)
    holder_name = models.CharField(max_length=255)
    holder_email = models.EmailField(blank=True)
    organisation_name = models.CharField(max_length=255, blank=True)
    pass_number = models.CharField(max_length=50, blank=True)
    valid_days = models.CharField(max_length=255, blank=True, help_text='Comma-separated dates or "all"')
    venue_access = models.CharField(max_length=255, blank=True, help_text='Venue codes or "all"')
    is_active = models.BooleanField(default=True)
    issued_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pass_number:
            prefix = self.pass_type[:2].upper()
            count = FestivalPass.objects.filter(festival=self.festival).count() + 1
            self.pass_number = f'{prefix}-{count:04d}'
        super().save(*args, **kwargs)


class FestivalVenueSlot(TenantOwnedModel):
    """Multi-venue scheduling slot for festival programming."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name='venue_slots')
    festival_venue = models.ForeignKey(FestivalVenue, on_delete=models.CASCADE, related_name='slots')
    operating_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='festival_slots',
        help_text='The show/performance scheduled in this slot',
    )
    slot_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_label = models.CharField(max_length=100, blank=True)
    is_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['slot_date', 'start_time']
