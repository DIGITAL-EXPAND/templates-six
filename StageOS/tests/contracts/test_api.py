import pytest
from apps.audit.models import AuditEvent
from apps.contracts.models import ContractTemplate, ContractRecord, SignatureRecord


# ── Model tests ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContractModels:
    def test_template_creation_with_template_fields(self, org_a):
        fields = [
            {'key': 'counterparty_name', 'label': 'Client Name', 'type': 'text', 'required': True},
            {'key': 'venue_fee', 'label': 'Venue Hire Fee', 'type': 'currency', 'required': True},
        ]
        tpl = ContractTemplate.objects.create(
            organisation=org_a,
            name='My Template',
            contract_type='venue_hire',
            template_fields=fields,
        )
        tpl.refresh_from_db()
        assert tpl.template_fields == fields
        assert len(tpl.template_fields) == 2

    def test_contract_record_creation(self, org_a, context_a):
        record = ContractRecord.objects.create(
            organisation=org_a,
            operating_context=context_a,
            contract_type='sponsorship',
            counterparty_name='Sponsor Co',
            counterparty_type='partner',
            value='50000.00',
            currency='ZAR',
        )
        assert record.status == 'draft'
        assert record.signatures_received == 0
        assert record.signatures_required == 2

    def test_signature_record_creation(self, org_a, contract_a):
        sig = SignatureRecord.objects.create(
            organisation=org_a,
            contract=contract_a,
            signatory_name='Alice',
            signatory_role='CFO',
            signature_type='digital',
            signature_order=2,
        )
        assert sig.is_signed is False
        assert sig.signed_at is None


