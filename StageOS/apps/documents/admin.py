from django.contrib import admin
from .models import Document, EvidenceSubmission


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'operating_context', 'uploaded_by', 'is_locked', 'created_at']
    list_filter = ['document_type', 'is_locked']
    search_fields = ['title', 'file_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EvidenceSubmission)
class EvidenceSubmissionAdmin(admin.ModelAdmin):
    list_display = ['document', 'task', 'submitted_by', 'accepted', 'rejected', 'accepted_at', 'rejected_at']
    list_filter = ['accepted', 'rejected']
    readonly_fields = ['id', 'created_at', 'updated_at']
