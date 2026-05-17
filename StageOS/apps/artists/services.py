import datetime

from apps.audit.models import AuditEvent
from apps.audit.services import AuditService

_REQUIRED_DOCUMENT_TYPES = {'id_copy', 'bank_confirmation'}


def upload_artist_document(artist, user, document_type, file_name):
    from .models import ArtistDocument
    doc, _ = ArtistDocument.objects.get_or_create(
        artist=artist,
        document_type=document_type,
        defaults={'organisation': artist.organisation},
    )
    doc.status = 'uploaded'
    doc.file_name = file_name
    doc.save(update_fields=['status', 'file_name', 'updated_at'])

    uploaded_types = set(
        ArtistDocument.objects.filter(
            artist=artist,
            status__in=('uploaded', 'verified'),
        ).values_list('document_type', flat=True)
    )
    if _REQUIRED_DOCUMENT_TYPES.issubset(uploaded_types):
        artist.status = 'contract_ready'
        artist.save(update_fields=['status', 'updated_at'])

    AuditEvent.objects.create(
        organisation=artist.organisation,
        actor=user,
        event_type='ARTIST_DOCUMENT_UPLOADED',
        payload={
            'artist_id': str(artist.id),
            'document_type': document_type,
            'file_name': file_name,
        },
    )
    return doc


def confirm_engagement(engagement, user):
    engagement.status = 'confirmed'
    engagement.save(update_fields=['status', 'updated_at'])
    AuditEvent.objects.create(
        organisation=engagement.organisation,
        actor=user,
        event_type='ARTIST_ENGAGEMENT_CONFIRMED',
        payload={
            'engagement_id': str(engagement.id),
            'artist_id': str(engagement.artist_id),
            'context_id': str(engagement.operating_context_id),
        },
    )
    return engagement


def verify_artist_document(doc, user, comment=''):
    old_status = doc.status
    doc.status = 'verified'
    doc.verified_by = user
    doc.verified_at = datetime.datetime.now(tz=datetime.timezone.utc)
    doc.save(update_fields=['status', 'verified_by', 'verified_at', 'updated_at'])
    AuditService.record(
        organisation=doc.organisation,
        actor=user,
        event_type='ARTIST_DOCUMENT_VERIFIED',
        target_type='ArtistDocument',
        target_id=doc.id,
        old_value=old_status,
        new_value=doc.status,
        reason=comment,
    )
    return doc


def reject_artist_document(doc, user, comment=''):
    old_status = doc.status
    doc.status = 'rejected'
    doc.verified_by = user
    doc.verified_at = datetime.datetime.now(tz=datetime.timezone.utc)
    doc.save(update_fields=['status', 'verified_by', 'verified_at', 'updated_at'])
    AuditService.record(
        organisation=doc.organisation,
        actor=user,
        event_type='ARTIST_DOCUMENT_REJECTED',
        target_type='ArtistDocument',
        target_id=doc.id,
        old_value=old_status,
        new_value=doc.status,
        reason=comment,
    )
    return doc
