import pytest
from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate, WorkflowInstance, WorkflowStepInstance
from apps.approvals.models import ApprovalRoute, ApprovalStep, ApprovalRequest, ApprovalDecision


@pytest.fixture
def template_a(db, org_a):
    return WorkflowTemplate.objects.create(
        organisation=org_a,
        name='Production Workflow',
        context_type='production',
    )


@pytest.fixture
def step_tpl_1(db, org_a, template_a):
    return WorkflowStepTemplate.objects.create(
        organisation=org_a,
        template=template_a,
        step_number=1,
        name='Pre-Production Check',
    )


@pytest.fixture
def step_tpl_2(db, org_a, template_a):
    return WorkflowStepTemplate.objects.create(
        organisation=org_a,
        template=template_a,
        step_number=2,
        name='Technical Approval',
        requires_evidence=True,
    )


@pytest.fixture
def workflow_instance(db, org_a, template_a, context_a, step_tpl_1, step_tpl_2, user_a):
    from apps.workflows.services import instantiate_workflow
    return instantiate_workflow(context=context_a, template=template_a, user=user_a)


@pytest.mark.django_db
class TestWorkflowTemplateCRUD:
    def test_create_template(self, client_a, org_a):
        r = client_a.post('/api/v1/workflows/templates/', {
            'name': 'Festival Workflow',
            'context_type': 'festival',
            'description': 'Standard festival workflow',
            'is_active': True,
        }, format='json')
        assert r.status_code == 201
        assert r.data['name'] == 'Festival Workflow'
        assert r.data['context_type'] == 'festival'

    def test_list_templates(self, client_a, template_a):
        r = client_a.get('/api/v1/workflows/templates/')
        assert r.status_code == 200
        ids = [t['id'] for t in r.data['results']]
        assert str(template_a.id) in ids

    def test_retrieve_template(self, client_a, template_a):
        r = client_a.get(f'/api/v1/workflows/templates/{template_a.id}/')
        assert r.status_code == 200
        assert r.data['name'] == template_a.name

    def test_update_template(self, client_a, template_a):
        r = client_a.patch(f'/api/v1/workflows/templates/{template_a.id}/', {
            'name': 'Updated Workflow',
        }, format='json')
        assert r.status_code == 200
        assert r.data['name'] == 'Updated Workflow'

    def test_delete_template(self, client_a, template_a):
        r = client_a.delete(f'/api/v1/workflows/templates/{template_a.id}/')
        assert r.status_code == 405


