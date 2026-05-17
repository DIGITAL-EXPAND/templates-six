from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from common.permissions import CanAccessYouthSensitiveData
from .models import (
    YouthProject, Activity, Session, LearnerGroup, FacilitatorAssignment,
    ConsentRecord, AttendanceRecord, Assessment, ShowcaseOutput,
)
from .serializers import (
    YouthProjectSerializer, ActivitySerializer, SessionSerializer,
    LearnerGroupSerializer, FacilitatorAssignmentSerializer,
    ConsentRecordSerializer, AttendanceRecordSerializer,
    AssessmentSerializer, ShowcaseOutputSerializer,
)
from .services import (
    create_youth_project, capture_session_attendance, get_project_stats,
    set_youth_project_status, receive_consent, withdraw_consent,
    vet_facilitator, complete_session,
)


class YouthProjectViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = YouthProject.objects.select_related('operating_context')
    serializer_class = YouthProjectSerializer
    filterset_fields = ['operating_context', 'status']
    ordering = ['-created_at']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        project = create_youth_project(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = project

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        project = self.get_object()
        data = get_project_stats(project)
        return Response(data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        updated = set_youth_project_status(self.get_object(), request.user, 'active', request.data.get('comment', ''))
        return Response(YouthProjectSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        updated = set_youth_project_status(self.get_object(), request.user, 'completed', request.data.get('comment', ''))
        return Response(YouthProjectSerializer(updated, context={'request': request}).data)


class ActivityViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Activity.objects.select_related('youth_project', 'venue', 'space')
    serializer_class = ActivitySerializer
    filterset_fields = ['youth_project', 'activity_type', 'recurrence']
    ordering = ['name']


class SessionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Session.objects.select_related('activity', 'venue')
    serializer_class = SessionSerializer
    filterset_fields = ['activity', 'status', 'session_date', 'attendance_captured']
    ordering = ['session_date', 'start_time']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]

    @action(detail=True, methods=['post'], url_path='capture-attendance')
    def capture_attendance(self, request, pk=None):
        session = self.get_object()
        attendance_data = request.data.get('attendance', [])
        records = capture_session_attendance(session, request.user, attendance_data)
        return Response({
            'session_id': str(session.id),
            'records_captured': len(records),
            'attendance_captured': True,
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        updated = complete_session(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(SessionSerializer(updated, context={'request': request}).data)


class LearnerGroupViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = LearnerGroup.objects.select_related('youth_project')
    serializer_class = LearnerGroupSerializer
    filterset_fields = ['youth_project']
    ordering = ['name']


class FacilitatorAssignmentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FacilitatorAssignment.objects.select_related(
        'youth_project', 'activity', 'facilitator',
    )
    serializer_class = FacilitatorAssignmentSerializer
    filterset_fields = ['youth_project', 'activity', 'facilitator', 'is_vetted']
    ordering = ['-created_at']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]

    @action(detail=True, methods=['post'])
    def vet(self, request, pk=None):
        updated = vet_facilitator(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(FacilitatorAssignmentSerializer(updated, context={'request': request}).data)


class ConsentRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ConsentRecord.objects.select_related('youth_project', 'learner_group')
    serializer_class = ConsentRecordSerializer
    filterset_fields = ['youth_project', 'learner_group', 'guardian_consent_received']
    ordering = ['learner_identifier']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]

    @action(detail=True, methods=['post'], url_path='receive-consent')
    def receive(self, request, pk=None):
        updated = receive_consent(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ConsentRecordSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='withdraw-consent')
    def withdraw(self, request, pk=None):
        updated = withdraw_consent(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ConsentRecordSerializer(updated, context={'request': request}).data)


class AttendanceRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related('session', 'learner_group')
    serializer_class = AttendanceRecordSerializer
    filterset_fields = ['session', 'learner_group', 'present']
    ordering = ['learner_identifier']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]


class AssessmentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Assessment.objects.select_related('youth_project', 'activity', 'assessor')
    serializer_class = AssessmentSerializer
    filterset_fields = ['youth_project', 'activity', 'assessment_type', 'learner_identifier']
    ordering = ['-assessment_date']
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessYouthSensitiveData]


class ShowcaseOutputViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ShowcaseOutput.objects.select_related('youth_project', 'output_context')
    serializer_class = ShowcaseOutputSerializer
    filterset_fields = ['youth_project', 'output_type']
    ordering = ['-created_at']
