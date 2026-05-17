from django.contrib import admin
from .models import (
    YouthProject, Activity, Session, LearnerGroup, FacilitatorAssignment,
    ConsentRecord, AttendanceRecord, Assessment, ShowcaseOutput,
)


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0
    fields = ['name', 'activity_type', 'recurrence', 'start_date']


class LearnerGroupInline(admin.TabularInline):
    model = LearnerGroup
    extra = 0
    fields = ['name']


@admin.register(YouthProject)
class YouthProjectAdmin(admin.ModelAdmin):
    list_display = ['operating_context', 'status', 'target_learners', 'target_schools']
    list_filter = ['status']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ActivityInline, LearnerGroupInline]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'youth_project', 'activity_type', 'recurrence', 'start_date']
    list_filter = ['activity_type', 'recurrence']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['activity', 'session_date', 'status', 'attendance_captured']
    list_filter = ['status', 'attendance_captured']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(LearnerGroup)
class LearnerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'youth_project']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(FacilitatorAssignment)
class FacilitatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['facilitator', 'youth_project', 'role', 'is_vetted']
    list_filter = ['is_vetted']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ['learner_identifier', 'youth_project', 'guardian_consent_received', 'consent_date']
    list_filter = ['guardian_consent_received', 'photo_consent']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['learner_identifier', 'session', 'present', 'arrival_time']
    list_filter = ['present']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['learner_identifier', 'youth_project', 'assessment_type', 'score', 'assessment_date']
    list_filter = ['assessment_type']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ShowcaseOutput)
class ShowcaseOutputAdmin(admin.ModelAdmin):
    list_display = ['title', 'youth_project', 'output_type', 'date']
    list_filter = ['output_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
