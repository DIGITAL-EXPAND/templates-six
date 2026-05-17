import pytest

from apps.programming.models import CalendarIssue


@pytest.mark.django_db
class TestManagementReportViews:
    def test_risk_register_counts_open_high_risks_and_scopes_tenant(
        self, client_a, org_a, context_a, user_a, org_b, context_b, user_b,
    ):
        from apps.governance.models import Risk

        Risk.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Major venue risk',
            risk_level='high',
            owner=user_a,
            mitigation_plan='Confirm alternate venue.',
        )
        Risk.objects.create(
            organisation=org_b,
            operating_context=context_b,
            title='Other org risk',
            risk_level='critical',
            owner=user_b,
        )

        r = client_a.get('/api/v1/reports/risk-register/')

        assert r.status_code == 200
        assert r.data['total'] == 1
        assert r.data['open'] == 1
        assert r.data['high_or_critical'] == 1
        assert r.data['results'][0]['title'] == 'Major venue risk'

    def test_contract_status_report_summarises_value_and_signatures(
        self, client_a, org_a, context_a,
    ):
        from decimal import Decimal
        from apps.contracts.models import ContractRecord

        ContractRecord.objects.create(
            organisation=org_a,
            operating_context=context_a,
            contract_type='venue_hire',
            counterparty_name='Client A',
            counterparty_type='client',
            value=Decimal('15000.00'),
            status='issued',
        )
        ContractRecord.objects.create(
            organisation=org_a,
            operating_context=context_a,
            contract_type='artist_performance',
            counterparty_name='Artist A',
            counterparty_type='artist',
            value=Decimal('5000.00'),
            status='signed',
        )

        r = client_a.get('/api/v1/reports/contract-status/')

        assert r.status_code == 200
        assert r.data['total'] == 2
        assert r.data['pending_signature'] == 1
        assert r.data['signed'] == 1
        assert r.data['total_value'] == '20000.00'

    def test_supplier_readiness_report_shows_verification_and_document_gaps(
        self, client_a, org_a, context_a,
    ):
        from apps.suppliers.models import Supplier, SupplierDocument, SupplierEngagement

        supplier = Supplier.objects.create(
            organisation=org_a,
            name='Lighting Co',
            category='Technical',
            csd_verified=False,
        )
        SupplierDocument.objects.create(
            organisation=org_a,
            supplier=supplier,
            document_type='csd_report',
            status='uploaded',
            file_name='csd.pdf',
        )
        SupplierEngagement.objects.create(
            organisation=org_a,
            supplier=supplier,
            operating_context=context_a,
            role='Lighting supplier',
        )

        r = client_a.get('/api/v1/reports/supplier-readiness/')

        assert r.status_code == 200
        assert r.data['total'] == 1
        assert r.data['verified'] == 0
        assert r.data['pending_verification'] == 1
        assert r.data['document_gaps'] == 1
        assert r.data['engagements'] == 1
        assert r.data['results'][0]['workspaces'] == ['Production A']

    def test_evidence_gaps_report_includes_tasks_and_process_steps(
        self, client_a, org_a, context_a, user_a,
    ):
        from apps.tasks.models import Task
        from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate
        from apps.workflows.services import instantiate_workflow

        Task.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Upload signed brief',
            evidence_required=True,
            evidence_provided=False,
            status='open',
        )
        template = WorkflowTemplate.objects.create(
            organisation=org_a,
            name='Evidence Process',
            context_type='production',
        )
        WorkflowStepTemplate.objects.create(
            organisation=org_a,
            template=template,
            step_number=1,
            name='Attach approved evidence',
            requires_evidence=True,
        )
        instantiate_workflow(context_a, template, user_a)

        r = client_a.get('/api/v1/reports/evidence-gaps/')

        assert r.status_code == 200
        assert r.data['total'] == 2
        assert r.data['task_gaps'] == 1
        assert r.data['process_step_gaps'] == 1
        assert {item['type'] for item in r.data['results']} == {'task', 'process_step'}

    def test_calendar_issues_report_counts_open_high_items(
        self, client_a, org_a, context_a, department_a, user_a,
    ):
        CalendarIssue.objects.create(
            organisation=org_a,
            operating_context=context_a,
            department=department_a,
            title='Load-in conflict',
            severity='high',
            raised_by=user_a,
        )
        CalendarIssue.objects.create(
            organisation=org_a,
            operating_context=context_a,
            department=department_a,
            title='Resolved note',
            severity='critical',
            status='resolved',
            raised_by=user_a,
        )

        r = client_a.get('/api/v1/reports/calendar-issues/')

        assert r.status_code == 200
        assert r.data['total'] == 2
        assert r.data['open'] == 1
        assert r.data['critical_or_high'] == 1

    def test_board_summary_exposes_pilot_readiness_signals(
        self, client_a, org_a, context_a, user_a,
    ):
        from apps.governance.models import Risk
        from apps.tasks.models import Task

        Risk.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Board risk',
            risk_level='critical',
            owner=user_a,
        )
        Task.objects.create(
            organisation=org_a,
            operating_context=context_a,
            title='Evidence missing',
            evidence_required=True,
            evidence_provided=False,
        )

        r = client_a.get('/api/v1/reports/board-summary/')

        assert r.status_code == 200
        assert r.data['workspaces'] == 1
        assert r.data['high_risks'] == 1
        assert r.data['evidence_gaps'] == 1
        assert r.data['board_ready'] is False
