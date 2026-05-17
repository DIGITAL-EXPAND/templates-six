import pytest
from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate, WorkflowInstance, WorkflowStepInstance
from apps.approvals.models import ApprovalRoute, ApprovalStep, ApprovalRequest, ApprovalDecision


# ── Workflow Template isolation ───────────────────────────────────────────────

@pytest.fixture
def template_a(db, org_a):
    return WorkflowTemplate.objects.create(
        organisation=org_a, name='Org A Workflow', context_type='production',
    )


@pytest.fixture
def template_b(db, org_b):
    return WorkflowTemplate.objects.create(
        organisation=org_b, name='Org B Workflow', context_type='production',
    )


@pytest.fixture
def step_tpl_a(db, org_a, template_a):
    return WorkflowStepTemplate.objects.create(
        organisation=org_a, template=template_a, step_number=1, name='Step A',
    )


@pytest.fixture
def step_tpl_b(db, org_b, template_b):
    return WorkflowStepTemplate.objects.create(
        organisation=org_b, template=template_b, step_number=1, name='Step B',
    )


@pytest.fixture
def workflow_instance_a(db, org_a, template_a, context_a, step_tpl_a, user_a):
    from apps.workflows.services import instantiate_workflow
    return instantiate_workflow(context=context_a, template=template_a, user=user_a)


@pytest.fixture
def workflow_instance_b(db, org_b, template_b, context_b, step_tpl_b, user_b):
    from apps.workflows.services import instantiate_workflow
    return instantiate_workflow(context=context_b, template=template_b, user=user_b)


# ── Approval fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def route_a(db, org_a):
    return ApprovalRoute.objects.create(organisation=org_a, name='Route A')


@pytest.fixture
def route_b(db, org_b):
    return ApprovalRoute.objects.create(organisation=org_b, name='Route B')


@pytest.fixture
def approval_step_a(db, org_a, route_a):
    return ApprovalStep.objects.create(
        organisation=org_a, route=route_a, step_number=1, name='Step A',
    )


@pytest.fixture
def approval_step_b(db, org_b, route_b):
    return ApprovalStep.objects.create(
        organisation=org_b, route=route_b, step_number=1, name='Step B',
    )


@pytest.fixture
def approval_request_a(db, org_a, context_a, approval_step_a, user_a):
    return ApprovalRequest.objects.create(
        organisation=org_a, operating_context=context_a,
        approval_step=approval_step_a, requested_by=user_a,
    )


@pytest.fixture
def approval_request_b(db, org_b, context_b, approval_step_b, user_b):
    return ApprovalRequest.objects.create(
        organisation=org_b, operating_context=context_b,
        approval_step=approval_step_b, requested_by=user_b,
    )


