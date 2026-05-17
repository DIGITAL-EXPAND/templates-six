from django.contrib import admin
from .models import OperatingContext


@admin.register(OperatingContext)
class OperatingContextAdmin(admin.ModelAdmin):
    list_display = ['title', 'context_type', 'status', 'site', 'owner', 'opening_date', 'readiness_score']
    list_filter = ['context_type', 'status', 'priority', 'risk_level', 'is_public']
    search_fields = ['title', 'synopsis', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['site', 'venue', 'primary_space', 'department', 'owner', 'parent_context']
    date_hierarchy = 'opening_date'
    fieldsets = (
        ('Identity', {'fields': ('id', 'title', 'context_type', 'status', 'priority', 'risk_level', 'synopsis')}),
        ('Location & Ownership', {'fields': ('site', 'venue', 'primary_space', 'department', 'owner')}),
        ('Dates', {'fields': ('start_date', 'end_date', 'opening_date', 'closing_date')}),
        ('Financial', {'fields': ('budget', 'actual_spend')}),
        ('Marketing & Ticketing', {'fields': ('ticketing_provider', 'campaign_level')}),
        ('Governance', {'fields': ('kpi_link', 'readiness_score', 'is_public', 'parent_context')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
