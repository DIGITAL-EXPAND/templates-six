from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone
from common.serializers import check_tenant_fk, ProtectedFieldsMixin
from .models import (
    WorkflowTemplate, WorkflowStepTemplate,
    WorkflowInstance, WorkflowStepInstance,
)


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'context_type', 'description',
            'is_active', 'version', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowStepTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStepTemplate
        fields = [
            'id', 'template', 'step_number', 'name',
            'owner_department', 'owner_role_description',
            'requires_approval', 'requires_evidence',
            'sla_days', 'description',
        ]
        read_only_fields = ['id']

    def validate_template(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Template')

    def validate_owner_department(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner department')


class WorkflowInstanceSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'template', 'operating_context',
            'status', 'started_at', 'completed_at',
        ]
        read_only_fields = ['id', 'status', 'started_at', 'completed_at']

    def validate_template(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Template')

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')


class WorkflowStepInstanceSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'started_at', 'completed_at', 'completed_by')
    owner_department = serializers.UUIDField(source='step_template.owner_department_id', read_only=True)
    owner_role_description = serializers.CharField(source='step_template.owner_role_description', read_only=True)
    requires_approval = serializers.BooleanField(source='step_template.requires_approval', read_only=True)
    requires_evidence = serializers.BooleanField(source='step_template.requires_evidence', read_only=True)
    sla_days = serializers.IntegerField(source='step_template.sla_days', read_only=True)
    due_date = serializers.SerializerMethodField()
    blockers = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowStepInstance
        fields = [
            'id', 'workflow_instance', 'step_template', 'step_number',
            'status', 'assigned_to', 'started_at', 'completed_at',
            'completed_by', 'evidence_document', 'approval_request', 'notes',
            'owner_department', 'owner_role_description', 'requires_approval',
            'requires_evidence', 'sla_days', 'due_date', 'blockers',
        ]
        read_only_fields = [
            'id', 'step_number', 'status', 'started_at',
            'completed_at', 'completed_by',
        ]

    def validate_workflow_instance(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Workflow instance')

    def validate_step_template(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Step template')

    def validate_assigned_to(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Assigned user')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')

    def validate_approval_request(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Approval')

    def get_due_date(self, obj):
        if obj.step_template.sla_days is None:
            return None
        basis = obj.started_at or obj.workflow_instance.started_at
        if not basis:
            return None
        return (basis + timedelta(days=obj.step_template.sla_days)).date()

    def get_blockers(self, obj):
        blockers = []
        if obj.status in {'completed', 'skipped'}:
            return blockers
        if obj.step_template.requires_evidence and obj.evidence_document_id is None:
            blockers.append('Evidence is required before this Process Step can be completed.')
        if obj.step_template.requires_approval:
            if obj.approval_request_id is None:
                blockers.append('Approval is required before this Process Step can be completed.')
            elif obj.approval_request.decision not in {'approved', 'exception_approved'}:
                blockers.append('Linked Approval is not approved.')
        due_date = self.get_due_date(obj)
        if due_date and due_date < timezone.localdate():
            blockers.append('Process Step SLA is overdue.')
        return blockers


class AdvanceStepSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, default='', allow_blank=True)
    evidence_document = serializers.UUIDField(required=False, allow_null=True, default=None)
    approval_request = serializers.UUIDField(required=False, allow_null=True, default=None)
