import random
import datetime
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService

_REQUIRED_DOCUMENT_TYPES = {'csd_report', 'tax_status', 'bank_confirmation'}


def verify_supplier(supplier, user):
    from .models import SupplierDocument
    uploaded_types = set(
        SupplierDocument.objects.filter(
            supplier=supplier,
            status__in=('uploaded', 'verified'),
        ).values_list('document_type', flat=True)
    )
    missing = _REQUIRED_DOCUMENT_TYPES - uploaded_types
    if missing:
        raise ValidationError(
            {'detail': f'Missing required documents: {", ".join(sorted(missing))}'}
        )
    supplier.csd_verified = True
    supplier.csd_verified_by = user
    supplier.csd_verified_at = datetime.datetime.now(tz=datetime.timezone.utc)
    supplier.status = 'ready'
    supplier.save(update_fields=['csd_verified', 'csd_verified_by', 'csd_verified_at', 'status', 'updated_at'])

    from .models import PaymentPack
    PaymentPack.objects.filter(
        supplier_engagement__supplier=supplier,
        status='awaiting_csd',
    ).update(status='ready_for_erp')

    AuditEvent.objects.create(
        organisation=supplier.organisation,
        actor=user,
        event_type='SUPPLIER_VERIFIED',
        payload={'supplier_id': str(supplier.id), 'supplier_name': supplier.name},
    )
    return supplier


def send_payment_to_erp(payment_pack, user):
    if not payment_pack.supplier_engagement.supplier.csd_verified:
        raise ValidationError(
            {'detail': 'Supplier must be CSD verified before payment can be processed'}
        )
    if payment_pack.status != 'ready_for_erp':
        raise ValidationError({'detail': 'Payment pack must be in ready_for_erp status'})

    erp_ref = f'INV-{datetime.date.today().year}-{random.randint(1000, 9999)}'
    payment_pack.status = 'sent_to_erp'
    payment_pack.erp_reference = erp_ref
    payment_pack.save(update_fields=['status', 'erp_reference', 'updated_at'])
    AuditEvent.objects.create(
        organisation=payment_pack.organisation,
        actor=user,
        event_type='PAYMENT_SENT_TO_ERP',
        payload={
            'payment_pack_id': str(payment_pack.id),
            'new_value': erp_ref,
        },
    )
    return payment_pack


def upload_supplier_document(supplier, user, document_type, file_name):
    from .models import SupplierDocument
    doc, _ = SupplierDocument.objects.get_or_create(
        supplier=supplier,
        document_type=document_type,
        defaults={'organisation': supplier.organisation},
    )
    doc.status = 'uploaded'
    doc.file_name = file_name
    doc.save(update_fields=['status', 'file_name', 'updated_at'])

    uploaded_types = set(
        SupplierDocument.objects.filter(
            supplier=supplier,
            status__in=('uploaded', 'verified'),
        ).values_list('document_type', flat=True)
    )
    if _REQUIRED_DOCUMENT_TYPES.issubset(uploaded_types):
        supplier.status = 'pending_verification'
        supplier.save(update_fields=['status', 'updated_at'])

    AuditEvent.objects.create(
        organisation=supplier.organisation,
        actor=user,
        event_type='SUPPLIER_DOCUMENT_UPLOADED',
        payload={
            'supplier_id': str(supplier.id),
            'document_type': document_type,
            'file_name': file_name,
        },
    )
    return doc


def verify_supplier_document(doc, user, comment=''):
    old_status = doc.status
    doc.status = 'verified'
    doc.verified_by = user
    doc.verified_at = datetime.datetime.now(tz=datetime.timezone.utc)
    doc.save(update_fields=['status', 'verified_by', 'verified_at', 'updated_at'])
    AuditService.record(
        organisation=doc.organisation,
        actor=user,
        event_type='SUPPLIER_DOCUMENT_VERIFIED',
        target_type='SupplierDocument',
        target_id=doc.id,
        old_value=old_status,
        new_value=doc.status,
        reason=comment,
    )
    return doc


def reject_supplier_document(doc, user, comment=''):
    old_status = doc.status
    doc.status = 'rejected'
    doc.verified_by = user
    doc.verified_at = datetime.datetime.now(tz=datetime.timezone.utc)
    doc.save(update_fields=['status', 'verified_by', 'verified_at', 'updated_at'])
    AuditService.record(
        organisation=doc.organisation,
        actor=user,
        event_type='SUPPLIER_DOCUMENT_REJECTED',
        target_type='SupplierDocument',
        target_id=doc.id,
        old_value=old_status,
        new_value=doc.status,
        reason=comment,
    )
    return doc


def suspend_supplier(supplier, user, comment=''):
    old_status = supplier.status
    supplier.status = 'suspended'
    supplier.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=supplier.organisation,
        actor=user,
        event_type='SUPPLIER_SUSPENDED',
        target_type='Supplier',
        target_id=supplier.id,
        old_value=old_status,
        new_value=supplier.status,
        reason=comment,
    )
    return supplier
