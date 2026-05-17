from django.contrib import admin
from .models import IntakeReview, ProducerAssignment, VenueHold, CalendarSlot


@admin.register(IntakeReview)
class IntakeReviewAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'reviewed_by', 'recommendation', 'status', 'review_date']
    list_filter = ['status', 'recommendation']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ProducerAssignment)
class ProducerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['producer', 'operating_context', 'is_primary', 'assigned_date']
    list_filter = ['is_primary']
    readonly_fields = ['id', 'assigned_date']


@admin.register(VenueHold)
class VenueHoldAdmin(admin.ModelAdmin):
    list_display = ['venue', 'operating_context', 'hold_date', 'hold_type', 'purpose']
    list_filter = ['hold_type', 'purpose']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(CalendarSlot)
class CalendarSlotAdmin(admin.ModelAdmin):
    list_display = ['venue', 'operating_context', 'date', 'slot_type', 'is_confirmed']
    list_filter = ['slot_type', 'is_confirmed']
    readonly_fields = ['id', 'created_at', 'updated_at']