@pytest.mark.django_db
class TestWorkflowTemplateTenantIsolation:
    def test_templates_list_excludes_other_org(self, client_a, template_a, template_b):
        r = client_a.get('/api/v1/workflows/templates/')
        ids = [t['id'] for t in r.data['results']]
        assert str(template_a.id) in ids
        assert str(template_b.id) not in ids

    def test_retrieve_other_org_template_returns_404(self, client_a, template_b):
        r = client_a.get(f'/api/v1/workflows/templates/{template_b.id}/')
        assert r.status_code == 404

    def test_update_other_org_template_returns_404(self, client_a, template_b):
        r = client_a.patch(f'/api/v1/workflows/templates/{template_b.id}/', {
            'name': 'Hacked',
        }, format='json')
        assert r.status_code == 404

    def test_delete_other_org_template_returns_404(self, client_a, template_b):
        r = client_a.delete(f'/api/v1/workflows/templates/{template_b.id}/')
        assert r.status_code == 404

    def test_cannot_create_step_for_other_org_template(self, client_a, template_b):
        r = client_a.post('/api/v1/workflows/step-templates/', {
            'template': str(template_b.id),
            'step_number': 1,
            'name': 'Cross-org Step',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestWorkflowInstanceTenantIsolation:
    def test_instances_list_excludes_other_org(self, client_a, workflow_instance_a, workflow_instance_b):
        r = client_a.get('/api/v1/workflows/instances/')
        ids = [i['id'] for i in r.data['results']]
        assert str(workflow_instance_a.id) in ids
        assert str(workflow_instance_b.id) not in ids

    def test_retrieve_other_org_instance_returns_404(self, client_a, workflow_instance_b):
        r = client_a.get(f'/api/v1/workflows/instances/{workflow_instance_b.id}/')
        assert r.status_code == 404

    def test_cannot_instantiate_with_other_org_template(self, client_a, template_b, context_a):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_b.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cannot_instantiate_with_other_org_context(self, client_a, template_a, context_b, step_tpl_a):
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template_a.id),
            'operating_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestWorkflowStepInstanceTenantIsolation:
    def test_steps_list_excludes_other_org(self, client_a, workflow_instance_a, workflow_instance_b):
        r = client_a.get('/api/v1/workflows/steps/')
        step_ids_visible = [s['id'] for s in r.data['results']]
        org_b_steps = WorkflowStepInstance.objects.filter(
            workflow_instance=workflow_instance_b,
        )
        for step in org_b_steps:
            assert str(step.id) not in step_ids_visible

    def test_retrieve_other_org_step_returns_404(self, client_a, workflow_instance_b):
        step_b = WorkflowStepInstance.objects.filter(
            workflow_instance=workflow_instance_b,
        ).first()
        r = client_a.get(f'/api/v1/workflows/steps/{step_b.id}/')
        assert r.status_code == 404

    def test_cannot_advance_other_org_step(self, client_a, workflow_instance_b):
        step_b = WorkflowStepInstance.objects.filter(
            workflow_instance=workflow_instance_b,
        ).first()
        r = client_a.post(f'/api/v1/workflows/steps/{step_b.id}/advance/', {}, format='json')
        assert r.status_code == 404


@pytest.mark.django_db
class TestApprovalRouteTenantIsolation:
    def test_routes_list_excludes_other_org(self, client_a, route_a, route_b):
        r = client_a.get('/api/v1/approvals/routes/')
        ids = [x['id'] for x in r.data['results']]
        assert str(route_a.id) in ids
        assert str(route_b.id) not in ids

    def test_retrieve_other_org_route_returns_404(self, client_a, route_b):
        r = client_a.get(f'/api/v1/approvals/routes/{route_b.id}/')
        assert r.status_code == 404

    def test_update_other_org_route_returns_404(self, client_a, route_b):
        r = client_a.patch(f'/api/v1/approvals/routes/{route_b.id}/', {
            'name': 'Hacked',
        }, format='json')
        assert r.status_code == 404

    def test_delete_other_org_route_returns_404(self, client_a, route_b):
        r = client_a.delete(f'/api/v1/approvals/routes/{route_b.id}/')
        assert r.status_code == 404

    def test_cannot_create_step_for_other_org_route(self, client_a, route_b):
        r = client_a.post('/api/v1/approvals/steps/', {
            'route': str(route_b.id),
            'step_number': 1,
            'name': 'Cross-org Step',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestApprovalRequestTenantIsolation:
    def test_requests_list_excludes_other_org(self, client_a, approval_request_a, approval_request_b):
        r = client_a.get('/api/v1/approvals/requests/')
        ids = [x['id'] for x in r.data['results']]
        assert str(approval_request_a.id) in ids
        assert str(approval_request_b.id) not in ids

    def test_retrieve_other_org_request_returns_404(self, client_a, approval_request_b):
        r = client_a.get(f'/api/v1/approvals/requests/{approval_request_b.id}/')
        assert r.status_code == 404

    def test_cannot_approve_other_org_request(self, client_a, approval_request_b):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_b.id}/approve/',
            {'comment': 'Sneaky'},
            format='json',
        )
        assert r.status_code == 404

    def test_cannot_reject_other_org_request(self, client_a, approval_request_b):
        r = client_a.post(
            f'/api/v1/approvals/requests/{approval_request_b.id}/reject/',
            {'comment': 'Sneaky'},
            format='json',
        )
        assert r.status_code == 404

    def test_cannot_submit_with_other_org_context(self, client_a, context_b, approval_step_a):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_b.id),
            'approval_step': str(approval_step_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_cannot_submit_with_other_org_step(self, client_a, context_a, approval_step_b):
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(approval_step_b.id),
        }, format='json')
        assert r.status_code == 400