# ── ContractTemplate CRUD ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContractTemplateCRUD:
    def test_list(self, client_a, contract_template_a):
        r = client_a.get('/api/v1/contracts/templates/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a):
        r = client_a.post('/api/v1/contracts/templates/', {
            'name': 'New Template',
            'contract_type': 'co_production',
        }, format='json')
        assert r.status_code == 201
        assert ContractTemplate.objects.filter(name='New Template', organisation=org_a).exists()

    def test_create_with_template_fields(self, client_a):
        fields = [{'key': 'fee', 'label': 'Fee', 'type': 'currency', 'required': True}]
        r = client_a.post('/api/v1/contracts/templates/', {
            'name': 'Template With Fields',
            'contract_type': 'supplier_service',
            'template_fields': fields,
        }, format='json')
        assert r.status_code == 201
        assert r.data['template_fields'] == fields

    def test_retrieve(self, client_a, contract_template_a):
        r = client_a.get(f'/api/v1/contracts/templates/{contract_template_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == 'Artist Performance Template'

    def test_partial_update(self, client_a, contract_template_a):
        r = client_a.patch(
            f'/api/v1/contracts/templates/{contract_template_a.id}/',
            {'is_active': False}, format='json',
        )
        assert r.status_code == 200
        contract_template_a.refresh_from_db()
        assert contract_template_a.is_active is False

    def test_delete(self, client_a, contract_template_a):
        r = client_a.delete(f'/api/v1/contracts/templates/{contract_template_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, contract_template_b):
        r = client_a.get(f'/api/v1/contracts/templates/{contract_template_b.id}/')
        assert r.status_code == 404

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/contracts/templates/')
        assert r.status_code == 401


# ── ContractRecord CRUD ───────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContractRecordCRUD:
    def test_list(self, client_a, contract_a):
        r = client_a.get('/api/v1/contracts/records/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, context_a):
        r = client_a.post('/api/v1/contracts/records/', {
            'operating_context': str(context_a.id),
            'contract_type': 'venue_hire',
            'counterparty_name': 'Venue Owner',
            'counterparty_type': 'partner',
        }, format='json')
        assert r.status_code == 201
        assert ContractRecord.objects.filter(
            organisation=org_a, counterparty_name='Venue Owner',
        ).exists()

    def test_create_emits_audit(self, client_a, context_a):
        client_a.post('/api/v1/contracts/records/', {
            'operating_context': str(context_a.id),
            'contract_type': 'sponsorship',
            'counterparty_name': 'Sponsor',
            'counterparty_type': 'partner',
        }, format='json')
        assert AuditEvent.objects.filter(event_type='CONTRACT_CREATED').exists()

    def test_create_without_context_returns_400(self, client_a):
        r = client_a.post('/api/v1/contracts/records/', {
            'contract_type': 'other',
            'counterparty_name': 'Nobody',
            'counterparty_type': 'other',
        }, format='json')
        assert r.status_code == 400

    def test_multiple_contracts_per_context(self, client_a, org_a, context_a):
        for name in ['Artist A', 'Supplier B']:
            client_a.post('/api/v1/contracts/records/', {
                'operating_context': str(context_a.id),
                'contract_type': 'artist_performance',
                'counterparty_name': name,
                'counterparty_type': 'artist',
            }, format='json')
        assert ContractRecord.objects.filter(organisation=org_a).count() == 2

    def test_retrieve(self, client_a, contract_a):
        r = client_a.get(f'/api/v1/contracts/records/{contract_a.id}/')
        assert r.status_code == 200
        assert r.data['counterparty_name'] == 'Big Artist'

    def test_partial_update(self, client_a, contract_a):
        r = client_a.patch(
            f'/api/v1/contracts/records/{contract_a.id}/',
            {'notes': 'Updated notes'}, format='json',
        )
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.notes == 'Updated notes'

    def test_delete(self, client_a, contract_a):
        r = client_a.delete(f'/api/v1/contracts/records/{contract_a.id}/')
        assert r.status_code == 405

    def test_cannot_reach_other_org(self, client_a, contract_b):
        r = client_a.get(f'/api/v1/contracts/records/{contract_b.id}/')
        assert r.status_code == 404


# ── ContractRecord filtering and search ──────────────────────────────────────

@pytest.mark.django_db
class TestContractRecordFiltering:
    def test_filter_by_status(self, client_a, org_a, context_a):
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='A', counterparty_type='other',
            status='draft',
        )
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='B', counterparty_type='other',
            status='issued',
        )
        r = client_a.get('/api/v1/contracts/records/?status=issued')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['counterparty_name'] == 'B'

    def test_filter_by_contract_type(self, client_a, org_a, context_a):
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='sponsorship', counterparty_name='Sponsor', counterparty_type='partner',
        )
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='venue_hire', counterparty_name='Venue', counterparty_type='partner',
        )
        r = client_a.get('/api/v1/contracts/records/?contract_type=sponsorship')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_filter_by_operating_context(self, client_a, org_a, context_a, site_a, user_a):
        from apps.contexts.models import OperatingContext
        ctx2 = OperatingContext.objects.create(
            organisation=org_a, title='Ctx2', site=site_a, owner=user_a,
        )
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='CTX1', counterparty_type='other',
        )
        ContractRecord.objects.create(
            organisation=org_a, operating_context=ctx2,
            contract_type='other', counterparty_name='CTX2', counterparty_type='other',
        )
        r = client_a.get(f'/api/v1/contracts/records/?operating_context={context_a.id}')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['counterparty_name'] == 'CTX1'

    def test_search_by_counterparty_name(self, client_a, org_a, context_a):
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Unique Sponsor Corp', counterparty_type='partner',
        )
        ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Other Party', counterparty_type='other',
        )
        r = client_a.get('/api/v1/contracts/records/?search=Unique+Sponsor')
        assert r.status_code == 200
        assert r.data['count'] == 1
        assert r.data['results'][0]['counterparty_name'] == 'Unique Sponsor Corp'


