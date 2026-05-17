from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from common.permissions import CanAccessPrivateIntake, IsTenantMember, UserRoles, user_type
from .models import (
    CalendarIssue, CalendarIssueStatus, IntakeRequest, IntakeRequestStatus,
    IntakeReview, ProducerAssignment, VenueHold, CalendarSlot,
)
from .serializers import (
    CalendarIssueActionSerializer, CalendarIssueSerializer,
    IntakeConvertSerializer, IntakeDecisionSerializer, IntakeRequestSerializer,
    IntakeReviewSerializer, ProducerAssignmentSerializer,
    VenueHoldSerializer, CalendarSlotSerializer,
)
from .services import (
    assign_producer, change_calendar_issue_status, convert_intake_to_context,
    create_calendar_issue, create_calendar_slot, create_intake_request, create_venue_hold,
    decide_intake_request, mark_intake_under_review, require_programming_calendar_authority,
    update_calendar_slot, update_venue_hold,
)


class IntakeRequestViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IntakeRequest.objects.select_related(
        'preferred_venue', 'submitted_by', 'reviewed_by', 'decided_by', 'converted_context',
    )
    serializer_class = IntakeRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessPrivateIntake]
    filterset_fields = ['request_type', 'status', 'preferred_venue', 'converted_context']
    search_fields = ['event_title', 'client_name', 'client_organisation', 'contact_email']
    ordering_fields = ['created_at', 'requested_start_date', 'event_title']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.CLIENT_EXTERNAL:
            return qs.filter(submitted_by=self.request.user)
        return qs

    def perform_create(self, serializer):
        intake_request = create_intake_request(
            organisation=self.request.user.organisation,
            user=self.request.user,
            data=serializer.validated_data,
        )
        serializer.instance = intake_request

    @action(detail=True, methods=['post'], url_path='start-review')
    def start_review(self, request, pk=None):
        intake_request = self.get_object()
        serializer = IntakeDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = mark_intake_under_review(
            intake_request,
            request.user,
            serializer.validated_data.get('comment', ''),
        )
        return Response(IntakeRequestSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self._decide(request, IntakeRequestStatus.APPROVED)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        return self._decide(request, IntakeRequestStatus.DECLINED)

    @action(detail=True, methods=['post'])
    def defer(self, request, pk=None):
        return self._decide(request, IntakeRequestStatus.DEFERRED)

    @action(detail=True, methods=['post'], url_path='request-changes')
    def request_changes(self, request, pk=None):
        return self._decide(request, IntakeRequestStatus.CHANGES_REQUESTED)

    @action(detail=True, methods=['post'], url_path='convert-to-workspace')
    def convert_to_workspace(self, request, pk=None):
        intake_request = self.get_object()
        serializer = IntakeConvertSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        context = convert_intake_to_context(
            intake_request,
            request.user,
            serializer.validated_data,
        )
        return Response({'workspace_id': str(context.id)}, status=status.HTTP_201_CREATED)

    def _decide(self, request, decision_status):
        intake_request = self.get_object()
        serializer = IntakeDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = decide_intake_request(
            intake_request,
            request.user,
            decision_status,
            serializer.validated_data.get('comment', ''),
        )
        return Response(IntakeRequestSerializer(updated, context={'request': request}).data)


class IntakeReviewViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = IntakeReview.objects.select_related('operating_context', 'reviewed_by')
    serializer_class = IntakeReviewSerializer
    filterset_fields = ['status', 'recommendation']
    ordering = ['-created_at']


class ProducerAssignmentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ProducerAssignment.objects.select_related(
        'operating_context', 'producer', 'assigned_by',
    )
    serializer_class = ProducerAssignmentSerializer
    filterset_fields = ['operating_context', 'producer', 'is_primary']
    ordering = ['-assigned_date']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        producer = vd.pop('producer')
        assignment = assign_producer(
            context=context_obj,
            producer=producer,
            assigned_by=self.request.user,
            **vd,
        )
        serializer.instance = assignment


class VenueHoldViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueHold.objects.select_related(
        'operating_context', 'venue', 'space', 'held_by',
    )
    serializer_class = VenueHoldSerializer
    filterset_fields = ['operating_context', 'venue', 'hold_date', 'hold_type']
    ordering = ['hold_date', 'start_time']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        hold = create_venue_hold(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = hold

    def perform_update(self, serializer):
        hold = update_venue_hold(serializer.instance, self.request.user, dict(serializer.validated_data))
        serializer.instance = hold

    def destroy(self, request, *args, **kwargs):
        require_programming_calendar_authority(request.user)
        return super().destroy(request, *args, **kwargs)


class CalendarSlotViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CalendarSlot.objects.select_related('operating_context', 'venue')
    serializer_class = CalendarSlotSerializer
    filterset_fields = ['operating_context', 'venue', 'date', 'slot_type', 'is_confirmed']
    ordering = ['date']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        slot = create_calendar_slot(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = slot

    def perform_update(self, serializer):
        slot = update_calendar_slot(serializer.instance, self.request.user, dict(serializer.validated_data))
        serializer.instance = slot

    def destroy(self, request, *args, **kwargs):
        require_programming_calendar_authority(request.user)
        return super().destroy(request, *args, **kwargs)


class CalendarIssueViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CalendarIssue.objects.select_related(
        'operating_context', 'venue_hold', 'calendar_slot', 'department',
        'raised_by', 'resolved_by',
    )
    serializer_class = CalendarIssueSerializer
    filterset_fields = [
        'operating_context', 'venue_hold', 'calendar_slot',
        'department', 'severity', 'status', 'due_date',
    ]
    search_fields = ['title', 'description', 'resolution_note']
    ordering_fields = ['created_at', 'due_date', 'severity', 'status']
    ordering = ['status', '-created_at']

    def perform_create(self, serializer):
        issue = create_calendar_issue(
            organisation=self.request.user.organisation,
            user=self.request.user,
            data=serializer.validated_data,
        )
        serializer.instance = issue

    @action(detail=True, methods=['post'])
    def progress(self, request, pk=None):
        return self._change_status(request, CalendarIssueStatus.IN_PROGRESS)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        return self._change_status(request, CalendarIssueStatus.RESOLVED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        return self._change_status(request, CalendarIssueStatus.CANCELLED)

    def _change_status(self, request, new_status):
        issue = self.get_object()
        serializer = CalendarIssueActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = change_calendar_issue_status(
            issue,
            request.user,
            new_status,
            serializer.validated_data.get('note', ''),
        )
        return Response(CalendarIssueSerializer(updated, context={'request': request}).data)
