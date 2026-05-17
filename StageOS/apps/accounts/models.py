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
