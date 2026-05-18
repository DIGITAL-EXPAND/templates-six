import hashlib
import json
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
    previous_hash = models.CharField(max_length=64, blank=True)
    record_hash = models.CharField(max_length=64, editable=False, blank=True)

    objects = AuditEventManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} @ {self.created_at}'

    def compute_hash(self, previous_hash: str) -> str:
        payload = json.dumps({
            'previous_hash': previous_hash,
            'organisation_id': str(self.organisation_id),
            'actor_id': str(self.actor_id) if self.actor_id else '',
            'event_type': self.event_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'payload': self.payload,
            'created_at': self.created_at.isoformat(),
        }, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('AuditEvent records cannot be updated.')
        # Compute hash chain before saving
        prior = (
            AuditEvent.objects.filter(organisation_id=self.organisation_id)
            .order_by('-created_at')
            .first()
        )
        self.previous_hash = prior.record_hash if prior else ''
        # created_at is auto_now_add so we need to save first, then compute hash
        # Use a temporary save approach: save to get created_at, then update hash directly
        super().save(*args, **kwargs)
        self.record_hash = self.compute_hash(self.previous_hash)
        # Bypass the immutability guard with raw SQL — only called from this save()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE audit_auditevent SET record_hash = %s WHERE id = %s',
                [self.record_hash, str(self.id)],
            )

    def delete(self, *args, **kwargs):
        raise ValidationError('AuditEvent records cannot be deleted.')
