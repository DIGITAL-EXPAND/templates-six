from django.contrib import admin
from .models import WorkflowTemplate, WorkflowStepTemplate, WorkflowInstance, WorkflowStepInstance


class WorkflowStepTemplateInline(admin.TabularInline):
    model = WorkflowStepTemplate
    extra = 0
    fields = ['step_number', 'name', 'requires_approval', 'requires_evidence', 'sla_days']


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'context_type', 'version', 'is_active']
    list_filter = ['context_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [WorkflowStepTemplateInline]


@admin.register(WorkflowStepTemplate)
class WorkflowStepTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'step_number', 'requires_approval', 'requires_evidence']
    list_filter = ['requires_approval', 'requires_evidence']
    readonly_fields = ['id']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['template', 'operating_context', 'status', 'started_at', 'completed_at']
    list_filter = ['status']
    readonly_fields = ['id', 'started_at', 'completed_at']


@admin.register(WorkflowStepInstance)
class WorkflowStepInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow_instance', 'step_number', 'status', 'assigned_to', 'completed_at']
    list_filter = ['status']
    readonly_fields = ['id', 'started_at', 'completed_at', 'completed_by']