# ── SignatureRecord CRUD ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSignatureRecordCRUD:
    def test_list(self, client_a, signature_a):
        r = client_a.get('/api/v1/contracts/signatures/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, contract_a):
        r = client_a.post('/api/v1/contracts/signatures/', {
            'contract': str(contract_a.id),
            'signatory_name': 'Bob Builder',
            'signatory_role': 'CFO',
            'signature_type': 'electronic',
            'signature_order': 2,
        }, format='json')
        assert r.status_code == 201
        assert SignatureRecord.objects.filter(
            organisation=org_a, signatory_name='Bob Builder',
        ).exists()

    def test_create_without_contract_returns_400(self, client_a):
        r = client_a.post('/api/v1/contracts/signatures/', {
            'signatory_name': 'Orphan Sig',
            'signatory_role': 'CEO',
            'signature_type': 'wet',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_contract_returns_400(self, client_a, contract_b):
        r = client_a.post('/api/v1/contracts/signatures/', {
            'contract': str(contract_b.id),
            'signatory_name': 'Cross-org',
            'signatory_role': 'CEO',
            'signature_type': 'wet',
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, signature_a):
        r = client_a.get(f'/api/v1/contracts/signatures/{signature_a.id}/')
        assert r.status_code == 200
        assert r.data['signatory_name'] == 'John Doe'

    def test_cannot_reach_other_org(self, client_a, signature_b):
        r = client_a.get(f'/api/v1/contracts/signatures/{signature_b.id}/')
        assert r.status_code == 404


# ── issue_contract action ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestIssueContractAction:
    def test_issue_from_draft(self, client_a, contract_a):
        r = client_a.post(f'/api/v1/contracts/records/{contract_a.id}/issue/', {}, format='json')
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.status == 'issued'

    def test_issue_sets_issued_date(self, client_a, contract_a):
        r = client_a.post(f'/api/v1/contracts/records/{contract_a.id}/issue/', {}, format='json')
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.issued_date is not None

    def test_issue_emits_audit(self, client_a, contract_a):
        client_a.post(f'/api/v1/contracts/records/{contract_a.id}/issue/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='CONTRACT_ISSUED').exists()

    def test_issue_from_legal_review(self, client_a, org_a, context_a):
        c = ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Party', counterparty_type='other',
            status='legal_review',
        )
        r = client_a.post(f'/api/v1/contracts/records/{c.id}/issue/', {}, format='json')
        assert r.status_code == 200
        c.refresh_from_db()
        assert c.status == 'issued'

    def test_issue_from_finance_review(self, client_a, org_a, context_a):
        c = ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Party', counterparty_type='other',
            status='finance_review',
        )
        r = client_a.post(f'/api/v1/contracts/records/{c.id}/issue/', {}, format='json')
        assert r.status_code == 200

    def test_issue_from_signed_returns_400(self, client_a, org_a, context_a):
        c = ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Party', counterparty_type='other',
            status='signed',
        )
        r = client_a.post(f'/api/v1/contracts/records/{c.id}/issue/', {}, format='json')
        assert r.status_code == 400

    def test_issue_from_cancelled_returns_400(self, client_a, org_a, context_a):
        c = ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='Party', counterparty_type='other',
            status='cancelled',
        )
        r = client_a.post(f'/api/v1/contracts/records/{c.id}/issue/', {}, format='json')
        assert r.status_code == 400

    def test_issue_other_org_returns_404(self, client_a, contract_b):
        r = client_a.post(f'/api/v1/contracts/records/{contract_b.id}/issue/', {}, format='json')
        assert r.status_code == 404

    def test_issue_response_contains_updated_contract(self, client_a, contract_a):
        r = client_a.post(f'/api/v1/contracts/records/{contract_a.id}/issue/', {}, format='json')
        assert r.data['status'] == 'issued'
        assert r.data['issued_date'] is not None


# ── submit_for_review action ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestSubmitForReviewAction:
    def test_submit_draft_to_legal_review(self, client_a, contract_a):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'legal_review'}, format='json',
        )
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.status == 'legal_review'

    def test_submit_to_finance_review(self, client_a, contract_a):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'finance_review'}, format='json',
        )
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.status == 'finance_review'

    def test_submit_to_scm_review(self, client_a, contract_a):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'scm_review'}, format='json',
        )
        assert r.status_code == 200
        contract_a.refresh_from_db()
        assert contract_a.status == 'scm_review'

    def test_submit_emits_audit(self, client_a, contract_a):
        client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'legal_review'}, format='json',
        )
        assert AuditEvent.objects.filter(event_type='CONTRACT_SUBMITTED_FOR_REVIEW').exists()

    def test_invalid_review_type_returns_400(self, client_a, contract_a):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'board_review'}, format='json',
        )
        assert r.status_code == 400

    def test_submit_from_issued_returns_400(self, client_a, org_a, context_a):
        c = ContractRecord.objects.create(
            organisation=org_a, operating_context=context_a,
            contract_type='other', counterparty_name='P', counterparty_type='other',
            status='issued',
        )
        r = client_a.post(
            f'/api/v1/contracts/records/{c.id}/submit-for-review/',
            {'review_type': 'legal_review'}, format='json',
        )
        assert r.status_code == 400

    def test_submit_response_contains_updated_status(self, client_a, contract_a):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_a.id}/submit-for-review/',
            {'review_type': 'finance_review'}, format='json',
        )
        assert r.data['status'] == 'finance_review'

    def test_submit_other_org_returns_404(self, client_a, contract_b):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_b.id}/submit-for-review/',
            {'review_type': 'legal_review'}, format='json',
        )
        assert r.status_code == 404


