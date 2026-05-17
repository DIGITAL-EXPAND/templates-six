import uuid
from django.db import models
from common.models import TenantOwnedModel


class YouthProjectStatus(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    RECRUITING = 'recruiting', 'Recruiting'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class ActivityType(models.TextChoices):
    CLASS_SESSION = 'class_session', 'Class Session'
    SECTIONAL_REHEARSAL = 'sectional_rehearsal', 'Sectional Rehearsal'
    FULL_REHEARSAL = 'full_rehearsal', 'Full Rehearsal'
    WORKSHOP = 'workshop', 'Workshop'
    MASTERCLASS = 'masterclass', 'Masterclass'
    PERFORMANCE = 'performance', 'Performance'
    ASSESSMENT = 'assessment', 'Assessment'
    SHOWCASE = 'showcase', 'Showcase'
    FIELD_TRIP = 'field_trip', 'Field Trip'
    OTHER = 'other', 'Other'


class Recurrence(models.TextChoices):
    ONCE = 'once', 'Once'
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    FORTNIGHTLY = 'fortnightly', 'Fortnightly'
    MONTHLY = 'monthly', 'Monthly'
    CUSTOM = 'custom', 'Custom'


class SessionStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class AssessmentType(models.TextChoices):
    FORMATIVE = 'formative', 'Formative'
    SUMMATIVE = 'summative', 'Summative'
    PORTFOLIO = 'portfolio', 'Portfolio'
    PERFORMANCE = 'performance', 'Performance'
    SELF_ASSESSMENT = 'self_assessment', 'Self Assessment'
    PEER_ASSESSMENT = 'peer_assessment', 'Peer Assessment'


class OutputType(models.TextChoices):
    CONCERT = 'concert', 'Concert'
    EXHIBITION = 'exhibition', 'Exhibition'
    PERFORMANCE = 'performance', 'Performance'
    PRESENTATION = 'presentation', 'Presentation'
    RECORDING = 'recording', 'Recording'
    PUBLICATION = 'publication', 'Publication'
    OTHER = 'other', 'Other'


class YouthProject(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operating_context = models.OneToOneField(
        'contexts.OperatingContext', on_delete=models.PROTECT,
        related_name='youth_project',
    )
    target_learners = models.IntegerField(default=0)
    target_schools = models.IntegerField(default=0)
    age_range_min = models.IntegerField(null=True, blank=True)
    age_range_max = models.IntegerField(null=True, blank=True)
    safeguarding_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=YouthProjectStatus.choices,
        default=YouthProjectStatus.PLANNING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Youth Project: {self.operating_context}'


class Activity(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='activities',
    )
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='youth_activities',
    )
    space = models.ForeignKey(
        'structure.Space', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='youth_activities',
    )
    recurrence = models.CharField(max_length=20, choices=Recurrence.choices, default=Recurrence.ONCE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    day_of_week = models.CharField(max_length=100, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    facilitator_count = models.IntegerField(default=1)
    max_learners = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_activity_type_display()})'


class Session(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='sessions',
    )
    session_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.ForeignKey(
        'structure.Venue', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='youth_sessions',
    )
    status = models.CharField(
        max_length=20, choices=SessionStatus.choices, default=SessionStatus.SCHEDULED,
    )
    facilitator_notes = models.TextField(blank=True)
    attendance_captured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['session_date', 'start_time']

    def __str__(self):
        return f'{self.activity.name} on {self.session_date}'


class LearnerGroup(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='learner_groups',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FacilitatorAssignment(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='facilitator_assignments',
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE,
        null=True, blank=True, related_name='facilitator_assignments',
    )
    facilitator = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='facilitated_projects',
    )
    role = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_vetted = models.BooleanField(default=False)
    vetting_date = models.DateField(null=True, blank=True)
    vetting_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('youth_project', 'facilitator', 'activity')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.facilitator} as {self.role}'


class ConsentRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='consent_records',
    )
    learner_identifier = models.CharField(max_length=100)
    learner_group = models.ForeignKey(
        LearnerGroup, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='consent_records',
    )
    guardian_consent_received = models.BooleanField(default=False)
    consent_date = models.DateField(null=True, blank=True)
    consent_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='consent_records',
    )
    photo_consent = models.BooleanField(default=False)
    data_processing_consent = models.BooleanField(default=False)
    withdrawal_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('youth_project', 'learner_identifier')]
        ordering = ['learner_identifier']

    def __str__(self):
        return f'Consent: {self.learner_identifier} [{self.youth_project}]'


class AttendanceRecord(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='attendance_records',
    )
    learner_identifier = models.CharField(max_length=100)
    learner_group = models.ForeignKey(
        LearnerGroup, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='attendance_records',
    )
    present = models.BooleanField(default=False)
    arrival_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('session', 'learner_identifier')]
        ordering = ['learner_identifier']

    def __str__(self):
        return f'{"P" if self.present else "A"}: {self.learner_identifier} @ {self.session}'


class Assessment(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='assessments',
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assessments',
    )
    learner_identifier = models.CharField(max_length=100)
    assessment_type = models.CharField(max_length=30, choices=AssessmentType.choices)
    score = models.CharField(max_length=50, blank=True)
    assessor = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='youth_assessments',
    )
    assessment_date = models.DateField()
    notes = models.TextField(blank=True)
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='youth_assessments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return f'{self.assessment_type}: {self.learner_identifier}'


class ShowcaseOutput(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youth_project = models.ForeignKey(
        YouthProject, on_delete=models.CASCADE, related_name='showcase_outputs',
    )
    output_context = models.ForeignKey(
        'contexts.OperatingContext', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='youth_showcases',
    )
    title = models.CharField(max_length=255)
    output_type = models.CharField(max_length=20, choices=OutputType.choices)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    evidence_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='showcase_evidence',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_output_type_display()})'
