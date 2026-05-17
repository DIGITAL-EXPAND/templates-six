from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, validate_unique_context, ProtectedFieldsMixin,
    require_non_negative, require_ordered_dates,
)
from .models import (
    YouthProject, Activity, Session, LearnerGroup, FacilitatorAssignment,
    ConsentRecord, AttendanceRecord, Assessment, ShowcaseOutput,
)


class YouthProjectSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = YouthProject
        fields = [
            'id', 'operating_context', 'target_learners', 'target_schools',
            'age_range_min', 'age_range_max', 'safeguarding_notes',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['target_learners', 'target_schools', 'age_range_min', 'age_range_max'])
        min_age = attrs.get('age_range_min')
        max_age = attrs.get('age_range_max')
        if min_age is not None and max_age is not None and max_age < min_age:
            raise serializers.ValidationError({'age_range_max': 'Maximum age cannot be below minimum age.'})
        return attrs


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            'id', 'youth_project', 'name', 'activity_type', 'venue', 'space',
            'recurrence', 'start_date', 'end_date', 'day_of_week',
            'start_time', 'end_time', 'facilitator_count', 'max_learners',
            'description', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate_space(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Space')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['facilitator_count', 'max_learners'])
        require_ordered_dates(attrs, 'start_date', 'end_date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError({'end_time': 'End time cannot be before start time.'})
        project = attrs.get('youth_project', getattr(self.instance, 'youth_project', None))
        venue = attrs.get('venue', getattr(self.instance, 'venue', None))
        space = attrs.get('space', getattr(self.instance, 'space', None))
        if project and venue and venue.organisation_id != project.organisation_id:
            raise serializers.ValidationError('Venue must belong to the youth project organisation.')
        if project and space and space.organisation_id != project.organisation_id:
            raise serializers.ValidationError('Space must belong to the youth project organisation.')
        return attrs


class SessionSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status', 'attendance_captured')
    class Meta:
        model = Session
        fields = [
            'id', 'activity', 'session_date', 'start_time', 'end_time',
            'venue', 'status', 'facilitator_notes', 'attendance_captured',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'attendance_captured', 'created_at', 'updated_at']

    def validate_activity(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Activity')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError({'end_time': 'End time cannot be before start time.'})
        return attrs


class LearnerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerGroup
        fields = ['id', 'youth_project', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')


class FacilitatorAssignmentSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('is_vetted', 'vetting_date')
    class Meta:
        model = FacilitatorAssignment
        fields = [
            'id', 'youth_project', 'activity', 'facilitator', 'role',
            'start_date', 'end_date', 'is_vetted', 'vetting_date',
            'vetting_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_vetted', 'vetting_date', 'created_at', 'updated_at']

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')

    def validate_activity(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Activity')

    def validate_facilitator(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Facilitator')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        project = attrs.get('youth_project', getattr(self.instance, 'youth_project', None))
        facilitator = attrs.get('facilitator', getattr(self.instance, 'facilitator', None))
        activity = attrs.get('activity', getattr(self.instance, 'activity', None))
        if project and facilitator and activity is not None:
            qs = FacilitatorAssignment.objects.filter(
                youth_project=project, facilitator=facilitator, activity=activity,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    'This facilitator is already assigned to this activity in this project.'
                )
        require_ordered_dates(attrs, 'start_date', 'end_date')
        return attrs


class ConsentRecordSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('guardian_consent_received', 'withdrawal_date')
    class Meta:
        model = ConsentRecord
        fields = [
            'id', 'youth_project', 'learner_identifier', 'learner_group',
            'guardian_consent_received', 'consent_date', 'consent_document',
            'photo_consent', 'data_processing_consent', 'withdrawal_date',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'guardian_consent_received', 'consent_date', 'withdrawal_date',
            'created_at', 'updated_at',
        ]

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')

    def validate_learner_group(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Learner group')

    def validate_consent_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Consent document')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        project = attrs.get('youth_project', getattr(self.instance, 'youth_project', None))
        identifier = attrs.get('learner_identifier', getattr(self.instance, 'learner_identifier', None))
        if project and identifier:
            qs = ConsentRecord.objects.filter(
                youth_project=project, learner_identifier=identifier,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    'A consent record already exists for this learner in this project.'
                )
        consent_date = attrs.get('consent_date', getattr(self.instance, 'consent_date', None))
        withdrawal_date = attrs.get('withdrawal_date', getattr(self.instance, 'withdrawal_date', None))
        if consent_date and withdrawal_date and withdrawal_date < consent_date:
            raise serializers.ValidationError({'withdrawal_date': 'Withdrawal date cannot be before consent date.'})
        return attrs


class AttendanceRecordSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('present',)
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'session', 'learner_identifier', 'learner_group',
            'present', 'arrival_time', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'present', 'created_at', 'updated_at']

    def validate_session(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Session')

    def validate_learner_group(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Learner group')


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            'id', 'youth_project', 'activity', 'learner_identifier',
            'assessment_type', 'score', 'assessor', 'assessment_date',
            'notes', 'evidence_document', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')

    def validate_activity(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Activity')

    def validate_assessor(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Assessor')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')


class ShowcaseOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowcaseOutput
        fields = [
            'id', 'youth_project', 'output_context', 'title',
            'output_type', 'date', 'description', 'evidence_document',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_youth_project(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Youth project')

    def validate_output_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Output context')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')
