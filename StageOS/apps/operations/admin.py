from django.contrib import admin
from .models import FOHPlan, ShowDayChecklist, Incident


class ShowDayChecklistInline(admin.TabularInline):
    model = ShowDayChecklist
    extra = 0
    fields = ['item', 'is_checked', 'checked_by']


@admin.register(FOHPlan)
class FOHPlanAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'status', 'ushers', 'security']
    list_filter = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ShowDayChecklistInline]


@admin.register(ShowDayChecklist)
class ShowDayChecklistAdmin(admin.ModelAdmin):
    list_display = ['item', 'foh_plan', 'is_checked', 'checked_by']
    list_filter = ['is_checked']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_type', 'operating_context', 'severity', 'occurred_at', 'reported_by']
    list_filter = ['incident_type', 'severity']
    readonly_fields = ['id', 'created_at', 'updated_at']
