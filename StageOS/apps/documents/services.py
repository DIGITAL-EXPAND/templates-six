from django.utils import timezone
from django.utils.text import get_valid_filename
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService


def upload_document(context, user, data):
    from .models import Document
    doc = Document.objects.create(
        operating_context=context,
        organisation=context.organisation,
        uploaded_by=user,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='document.uploaded',
        payload={
            'document_id': str(doc.id),
            'title': doc.title,
            'context_id': str(context.id),
        },
    )
    return doc


def store_uploaded_document(context, user, uploaded_file, data):
    from .models import Document

    safe_file_name = get_valid_filename(uploaded_file.name)
    uploaded_file.name = safe_file_name
    doc = Document.objects.create(
        operating_context=context,
        organisation=context.organisation,
        uploaded_by=user,
        file=uploaded_file,
        file_name=safe_file_name,
        file_size=uploaded_file.size,
        mime_type=getattr(uploaded_file, 'content_type', '') or '',
        title=data['title'],
        document_type=data['document_type'],
        version=data.get('version', 1),
    )
    doc.storage_ref = doc.file.name
    doc.save(update_fields=['storage_ref', 'updated_at'])
    AuditService.record(
        organisation=context.organisation,
        actor=user,
        event_type='document.file_uploaded',
        target_type='Document',
        target_id=doc.id,
        payload={
            'document_id': str(doc.id),
            'title': doc.title,
            'context_id': str(context.id),
            'file_name': doc.file_name,
            'file_size': doc.file_size,
            'mime_type': doc.mime_type,
            'storage_ref': doc.storage_ref,
        },
    )
    return doc


def record_document_download(document, user):
    AuditService.record(
        organisation=document.organisation,
        actor=user,
        event_type='document.downloaded',
        target_type='Document',
        target_id=document.id,
        payload={
            'document_id': str(document.id),
            'context_id': str(document.operating_context_id),
            'file_name': document.file_name,
        },
    )


def accept_evidence(submission, user):
    submission.accepted = True
    submission.accepted_by = user
    submission.accepted_at = timezone.now()
    submission.rejected = False
    submission.rejected_by = None
    submission.rejected_at = None
    submission.rejection_reason = ''
    submission.save(update_fields=[
        'accepted', 'accepted_by', 'accepted_at',
        'rejected', 'rejected_by', 'rejected_at', 'rejection_reason',
        'updated_at',
    ])

    if submission.task and submission.task.evidence_required:
        submission.task.evidence_provided = True
        submission.task.save(update_fields=['evidence_provided', 'updated_at'])

    AuditEvent.objects.create(
        organisation=submission.organisation,
        actor=user,
        event_type='evidence.accepted',
        payload={
            'submission_id': str(submission.id),
            'context_id': str(submission.operating_context_id),
        },
    )
    return submission


def reject_evidence(submission, user, reason):
    if not reason or not reason.strip():
        raise ValidationError({'reason': 'A rejection reason is required.'})
    submission.accepted = False
    submission.accepted_by = None
    submission.accepted_at = None
    submission.rejected = True
    submission.rejected_by = user
    submission.rejected_at = timezone.now()
    submission.rejection_reason = reason.strip()
    submission.save(update_fields=[
        'accepted', 'accepted_by', 'accepted_at',
        'rejected', 'rejected_by', 'rejected_at', 'rejection_reason',
        'updated_at',
    ])

    if submission.task and submission.task.evidence_required:
        has_accepted = submission.task.evidence_submissions.filter(accepted=True).exclude(id=submission.id).exists()
        submission.task.evidence_provided = has_accepted
        submission.task.save(update_fields=['evidence_provided', 'updated_at'])

    if submission.task and submission.task.assigned_to:
        from apps.tasks.services import _notify
        _notify(
            recipient=submission.task.assigned_to,
            actor=user,
            notification_type='evidence_rejected',
            title='Your uploaded file was not accepted',
            message=reason or 'No reason provided',
            task=submission.task,
            department=submission.task.department,
        )

    AuditService.record(
        organisation=submission.organisation,
        actor=user,
        event_type='evidence.rejected',
        target_type='EvidenceSubmission',
        target_id=submission.id,
        reason=reason.strip(),
        payload={
            'submission_id': str(submission.id),
            'context_id': str(submission.operating_context_id),
            'document_id': str(submission.document_id),
            'task_id': str(submission.task_id) if submission.task_id else None,
        },
    )
    return submission


def submit_evidence(context, user, data):
    from .models import EvidenceSubmission
    submission = EvidenceSubmission.objects.create(
        organisation=context.organisation,
        operating_context=context,
        submitted_by=user,
        **data,
    )
    AuditService.record(
        organisation=context.organisation,
        actor=user,
        event_type='evidence.submitted',
        target_type='EvidenceSubmission',
        target_id=submission.id,
        payload={
            'submission_id': str(submission.id),
            'context_id': str(context.id),
            'document_id': str(submission.document_id),
            'task_id': str(submission.task_id) if submission.task_id else None,
        },
    )
    return submission


def set_document_lock(document, user, locked, comment=''):
    old_value = document.is_locked
    document.is_locked = locked
    document.save(update_fields=['is_locked', 'updated_at'])
    AuditService.record(
        organisation=document.organisation,
        actor=user,
        event_type='document.locked' if locked else 'document.unlocked',
        target_type='Document',
        target_id=document.id,
        old_value=old_value,
        new_value=locked,
        reason=comment,
    )
    return document
