from django.contrib import admin
from .models import ApprovalRoute, ApprovalStep, ApprovalRequest


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 0
    fields = ['step_number', 'name', 'approver_role_description', 'can_delegate']


@admin.register(ApprovalRoute)
class ApprovalRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'context_type', 'is_active']
    list_filter = ['context_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ApprovalStepInline]


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'route', 'step_number', 'can_delegate']
    readonly_fields = ['id']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'approval_step', 'requested_by', 'decision', 'decided_at']
    list_filter = ['decision']
    readonly_fields = ['id', 'requested_at', 'decided_at', 'decided_by']
