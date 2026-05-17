from django.contrib import admin
from .models import Artist, ArtistDocument, ArtistEngagement


class ArtistDocumentInline(admin.TabularInline):
    model = ArtistDocument
    extra = 0
    fields = ['document_type', 'file_name', 'status']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['legal_name', 'professional_name', 'discipline', 'status']
    list_filter = ['status', 'discipline']
    search_fields = ['legal_name', 'professional_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ArtistDocumentInline]


@admin.register(ArtistDocument)
class ArtistDocumentAdmin(admin.ModelAdmin):
    list_display = ['artist', 'document_type', 'status']
    list_filter = ['document_type', 'status']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ArtistEngagement)
class ArtistEngagementAdmin(admin.ModelAdmin):
    list_display = ['artist', 'operating_context', 'role', 'status', 'fee']
    list_filter = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']