# ── sign action ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSignAction:
    def _make_issued_contract(self, org, context, signatures_required=2):
        c = ContractRecord.objects.create(
            organisation=org, operating_context=context,
            contract_type='other', counterparty_name='Party', counterparty_type='other',
            status='issued', signatures_required=signatures_required,
        )
        return c

    def test_first_signature_sets_counter_signed(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a, signatures_required=2)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer A', signatory_role='CEO', signature_type='wet',
        )
        r = client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert r.status_code == 200
        contract.refresh_from_db()
        assert contract.status == 'counter_signed'
        assert contract.signatures_received == 1

    def test_final_signature_sets_signed(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a, signatures_required=1)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer A', signatory_role='CEO', signature_type='wet',
        )
        r = client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert r.status_code == 200
        contract.refresh_from_db()
        assert contract.status == 'signed'
        assert contract.signatures_received == 1

    def test_sign_sets_is_signed_and_signed_at(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer', signatory_role='CFO', signature_type='digital',
        )
        r = client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert r.status_code == 200
        sig.refresh_from_db()
        assert sig.is_signed is True
        assert sig.signed_at is not None

    def test_sign_already_signed_returns_400(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer', signatory_role='CFO', signature_type='wet',
        )
        client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        r = client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert r.status_code == 400

    def test_sign_unissued_contract_returns_400(self, client_a, signature_a):
        # contract_a is in 'draft' status
        r = client_a.post(f'/api/v1/contracts/signatures/{signature_a.id}/sign/', {}, format='json')
        assert r.status_code == 400

    def test_sign_emits_counter_signed_audit(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a, signatures_required=2)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer', signatory_role='CFO', signature_type='wet',
        )
        client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='CONTRACT_SIGNATURE_RECORDED').exists()

    def test_sign_emits_fully_signed_audit(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a, signatures_required=1)
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer', signatory_role='CFO', signature_type='wet',
        )
        client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert AuditEvent.objects.filter(event_type='CONTRACT_FULLY_SIGNED').exists()

    def test_sign_other_org_returns_404(self, client_a, signature_b):
        r = client_a.post(f'/api/v1/contracts/signatures/{signature_b.id}/sign/', {}, format='json')
        assert r.status_code == 404

    def test_sign_counter_signed_contract_advances_to_signed(self, client_a, org_a, context_a):
        contract = self._make_issued_contract(org_a, context_a, signatures_required=2)
        contract.status = 'counter_signed'
        contract.signatures_received = 1
        contract.save()
        sig = SignatureRecord.objects.create(
            organisation=org_a, contract=contract,
            signatory_name='Signer 2', signatory_role='Board', signature_type='wet',
        )
        r = client_a.post(f'/api/v1/contracts/signatures/{sig.id}/sign/', {}, format='json')
        assert r.status_code == 200
        contract.refresh_from_db()
        assert contract.status == 'signed'


# ── Cross-org validation ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestContractCrossOrgValidation:
    def test_create_record_with_other_org_context_rejected(self, client_a, context_b):
        r = client_a.post('/api/v1/contracts/records/', {
            'operating_context': str(context_b.id),
            'contract_type': 'other',
            'counterparty_name': 'Cross Org',
            'counterparty_type': 'other',
        }, format='json')
        assert r.status_code == 400

    def test_create_record_with_other_org_template_rejected(self, client_a, context_a, contract_template_b):
        r = client_a.post('/api/v1/contracts/records/', {
            'operating_context': str(context_a.id),
            'template': str(contract_template_b.id),
            'contract_type': 'other',
            'counterparty_name': 'Party',
            'counterparty_type': 'other',
        }, format='json')
        assert r.status_code == 400

    def test_create_signature_with_other_org_contract_rejected(self, client_a, contract_b):
        r = client_a.post('/api/v1/contracts/signatures/', {
            'contract': str(contract_b.id),
            'signatory_name': 'Cross Org Signer',
            'signatory_role': 'CEO',
            'signature_type': 'wet',
        }, format='json')
        assert r.status_code == 400
