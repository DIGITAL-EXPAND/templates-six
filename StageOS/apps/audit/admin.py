from django.contrib import admin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'target_type', 'target_id', 'organisation', 'actor', 'created_at']
    list_filter = ['event_type', 'target_type', 'organisation']
    search_fields = ['event_type', 'target_type', 'target_id', 'actor__email']
    readonly_fields = [
        'id', 'organisation', 'actor', 'event_type', 'target_type', 'target_id',
        'old_value', 'new_value', 'reason', 'payload', 'created_at',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
