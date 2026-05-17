from django.contrib import admin
from .models import Campaign, CampaignDeliverable


class CampaignDeliverableInline(admin.TabularInline):
    model = CampaignDeliverable
    extra = 0
    fields = ['deliverable_type', 'title', 'status', 'due_date']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'campaign_level', 'status', 'owner']
    list_filter = ['status', 'campaign_level']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [CampaignDeliverableInline]


@admin.register(CampaignDeliverable)
class CampaignDeliverableAdmin(admin.ModelAdmin):
    list_display = ['title', 'campaign', 'deliverable_type', 'status', 'due_date']
    list_filter = ['status', 'deliverable_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
