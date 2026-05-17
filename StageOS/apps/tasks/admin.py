from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'operating_context', 'status', 'priority', 'assigned_to', 'due_date']
    list_filter = ['status', 'priority', 'evidence_required']
    search_fields = ['title']
    readonly_fields = ['id', 'completed_at', 'completed_by', 'created_at', 'updated_at']
