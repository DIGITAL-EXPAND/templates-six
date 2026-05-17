import pytest
from rest_framework.exceptions import ValidationError

from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate, WorkflowInstance, WorkflowStepInstance
from apps.workflows.services import instantiate_workflow, advance_step, EvidenceRequired
from apps.audit.models import AuditEvent
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
        name='Pre-Production',
    )


@pytest.fixture
def step_tpl_2(db, org_a, template_a):
    return WorkflowStepTemplate.objects.create(
        organisation=org_a,
        template=template_a,
        step_number=2,
        name='Evidence Step',
        requires_evidence=True,
    )


@pytest.mark.django_db
class TestInstantiateWorkflowService:
    def test_creates_instance_and_steps(self, context_a, template_a, step_tpl_1, step_tpl_2, user_a):
        instance = instantiate_workflow(context=context_a, template=template_a, user=user_a)
        assert instance.status == 'active'
        assert instance.template == template_a
        assert WorkflowStepInstance.objects.filter(workflow_instance=instance).count() == 2

    def test_first_step_in_progress(self, context_a, template_a, step_tpl_1, step_tpl_2, user_a):
        instance = instantiate_workflow(context=context_a, template=template_a, user=user_a)
        first = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        assert first.status == 'in_progress'

    def test_remaining_steps_pending(self, context_a, template_a, step_tpl_1, step_tpl_2, user_a):
        instance = instantiate_workflow(context=context_a, template=template_a, user=user_a)
        second = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        assert second.status == 'pending'

    def test_creates_audit_event(self, context_a, template_a, step_tpl_1, user_a):
        instantiate_workflow(context=context_a, template=template_a, user=user_a)
        event = AuditEvent.objects.filter(event_type='workflow.instantiated').first()
        assert event is not None
        assert event.actor == user_a

    def test_context_type_mismatch_raises(self, context_a, org_a, user_a):
        festival_tpl = WorkflowTemplate.objects.create(
            organisation=org_a, name='Festival', context_type='festival',
        )
        with pytest.raises(ValidationError):
            instantiate_workflow(context=context_a, template=festival_tpl, user=user_a)


@pytest.mark.django_db
class TestAdvanceStepService:
    @pytest.fixture
    def instance(self, context_a, template_a, step_tpl_1, step_tpl_2, user_a):
        return instantiate_workflow(context=context_a, template=template_a, user=user_a)

    def test_advance_marks_step_completed(self, instance, user_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        step1.refresh_from_db()
        assert step1.status == 'completed'
        assert step1.completed_by == user_a
        assert step1.completed_at is not None

    def test_advance_activates_next_step(self, instance, user_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        step2 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        assert step2.status == 'in_progress'

    def test_advance_last_step_completes_workflow(self, instance, user_a, document_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        step2 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        advance_step(step2, user_a, evidence_document=document_a)
        instance.refresh_from_db()
        assert instance.status == 'completed'

    def test_advance_non_in_progress_raises_validation_error(self, instance, user_a):
        step2 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        with pytest.raises(ValidationError):
            advance_step(step2, user_a)

    def test_advance_without_evidence_when_required_raises_422(self, instance, user_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        step2 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        with pytest.raises(EvidenceRequired):
            advance_step(step2, user_a)

    def test_advance_with_evidence_succeeds(self, instance, user_a, document_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        step2 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=2)
        result = advance_step(step2, user_a, evidence_document=document_a)
        assert result.status == 'completed'
        assert result.evidence_document == document_a

    def test_approval_required_without_approval_raises(self, instance, user_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        step1.step_template.requires_approval = True
        step1.step_template.save(update_fields=['requires_approval'])
        with pytest.raises(ValidationError):
            advance_step(step1, user_a)

    def test_approval_required_with_approved_approval_succeeds(self, instance, user_a, org_a, context_a):
        route = ApprovalRoute.objects.create(organisation=org_a, name='Process Route')
        approval_step = ApprovalStep.objects.create(
            organisation=org_a, route=route, step_number=1, name='Process Approval',
        )
        approval = ApprovalRequest.objects.create(
            organisation=org_a, operating_context=context_a,
            approval_step=approval_step, requested_by=user_a,
            decision=ApprovalDecision.EXCEPTION_APPROVED,
            decided_by=user_a,
        )
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        step1.step_template.requires_approval = True
        step1.step_template.save(update_fields=['requires_approval'])
        result = advance_step(step1, user_a, approval_request=approval)
        assert result.status == 'completed'
        assert result.approval_request == approval

    def test_creates_audit_event(self, instance, user_a):
        step1 = WorkflowStepInstance.objects.get(workflow_instance=instance, step_number=1)
        advance_step(step1, user_a)
        event = AuditEvent.objects.filter(event_type='workflow.step_completed').first()
        assert event is not None
