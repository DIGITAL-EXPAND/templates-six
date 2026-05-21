import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserType(models.TextChoices):
    INTERNAL_ADMIN = 'internal_admin', 'Internal Admin'
    EXECUTIVE = 'executive', 'Executive'
    MANAGER = 'manager', 'Manager'
    STAFF = 'staff', 'Staff'
    READ_ONLY = 'read_only', 'Read Only'
    SUPPLIER_EXTERNAL = 'supplier_external', 'Supplier External'
    ARTIST_EXTERNAL = 'artist_external', 'Artist External'
    CLIENT_EXTERNAL = 'client_external', 'Client External'
    YOUTH_EXTERNAL = 'youth_external', 'Youth External'
    INTEGRATION_SERVICE = 'integration_service', 'Integration Service'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', UserType.INTERNAL_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STAFF,
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    data_processing_consent = models.BooleanField(default=False)
    data_processing_consent_date = models.DateTimeField(null=True, blank=True)
    invite_token = models.UUIDField(null=True, blank=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

from .popia_models import DataConsent  # noqa: F401 - ensures Django tracks this model


# ── Leave Requests ────────────────────────────────────────────────────────────

from common.models import TenantOwnedModel  # noqa: E402 - already imported in popia_models

class LeaveType(models.TextChoices):
    ANNUAL = 'annual', 'Annual Leave'
    SICK = 'sick', 'Sick Leave'
    FAMILY = 'family', 'Family Responsibility Leave'
    MATERNITY = 'maternity', 'Maternity Leave'
    PATERNITY = 'paternity', 'Paternity Leave'
    STUDY = 'study', 'Study Leave'
    UNPAID = 'unpaid', 'Unpaid Leave'
    OTHER = 'other', 'Other'

class LeaveStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Approval'
    APPROVED = 'approved', 'Approved'
    DECLINED = 'declined', 'Declined'
    CANCELLED = 'cancelled', 'Cancelled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'

class LeaveRequest(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('User', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    status = models.CharField(max_length=15, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leave_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    declined_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
