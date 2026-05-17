from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.audit.services import AuditService


def set_campaign_status(campaign, user, status, comment=''):
    old_status = campaign.status
    campaign.status = status
    campaign.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=campaign.organisation,
        actor=user,
        event_type='campaign.status_changed',
        target_type='Campaign',
        target_id=campaign.id,
        old_value=old_status,
        new_value=status,
        reason=comment,
    )
    return campaign


def complete_deliverable(deliverable, user, evidence_document=None, comment=''):
    if evidence_document is None and deliverable.evidence_document_id is None:
        raise ValidationError({
            'evidence_document': 'Evidence is required before a marketing deliverable can be completed.'
        })
    old_status = deliverable.status
    deliverable.status = 'complete'
    deliverable.completed_at = timezone.now()
    if evidence_document is not None:
        deliverable.evidence_document = evidence_document
    deliverable.save(update_fields=['status', 'completed_at', 'evidence_document', 'updated_at'])
    AuditService.record(
        organisation=deliverable.organisation,
        actor=user,
        event_type='campaign.deliverable_completed',
        target_type='CampaignDeliverable',
        target_id=deliverable.id,
        old_value=old_status,
        new_value=deliverable.status,
        reason=comment,
        payload={'has_evidence': deliverable.evidence_document_id is not None},
    )
    return deliverable
