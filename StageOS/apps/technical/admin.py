from django.contrib import admin
from .models import TechnicalRider, CrewRequirement, EquipmentRequirement


class CrewRequirementInline(admin.TabularInline):
    model = CrewRequirement
    extra = 0
    fields = ['role', 'quantity', 'notes']


class EquipmentRequirementInline(admin.TabularInline):
    model = EquipmentRequirement
    extra = 0
    fields = ['item', 'quantity', 'source']


@admin.register(TechnicalRider)
class TechnicalRiderAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'crew_size', 'status', 'approved_by']
    list_filter = ['status']
    readonly_fields = ['id', 'approved_at', 'created_at', 'updated_at']
    inlines = [CrewRequirementInline, EquipmentRequirementInline]


@admin.register(CrewRequirement)
class CrewRequirementAdmin(admin.ModelAdmin):
    list_display = ['role', 'quantity', 'rider']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EquipmentRequirement)
class EquipmentRequirementAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'source', 'rider']
    list_filter = ['source']
    readonly_fields = ['id', 'created_at', 'updated_at']
