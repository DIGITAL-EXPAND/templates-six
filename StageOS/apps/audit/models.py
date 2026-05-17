import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


class AuditEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('AuditEvent records cannot be updated.')

    def delete(self):
        raise ValidationError('AuditEvent records cannot be deleted.')


class AuditEventManager(models.Manager):
    def get_queryset(self):
        return AuditEventQuerySet(self.model, using=self._db)


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.PROTECT,
        related_name='audit_events',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_events',
    )
    event_type = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AuditEventManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} @ {self.created_at}'

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('AuditEvent records cannot be updated.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('AuditEvent records cannot be deleted.')
