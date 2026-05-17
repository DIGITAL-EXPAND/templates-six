from django.contrib import admin
from .models import Supplier, SupplierDocument, SupplierEngagement, PaymentPack


class SupplierDocumentInline(admin.TabularInline):
    model = SupplierDocument
    extra = 0
    fields = ['document_type', 'file_name', 'status']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'csd_verified', 'bee_level']
    list_filter = ['status', 'csd_verified', 'bee_level']
    search_fields = ['name', 'contact_name', 'csd_number']
    readonly_fields = ['id', 'csd_verified', 'csd_verified_by', 'csd_verified_at', 'created_at', 'updated_at']
    inlines = [SupplierDocumentInline]


@admin.register(SupplierDocument)
class SupplierDocumentAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'document_type', 'status']
    list_filter = ['document_type', 'status']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(SupplierEngagement)
class SupplierEngagementAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'operating_context', 'role', 'status', 'value']
    list_filter = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PaymentPack)
class PaymentPackAdmin(admin.ModelAdmin):
    list_display = ['supplier_engagement', 'amount', 'status', 'erp_reference', 'submitted_date']
    list_filter = ['status']
    readonly_fields = ['id', 'erp_reference', 'submitted_date', 'created_at', 'updated_at']
