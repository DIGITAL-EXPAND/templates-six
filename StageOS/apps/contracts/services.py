import datetime
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService

_ISSUABLE_STATUSES = {'draft', 'legal_review', 'finance_review', 'scm_review'}
_REVIEW_TYPES = {'legal_review', 'finance_review', 'scm_review'}


def create_contract(context, user, data):
    from .models import ContractRecord
    contract = ContractRecord.objects.create(
        organisation=context.organisation,
        operating_context=context,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='CONTRACT_CREATED',
        payload={
            'contract_id': str(contract.id),
            'context_id': str(context.id),
            'counterparty_name': contract.counterparty_name,
            'contract_type': contract.contract_type,
        },
    )
    return contract


def issue_contract(contract, user):
    if contract.status not in _ISSUABLE_STATUSES:
        raise ValidationError(
            {'detail': 'Contract can only be issued from draft or review status'}
        )
    old_status = contract.status
    contract.status = 'issued'
    contract.issued_date = datetime.date.today()
    contract.save(update_fields=['status', 'issued_date', 'updated_at'])
    AuditEvent.objects.create(
        organisation=contract.organisation,
        actor=user,
        event_type='CONTRACT_ISSUED',
        payload={
            'contract_id': str(contract.id),
            'old_value': old_status,
            'new_value': 'issued',
        },
    )
    return contract


def record_signature(signature_record, user):
    if signature_record.is_signed:
        raise ValidationError({'detail': 'This signature has already been recorded'})
    if signature_record.contract.status not in ('issued', 'counter_signed'):
        raise ValidationError(
            {'detail': 'Contract must be issued before signatures can be recorded'}
        )
    signature_record.is_signed = True
    signature_record.signed_at = datetime.datetime.now(tz=datetime.timezone.utc)
    signature_record.save(update_fields=['is_signed', 'signed_at', 'updated_at'])

    contract = signature_record.contract
    contract.signatures_received += 1

    if contract.signatures_received >= contract.signatures_required:
        contract.status = 'signed'
        contract.save(update_fields=['signatures_received', 'status', 'updated_at'])
        AuditEvent.objects.create(
            organisation=contract.organisation,
            actor=user,
            event_type='CONTRACT_FULLY_SIGNED',
            payload={
                'contract_id': str(contract.id),
                'signatures_received': contract.signatures_received,
            },
        )
    else:
        contract.status = 'counter_signed'
        contract.save(update_fields=['signatures_received', 'status', 'updated_at'])
        AuditEvent.objects.create(
            organisation=contract.organisation,
            actor=user,
            event_type='CONTRACT_SIGNATURE_RECORDED',
            payload={
                'contract_id': str(contract.id),
                'signatures_received': contract.signatures_received,
                'signatures_required': contract.signatures_required,
            },
        )
    return signature_record


def submit_for_review(contract, user, review_type):
    if review_type not in _REVIEW_TYPES:
        raise ValidationError(
            {'detail': f'review_type must be one of: {", ".join(sorted(_REVIEW_TYPES))}'}
        )
    valid_from = _ISSUABLE_STATUSES  # draft + all review types
    if contract.status not in valid_from:
        raise ValidationError(
            {'detail': 'Contract cannot be submitted for review from its current status'}
        )
    contract.status = review_type
    contract.save(update_fields=['status', 'updated_at'])
    AuditEvent.objects.create(
        organisation=contract.organisation,
        actor=user,
        event_type='CONTRACT_SUBMITTED_FOR_REVIEW',
        payload={
            'contract_id': str(contract.id),
            'new_value': review_type,
        },
    )
    return contract


def cancel_contract(contract, user, comment=''):
    old_status = contract.status
    contract.status = 'cancelled'
    contract.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=contract.organisation,
        actor=user,
        event_type='CONTRACT_CANCELLED',
        target_type='ContractRecord',
        target_id=contract.id,
        old_value=old_status,
        new_value=contract.status,
        reason=comment,
    )
    return contract


def lock_final_contract(contract, user, comment=''):
    if contract.status != 'signed':
        raise ValidationError({'detail': 'Contract must be fully signed before it can be locked.'})
    if not contract.signed_document_id:
        raise ValidationError({'detail': 'Signed document is required before locking.'})
    old_status = contract.status
    AuditService.record(
        organisation=contract.organisation,
        actor=user,
        event_type='CONTRACT_LOCKED',
        target_type='ContractRecord',
        target_id=contract.id,
        old_value=old_status,
        new_value=contract.status,
        reason=comment,
        payload={'signed_document_id': str(contract.signed_document_id)},
    )
    return contract