@pytest.mark.django_db
class TestWorkflowStepTemplateCRUD:
    def test_create_step_template(self, client_a, template_a):
        r = client_a.post('/api/v1/workflows/step-templates/', {
            'template': str(template_a.id),
            'step_number': 1,
            'name': 'Opening Check',
            'requires_evidence': False,
        }, format='json')
        assert r.status_code == 201
        assert r.data['name'] == 'Opening Check'
        assert r.data['step_number'] == 1

    def test_list_step_templates(self, client_a, step_tpl_1):
        r = client_a.get('/api/v1/workflows/step-templates/')
        assert r.status_code == 200
        ids = [s['id'] for s in r.data['results']]
        assert str(step_tpl_1.id) in ids

    def test_unique_step_number_enforced(self, client_a, template_a, step_tpl_1):
        r = client_a.post('/api/v1/workflows/step-templates/', {
            'template': str(template_a.id),
            'step_number': 1,
            'name': 'Duplicate Step',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestInstantiateWorkflow:
    def test_instantiate_creates_instance(self, client_a, template_a, context_a, step_tpl_1, step_tpl_2):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_a.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 201
        assert r.data['status'] == 'active'

    def test_instantiate_creates_step_instances(self, client_a, template_a, context_a, step_tpl_1, step_tpl_2):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_a.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 201
        instance_id = r.data['id']
        steps = WorkflowStepInstance.objects.filter(workflow_instance_id=instance_id)
        assert steps.count() == 2

    def test_first_step_is_in_progress(self, client_a, template_a, context_a, step_tpl_1, step_tpl_2):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_a.id),
            'operating_context': str(context_a.id),
        }, format='json')
        instance_id = r.data['id']
        first = WorkflowStepInstance.objects.get(
            workflow_instance_id=instance_id, step_number=1,
        )
        assert first.status == 'in_progress'

    def test_remaining_steps_are_pending(self, client_a, template_a, context_a, step_tpl_1, step_tpl_2):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_a.id),
            'operating_context': str(context_a.id),
        }, format='json')
        instance_id = r.data['id']
        pending = WorkflowStepInstance.objects.filter(
            workflow_instance_id=instance_id, step_number__gt=1,
        )
        assert all(s.status == 'pending' for s in pending)

    def test_context_type_mismatch_rejected(self, client_a, context_a):
        # template for 'festival' but context is 'production'
        festival_tpl = WorkflowTemplate.objects.create(
            organisation=context_a.organisation,
            name='Festival WF',
            context_type='festival',
        )
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(festival_tpl.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestAdvanceStep:
    def test_advance_step_completes_current(self, client_a, workflow_instance):
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        r = client_a.post(f'/api/v1/workflows/steps/{step.id}/advance/', {
            'notes': 'Done',
        }, format='json')
        assert r.status_code == 200
        step.refresh_from_db()
        assert step.status == 'completed'
        assert step.completed_by is not None

    def test_advance_step_activates_next(self, client_a, workflow_instance):
        step1 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        client_a.post(f'/api/v1/workflows/steps/{step1.id}/advance/', {
            'notes': 'Done',
        }, format='json')
        step2 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=2,
        )
        assert step2.status == 'in_progress'

    def test_advance_last_step_completes_workflow(self, client_a, workflow_instance, document_a):
        step1 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        client_a.post(f'/api/v1/workflows/steps/{step1.id}/advance/', {
            'notes': 'Step 1 done',
        }, format='json')
        step2 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=2,
        )
        r = client_a.post(f'/api/v1/workflows/steps/{step2.id}/advance/', {
            'notes': 'Step 2 done',
            'evidence_document': str(document_a.id),
        }, format='json')
        assert r.status_code == 200
        workflow_instance.refresh_from_db()
        assert workflow_instance.status == 'completed'
        assert workflow_instance.completed_at is not None

    def test_cannot_advance_pending_step(self, client_a, workflow_instance):
        step2 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=2,
        )
        r = client_a.post(f'/api/v1/workflows/steps/{step2.id}/advance/', {}, format='json')
        assert r.status_code == 400

    def test_evidence_required_without_document_raises_422(self, client_a, workflow_instance):
        # Advance step 1 first to make step 2 in_progress
        step1 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        client_a.post(f'/api/v1/workflows/steps/{step1.id}/advance/', {
            'notes': 'done',
        }, format='json')
        step2 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=2,
        )
        r = client_a.post(f'/api/v1/workflows/steps/{step2.id}/advance/', {
            'notes': 'Missing evidence',
        }, format='json')
        assert r.status_code == 422

    def test_advance_with_evidence_document_works(self, client_a, workflow_instance, document_a):
        step1 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        client_a.post(f'/api/v1/workflows/steps/{step1.id}/advance/', {
            'notes': 'done',
        }, format='json')
        step2 = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=2,
        )
        r = client_a.post(f'/api/v1/workflows/steps/{step2.id}/advance/', {
            'notes': 'With evidence',
            'evidence_document': str(document_a.id),
        }, format='json')
        assert r.status_code == 200
        step2.refresh_from_db()
        assert step2.status == 'completed'
        assert step2.evidence_document == document_a

    def test_approval_required_without_approval_returns_400(self, client_a, workflow_instance):
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        step.step_template.requires_approval = True
        step.step_template.save(update_fields=['requires_approval'])
        r = client_a.post(f'/api/v1/workflows/steps/{step.id}/advance/', {
            'notes': 'Missing approval',
        }, format='json')
        assert r.status_code == 400
        assert 'approval' in str(r.data).lower()

    def test_approval_required_with_pending_approval_returns_400(self, client_a, workflow_instance, org_a, context_a, user_a):
        route = ApprovalRoute.objects.create(organisation=org_a, name='Process Route')
        approval_step = ApprovalStep.objects.create(
            organisation=org_a, route=route, step_number=1, name='Process Approval',
        )
        approval = ApprovalRequest.objects.create(
            organisation=org_a, operating_context=context_a,
            approval_step=approval_step, requested_by=user_a,
        )
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        step.step_template.requires_approval = True
        step.step_template.save(update_fields=['requires_approval'])
        r = client_a.post(f'/api/v1/workflows/steps/{step.id}/advance/', {
            'notes': 'Pending approval',
            'approval_request': str(approval.id),
        }, format='json')
        assert r.status_code == 400

    def test_approval_required_with_approved_approval_completes(self, client_a, workflow_instance, org_a, context_a, user_a):
        route = ApprovalRoute.objects.create(organisation=org_a, name='Process Route')
        approval_step = ApprovalStep.objects.create(
            organisation=org_a, route=route, step_number=1, name='Process Approval',
        )
        approval = ApprovalRequest.objects.create(
            organisation=org_a, operating_context=context_a,
            approval_step=approval_step, requested_by=user_a,
            decision=ApprovalDecision.APPROVED,
            decided_by=user_a,
        )
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        step.step_template.requires_approval = True
        step.step_template.save(update_fields=['requires_approval'])
        r = client_a.post(f'/api/v1/workflows/steps/{step.id}/advance/', {
            'notes': 'Approved',
            'approval_request': str(approval.id),
        }, format='json')
        assert r.status_code == 200
        step.refresh_from_db()
        assert step.approval_request == approval

    def test_approval_required_rejects_other_org_approval(self, client_a, workflow_instance, org_b, context_b, user_b):
        route = ApprovalRoute.objects.create(organisation=org_b, name='Other Route')
        approval_step = ApprovalStep.objects.create(
            organisation=org_b, route=route, step_number=1, name='Other Approval',
        )
        approval = ApprovalRequest.objects.create(
            organisation=org_b, operating_context=context_b,
            approval_step=approval_step, requested_by=user_b,
            decision=ApprovalDecision.APPROVED,
            decided_by=user_b,
        )
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        step.step_template.requires_approval = True
        step.step_template.save(update_fields=['requires_approval'])
        r = client_a.post(f'/api/v1/workflows/steps/{step.id}/advance/', {
            'notes': 'Cross tenant',
            'approval_request': str(approval.id),
        }, format='json')
        assert r.status_code == 400
        assert 'approval_request' in r.data

    def test_advance_response_includes_process_metadata_and_blockers(self, client_a, workflow_instance):
        step = WorkflowStepInstance.objects.get(
            workflow_instance=workflow_instance, step_number=1,
        )
        step.step_template.requires_approval = True
        step.step_template.save(update_fields=['requires_approval'])
        r = client_a.get(f'/api/v1/workflows/steps/{step.id}/')
        assert r.status_code == 200
        assert r.data['requires_approval'] is True
        assert 'blockers' in r.data

    def test_list_step_instances_filterable_by_workflow(self, client_a, workflow_instance):
        r = client_a.get(
            f'/api/v1/workflows/steps/?workflow_instance={workflow_instance.id}'
        )
        assert r.status_code == 200
        assert r.data['count'] == 2

    def test_list_instances_filterable_by_status(self, client_a, workflow_instance):
        r = client_a.get('/api/v1/workflows/instances/?status=active')
        assert r.status_code == 200
        assert r.data['count'] >= 1
