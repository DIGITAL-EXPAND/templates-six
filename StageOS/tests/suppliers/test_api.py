import pytest
from apps.audit.models import AuditEvent
from apps.suppliers.models import Supplier, SupplierDocument, SupplierEngagement, PaymentPack


# ── Supplier CRUD ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSupplierCRUD:
    def test_list(self, client_a, supplier_a):
        r = client_a.get('/api/v1/suppliers/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a):
        r = client_a.post('/api/v1/suppliers/', {
            'name': 'New Supplier',
            'category': 'Security',
        }, format='json')
        assert r.status_code == 201
        assert Supplier.objects.filter(organisation=org_a, name='New Supplier').exists()

    def test_retrieve(self, client_a, supplier_a):
        r = client_a.get(f'/api/v1/suppliers/{supplier_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == 'Lights & Sound Co'

    def test_partial_update(self, client_a, supplier_a):
        r = client_a.patch(f'/api/v1/suppliers/{supplier_a.id}/', {'panel': 'Tech Panel'}, format='json')
        assert r.status_code == 200
        supplier_a.refresh_from_db()
        assert supplier_a.panel == 'Tech Panel'

    def test_delete(self, client_a, supplier_a):
        r = client_a.delete(f'/api/v1/suppliers/{supplier_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, supplier_b):
        r = client_a.get(f'/api/v1/suppliers/{supplier_b.id}/')
        assert r.status_code == 404

    def test_filter_by_status(self, client_a, org_a):
        Supplier.objects.create(organisation=org_a, name='Ready One', category='X', status='ready')
        Supplier.objects.create(organisation=org_a, name='Pending One', category='X', status='pending_verification')
        r = client_a.get('/api/v1/suppliers/?status=ready')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['name'] == 'Ready One'

    def test_search_by_name(self, client_a, org_a):
        Supplier.objects.create(organisation=org_a, name='UniqueNameSupplier', category='X')
        Supplier.objects.create(organisation=org_a, name='Other Vendor', category='X')
        r = client_a.get('/api/v1/suppliers/?search=UniqueNameSupplier')
        assert r.data['count'] == 1

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/suppliers/')
        assert r.status_code == 401


# ── SupplierDocument CRUD ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSupplierDocumentCRUD:
    def test_create(self, client_a, org_a, supplier_a):
        r = client_a.post('/api/v1/suppliers/documents/', {
            'supplier': str(supplier_a.id),
            'document_type': 'csd_report',
            'file_name': 'csd_report.pdf',
        }, format='json')
        assert r.status_code == 201
        assert SupplierDocument.objects.filter(
            organisation=org_a, supplier=supplier_a, document_type='csd_report',
        ).exists()

    def test_list_filterable_by_supplier(self, client_a, org_a, supplier_a):
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a, document_type='csd_report',
        )
        r = client_a.get(f'/api/v1/suppliers/documents/?supplier={supplier_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_document_type(self, client_a, org_a, supplier_a):
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a, document_type='csd_report',
        )
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a, document_type='tax_status',
        )
        r = client_a.get('/api/v1/suppliers/documents/?document_type=csd_report')
        assert r.data['count'] == 1

    def test_cross_org_supplier_returns_400(self, client_a, supplier_b):
        r = client_a.post('/api/v1/suppliers/documents/', {
            'supplier': str(supplier_b.id),
            'document_type': 'csd_report',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org_doc(self, client_a, org_b, supplier_b):
        doc = SupplierDocument.objects.create(
            organisation=org_b, supplier=supplier_b, document_type='csd_report',
        )
        r = client_a.get(f'/api/v1/suppliers/documents/{doc.id}/')
        assert r.status_code == 404


# ── SupplierEngagement CRUD ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestSupplierEngagementCRUD:
    def test_create(self, client_a, org_a, supplier_a, context_a):
        r = client_a.post('/api/v1/suppliers/engagements/', {
            'supplier': str(supplier_a.id),
            'operating_context': str(context_a.id),
            'role': 'Sound Engineer',
        }, format='json')
        assert r.status_code == 201
        assert SupplierEngagement.objects.filter(
            organisation=org_a, supplier=supplier_a,
        ).exists()

    def test_list(self, client_a, supplier_engagement_a):
        r = client_a.get('/api/v1/suppliers/engagements/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_duplicate_supplier_context_returns_400(self, client_a, supplier_engagement_a, supplier_a, context_a):
        r = client_a.post('/api/v1/suppliers/engagements/', {
            'supplier': str(supplier_a.id),
            'operating_context': str(context_a.id),
            'role': 'Duplicate Role',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_supplier_returns_400(self, client_a, supplier_b, context_a):
        r = client_a.post('/api/v1/suppliers/engagements/', {
            'supplier': str(supplier_b.id),
            'operating_context': str(context_a.id),
            'role': 'Cross-org supplier',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_context_returns_400(self, client_a, supplier_a, context_b):
        r = client_a.post('/api/v1/suppliers/engagements/', {
            'supplier': str(supplier_a.id),
            'operating_context': str(context_b.id),
            'role': 'Cross-org context',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, supplier_engagement_b):
        r = client_a.get(f'/api/v1/suppliers/engagements/{supplier_engagement_b.id}/')
        assert r.status_code == 404


# ── PaymentPack CRUD ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPaymentPackCRUD:
    def test_create(self, client_a, org_a, supplier_engagement_a, context_a):
        r = client_a.post('/api/v1/suppliers/payment-packs/', {
            'supplier_engagement': str(supplier_engagement_a.id),
            'operating_context': str(context_a.id),
            'amount': '5000.00',
        }, format='json')
        assert r.status_code == 201
        assert PaymentPack.objects.filter(organisation=org_a).exists()

    def test_cross_org_engagement_returns_400(self, client_a, supplier_engagement_b, context_a):
        r = client_a.post('/api/v1/suppliers/payment-packs/', {
            'supplier_engagement': str(supplier_engagement_b.id),
            'operating_context': str(context_a.id),
            'amount': '1000.00',
        }, format='json')
        assert r.status_code == 400

    def test_filter_by_status(self, client_a, org_a, supplier_engagement_a, context_a):
        PaymentPack.objects.create(
            organisation=org_a, supplier_engagement=supplier_engagement_a,
            operating_context=context_a, amount='2000', status='ready_for_erp',
        )
        PaymentPack.objects.create(
            organisation=org_a, supplier_engagement=supplier_engagement_a,
            operating_context=context_a, amount='1000', status='awaiting_csd',
        )
        r = client_a.get('/api/v1/suppliers/payment-packs/?status=ready_for_erp')
        assert r.data['count'] == 1

    def test_cannot_reach_other_org(self, client_a, org_b, supplier_engagement_b, context_b):
        pack = PaymentPack.objects.create(
            organisation=org_b, supplier_engagement=supplier_engagement_b,
            operating_context=context_b, amount='500',
        )
        r = client_a.get(f'/api/v1/suppliers/payment-packs/{pack.id}/')
        assert r.status_code == 404


# ── verify_supplier action ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestVerifySupplierAction:
    def _upload_required_docs(self, org, supplier):
        for doc_type in ('csd_report', 'tax_status', 'bank_confirmation'):
            SupplierDocument.objects.create(
                organisation=org, supplier=supplier,
                document_type=doc_type, status='uploaded',
                file_name=f'{doc_type}.pdf',
            )

    def test_verify_succeeds_when_all_docs_uploaded(self, client_a, org_a, supplier_a):
        self._upload_required_docs(org_a, supplier_a)
        r = client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        assert r.status_code == 200
        supplier_a.refresh_from_db()
        assert supplier_a.csd_verified is True
        assert supplier_a.status == 'ready'

    def test_verify_sets_verified_by_and_at(self, client_a, org_a, supplier_a, user_a):
        self._upload_required_docs(org_a, supplier_a)
        client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        supplier_a.refresh_from_db()
        assert supplier_a.csd_verified_by == user_a
        assert supplier_a.csd_verified_at is not None

    def test_verify_emits_audit(self, client_a, org_a, supplier_a):
        self._upload_required_docs(org_a, supplier_a)
        client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='SUPPLIER_VERIFIED').exists()

    def test_verify_with_verified_status_docs_succeeds(self, client_a, org_a, supplier_a):
        for doc_type in ('csd_report', 'tax_status', 'bank_confirmation'):
            SupplierDocument.objects.create(
                organisation=org_a, supplier=supplier_a,
                document_type=doc_type, status='verified',
            )
        r = client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        assert r.status_code == 200

    def test_verify_fails_when_docs_missing(self, client_a, org_a, supplier_a):
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a,
            document_type='csd_report', status='uploaded',
        )
        r = client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        assert r.status_code == 400

    def test_verify_error_lists_missing_docs(self, client_a, org_a, supplier_a):
        r = client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        assert r.status_code == 400
        detail = str(r.data)
        assert 'csd_report' in detail or 'bank_confirmation' in detail

    def test_verify_other_org_returns_404(self, client_a, supplier_b):
        r = client_a.post(f'/api/v1/suppliers/{supplier_b.id}/verify/', {}, format='json')
        assert r.status_code == 404


# ── send_payment_to_erp action ────────────────────────────────────────────────

@pytest.mark.django_db
class TestSendPaymentToERPAction:
    def _make_verified_supplier(self, org, user):
        supplier = Supplier.objects.create(
            organisation=org, name='Verified Supplier',
            category='Tech', status='ready', csd_verified=True,
            csd_verified_by=user,
        )
        return supplier

    def _make_ready_pack(self, org, supplier, context):
        engagement = SupplierEngagement.objects.create(
            organisation=org, supplier=supplier,
            operating_context=context, role='Service',
        )
        return PaymentPack.objects.create(
            organisation=org, supplier_engagement=engagement,
            operating_context=context, amount='10000', status='ready_for_erp',
        )

    def test_send_succeeds_when_verified_and_ready(self, client_a, org_a, context_a, user_a):
        supplier = self._make_verified_supplier(org_a, user_a)
        pack = self._make_ready_pack(org_a, supplier, context_a)
        r = client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        assert r.status_code == 200
        pack.refresh_from_db()
        assert pack.status == 'sent_to_erp'

    def test_send_generates_erp_reference(self, client_a, org_a, context_a, user_a):
        supplier = self._make_verified_supplier(org_a, user_a)
        pack = self._make_ready_pack(org_a, supplier, context_a)
        client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        pack.refresh_from_db()
        assert pack.erp_reference.startswith('INV-')

    def test_send_emits_audit(self, client_a, org_a, context_a, user_a):
        supplier = self._make_verified_supplier(org_a, user_a)
        pack = self._make_ready_pack(org_a, supplier, context_a)
        client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='PAYMENT_SENT_TO_ERP').exists()

    def test_send_fails_when_supplier_not_verified(self, client_a, org_a, context_a, user_a):
        supplier = Supplier.objects.create(
            organisation=org_a, name='Unverified', category='X', csd_verified=False,
        )
        engagement = SupplierEngagement.objects.create(
            organisation=org_a, supplier=supplier,
            operating_context=context_a, role='Service',
        )
        pack = PaymentPack.objects.create(
            organisation=org_a, supplier_engagement=engagement,
            operating_context=context_a, amount='1000', status='ready_for_erp',
        )
        r = client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        assert r.status_code == 400

    def test_send_fails_when_status_not_ready_for_erp(self, client_a, org_a, context_a, user_a):
        supplier = self._make_verified_supplier(org_a, user_a)
        engagement = SupplierEngagement.objects.create(
            organisation=org_a, supplier=supplier,
            operating_context=context_a, role='Service',
        )
        pack = PaymentPack.objects.create(
            organisation=org_a, supplier_engagement=engagement,
            operating_context=context_a, amount='500', status='awaiting_csd',
        )
        r = client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        assert r.status_code == 400

    def test_send_other_org_returns_404(self, client_a, org_b, supplier_engagement_b, context_b):
        pack = PaymentPack.objects.create(
            organisation=org_b, supplier_engagement=supplier_engagement_b,
            operating_context=context_b, amount='500', status='ready_for_erp',
        )
        r = client_a.post(f'/api/v1/suppliers/payment-packs/{pack.id}/send-to-erp/', {}, format='json')
        assert r.status_code == 404


# ── upload_supplier_document service ─────────────────────────────────────────

@pytest.mark.django_db
class TestUploadSupplierDocument:
    def test_uploading_last_required_doc_sets_pending_verification(self, client_a, org_a, supplier_a):
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a,
            document_type='csd_report', status='uploaded',
        )
        SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a,
            document_type='tax_status', status='uploaded',
        )
        r = client_a.post('/api/v1/suppliers/documents/', {
            'supplier': str(supplier_a.id),
            'document_type': 'bank_confirmation',
            'file_name': 'bank.pdf',
        }, format='json')
        assert r.status_code == 201
        supplier_a.refresh_from_db()
        assert supplier_a.status == 'documents_incomplete'

    def test_upload_document_service_sets_pending_verification(self, client_a, org_a, supplier_a, user_a):
        from apps.suppliers.services import upload_supplier_document
        upload_supplier_document(supplier_a, user_a, 'csd_report', 'csd.pdf')
        upload_supplier_document(supplier_a, user_a, 'tax_status', 'tax.pdf')
        upload_supplier_document(supplier_a, user_a, 'bank_confirmation', 'bank.pdf')
        supplier_a.refresh_from_db()
        assert supplier_a.status == 'pending_verification'

    def test_upload_document_service_emits_audit(self, client_a, org_a, supplier_a, user_a):
        from apps.suppliers.services import upload_supplier_document
        upload_supplier_document(supplier_a, user_a, 'csd_report', 'csd.pdf')
        assert AuditEvent.objects.filter(event_type='SUPPLIER_DOCUMENT_UPLOADED').exists()

    def test_upload_creates_or_updates_existing(self, org_a, supplier_a, user_a):
        from apps.suppliers.services import upload_supplier_document
        upload_supplier_document(supplier_a, user_a, 'csd_report', 'v1.pdf')
        upload_supplier_document(supplier_a, user_a, 'csd_report', 'v2.pdf')
        assert SupplierDocument.objects.filter(
            supplier=supplier_a, document_type='csd_report',
        ).count() == 1
        doc = SupplierDocument.objects.get(supplier=supplier_a, document_type='csd_report')
        assert doc.file_name == 'v2.pdf'


# ── CSD verification auto-advances payment packs ─────────────────────────────

@pytest.mark.django_db
class TestCSDVerificationAdvancesPaymentPacks:
    """Regression: verifying a supplier must flip awaiting_csd packs to ready_for_erp."""

    def _upload_required_docs(self, org, supplier):
        for doc_type in ('csd_report', 'tax_status', 'bank_confirmation'):
            SupplierDocument.objects.create(
                organisation=org, supplier=supplier,
                document_type=doc_type, status='uploaded',
                file_name=f'{doc_type}.pdf',
            )

    def test_awaiting_csd_packs_become_ready_for_erp_on_verify(
        self, client_a, org_a, supplier_a, supplier_engagement_a, context_a,
    ):
        self._upload_required_docs(org_a, supplier_a)
        pack = PaymentPack.objects.create(
            organisation=org_a,
            supplier_engagement=supplier_engagement_a,
            operating_context=context_a,
            amount='5000.00',
            status='awaiting_csd',
        )
        client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        pack.refresh_from_db()
        assert pack.status == 'ready_for_erp'

    def test_only_awaiting_csd_packs_are_advanced(
        self, client_a, org_a, supplier_a, supplier_engagement_a, context_a,
    ):
        self._upload_required_docs(org_a, supplier_a)
        pack_awaiting = PaymentPack.objects.create(
            organisation=org_a,
            supplier_engagement=supplier_engagement_a,
            operating_context=context_a,
            amount='1000.00',
            status='awaiting_csd',
        )
        pack_sent = PaymentPack.objects.create(
            organisation=org_a,
            supplier_engagement=supplier_engagement_a,
            operating_context=context_a,
            amount='2000.00',
            status='sent_to_erp',
        )
        client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        pack_awaiting.refresh_from_db()
        pack_sent.refresh_from_db()
        assert pack_awaiting.status == 'ready_for_erp'
        assert pack_sent.status == 'sent_to_erp'

    def test_packs_of_other_supplier_not_advanced(
        self, client_a, org_a, supplier_a, context_a, user_a,
    ):
        self._upload_required_docs(org_a, supplier_a)
        other_supplier = Supplier.objects.create(
            organisation=org_a, name='Other Supplier', category='X',
        )
        other_engagement = SupplierEngagement.objects.create(
            organisation=org_a, supplier=other_supplier,
            operating_context=context_a, role='Other Role',
        )
        unrelated_pack = PaymentPack.objects.create(
            organisation=org_a,
            supplier_engagement=other_engagement,
            operating_context=context_a,
            amount='999.00',
            status='awaiting_csd',
        )
        client_a.post(f'/api/v1/suppliers/{supplier_a.id}/verify/', {}, format='json')
        unrelated_pack.refresh_from_db()
        assert unrelated_pack.status == 'awaiting_csd'
