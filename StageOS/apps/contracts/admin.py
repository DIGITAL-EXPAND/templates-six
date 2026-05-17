from django.contrib import admin
from .models import ContractTemplate, ContractRecord, SignatureRecord


class SignatureRecordInline(admin.TabularInline):
    model = SignatureRecord
    extra = 0
    fields = ['signatory_name', 'signatory_role', 'signature_type', 'is_signed', 'signature_order']


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'contract_type', 'version', 'is_active']
    list_filter = ['contract_type', 'is_active']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ContractRecord)
class ContractRecordAdmin(admin.ModelAdmin):
    list_display = ['counterparty_name', 'contract_type', 'status', 'value', 'currency', 'issued_date']
    list_filter = ['contract_type', 'status', 'counterparty_type']
    search_fields = ['counterparty_name', 'notes']
    readonly_fields = ['id', 'signatures_received', 'created_at', 'updated_at']
    inlines = [SignatureRecordInline]


@admin.register(SignatureRecord)
class SignatureRecordAdmin(admin.ModelAdmin):
    list_display = ['signatory_name', 'signatory_role', 'contract', 'is_signed', 'signed_at']
    list_filter = ['is_signed', 'signature_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
