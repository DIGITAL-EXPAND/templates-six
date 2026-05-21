from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from common.permissions import CanAccessPrivateIntake, IsTenantMember, UserRoles, user_type
from .models import (
    CalendarIssue, CalendarIssueStatus, IntakeRequest, IntakeRequestStatus,
    IntakeReview, ProducerAssignment, VenueHold, CalendarSlot,
    Season, Show, Performance, ProductionLicence,
)
from .serializers import (
    CalendarIssueActionSerializer, CalendarIssueSerializer,
    IntakeConvertSerializer, IntakeDecisionSerializer, IntakeRequestSerializer,
    IntakeReviewSerializer, ProducerAssignmentSerializer,
    VenueHoldSerializer, CalendarSlotSerializer,
    SeasonSerializer, ShowSerializer, PerformanceSerializer,
    ProductionLicenceSerializer,
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


class SeasonViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Season.objects.select_related('organisation')
    serializer_class = SeasonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['organisation', 'year', 'is_active']
    search_fields = ['name']
    ordering_fields = ['year', 'name']
    ordering = ['-year', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(organisation=self.request.user.organisation)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Aggregate season analytics: shows, performances, tickets sold, gross revenue."""
        from apps.ticketing.models import Booking, Ticket
        season = self.get_object()
        shows = season.shows.filter(organisation=request.user.organisation)
        show_ids = list(shows.values_list('id', flat=True))
        performances = Performance.objects.filter(
            show_id__in=show_ids, organisation=request.user.organisation
        )
        bookings = Booking.objects.filter(
            performance__in=performances, organisation=request.user.organisation
        )
        tickets = Ticket.objects.filter(booking__in=bookings)
        gross_revenue = tickets.aggregate(total=models.Sum('amount'))['total'] or 0
        return Response({
            'season_id': str(season.id),
            'season_name': season.name,
            'year': season.year,
            'show_count': shows.count(),
            'performance_count': performances.count(),
            'total_bookings': bookings.count(),
            'tickets_sold': tickets.count(),
            'gross_revenue': str(gross_revenue),
        })


    @action(detail=True, methods=['get'])
    def close_out_summary(self, request, pk=None):
        """Season close-out: aggregate financials across all shows."""
        from apps.ticketing.models import Ticket, Booking
        from apps.artists.models import ArtistPayment
        season = self.get_object()
        org = request.user.organisation
        shows = season.shows.filter(organisation=org)
        show_summaries = []
        total_revenue = 0
        total_costs = 0
        for show in shows:
            performances = show.performances.filter(organisation=org)
            bookings = Booking.objects.filter(performance__in=performances)
            rev = Ticket.objects.filter(booking__in=bookings).aggregate(
                t=models.Sum('amount'))['t'] or 0
            costs = ArtistPayment.objects.filter(
                engagement__operating_context=show.operating_context,
                status='paid', organisation=org,
            ).aggregate(t=models.Sum('amount'))['t'] or 0
            total_revenue += rev
            total_costs += costs
            ctx = show.operating_context
            show_summaries.append({
                'show_id': str(show.id),
                'title': ctx.title if ctx else '',
                'status': ctx.status if ctx else '',
                'performances': performances.count(),
                'ticket_revenue': str(rev),
                'artist_costs': str(costs),
                'net': str(rev - costs),
            })
        return Response({
            'season_id': str(season.id),
            'season_name': season.name,
            'year': season.year,
            'shows': show_summaries,
            'totals': {
                'total_revenue': str(total_revenue),
                'total_costs': str(total_costs),
                'net_position': str(total_revenue - total_costs),
            },
        })


class ShowViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Show.objects.select_related('operating_context', 'season')
    serializer_class = ShowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['operating_context', 'season', 'status', 'genre']
    search_fields = ['title', 'subtitle', 'synopsis', 'producer_name']
    ordering_fields = ['created_at', 'title', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['get'])
    def lifecycle(self, request, pk=None):
        """Full production timeline for a show."""
        from apps.artists.models import ArtistEngagement, ArtistPayment
        from apps.contracts.models import ContractRecord
        from apps.technical.models import TechnicalRider
        from apps.ticketing.models import Booking, Ticket
        from apps.operations.models import ShowCall, PostShowReport

        show = self.get_object()
        org = request.user.organisation

        performances = show.performances.filter(organisation=org).order_by('performance_date', 'start_time')
        engagements = ArtistEngagement.objects.filter(
            operating_context=show.operating_context, organisation=org
        ).select_related('artist')
        payments = ArtistPayment.objects.filter(
            engagement__operating_context=show.operating_context, organisation=org
        )
        contracts = ContractRecord.objects.filter(
            operating_context=show.operating_context, organisation=org
        )
        try:
            rider = TechnicalRider.objects.get(operating_context=show.operating_context, organisation=org)
            rider_data = {
                'status': rider.status,
                'crew_size': rider.crew_size,
                'load_in_date': str(rider.load_in_date) if rider.load_in_date else None,
            }
        except TechnicalRider.DoesNotExist:
            rider_data = None

        ctx = show.operating_context
        show_calls = ShowCall.objects.filter(operating_context=ctx, organisation=org) if ctx else ShowCall.objects.none()
        post_show = PostShowReport.objects.filter(operating_context=ctx, organisation=org) if ctx else PostShowReport.objects.none()
        bookings = Booking.objects.filter(performance__show=show, organisation=org)
        ticket_revenue = Ticket.objects.filter(booking__in=bookings).aggregate(
            total=models.Sum('amount'))['total'] or 0
        paid_costs = payments.filter(status='paid').aggregate(
            total=models.Sum('amount'))['total'] or 0

        return Response({
            'show_id': str(show.id),
            'title': ctx.title if ctx else '',
            'status': ctx.status if ctx else '',
            'budget_approved': str(show.budget_approved or 0),
            'revenue_target': str(show.revenue_target or 0),
            'performances': [
                {
                    'id': str(p.id),
                    'date': str(p.performance_date),
                    'start_time': str(p.start_time),
                    'end_time': str(p.end_time) if p.end_time else None,
                    'expected_audience': p.expected_audience,
                }
                for p in performances
            ],
            'engagements': [
                {
                    'id': str(e.id),
                    'artist_name': e.artist.professional_name or e.artist.legal_name,
                    'role': e.role,
                    'fee': str(e.fee),
                    'status': e.status,
                }
                for e in engagements
            ],
            'payments': [
                {
                    'id': str(p.id),
                    'milestone': p.milestone,
                    'amount': str(p.amount),
                    'status': p.status,
                    'paid_date': str(p.paid_date) if p.paid_date else None,
                }
                for p in payments
            ],
            'contracts': [
                {
                    'id': str(c.id),
                    'contract_type': c.contract_type,
                    'status': c.status,
                    'expiry_date': str(c.expiry_date) if c.expiry_date else None,
                }
                for c in contracts
            ],
            'technical_rider': rider_data,
            'show_calls_count': show_calls.count(),
            'post_show_reports_count': post_show.count(),
            'financial_summary': {
                'ticket_revenue': str(ticket_revenue),
                'artist_costs_paid': str(paid_costs),
                'net_position': str(ticket_revenue - paid_costs),
            },
        })

    @action(detail=True, methods=['post'])
    def close_out(self, request, pk=None):
        """Mark a show as completed and generate final financial summary."""
        from apps.ticketing.models import Booking, Ticket
        from apps.artists.models import ArtistPayment
        show = self.get_object()
        ctx = show.operating_context
        if ctx:
            ctx.status = 'completed'
            ctx.save(update_fields=['status'])
        org = request.user.organisation
        performances = show.performances.filter(organisation=org)
        bookings = Booking.objects.filter(performance__in=performances)
        ticket_revenue = Ticket.objects.filter(
            booking__in=bookings
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        paid_costs = ArtistPayment.objects.filter(
            engagement__operating_context=ctx, status='paid', organisation=org
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return Response({
            'show_id': str(show.id),
            'title': ctx.title if ctx else '',
            'status': 'completed',
            'ticket_revenue': str(ticket_revenue),
            'artist_costs_paid': str(paid_costs),
            'net_position': str(ticket_revenue - paid_costs),
            'message': 'Show closed out successfully.',
        })

    @action(detail=True, methods=['get'])
    def financials(self, request, pk=None):
        """Per-show P&L: budget approved, ticket revenue, artist costs."""
        from apps.ticketing.models import Booking, Ticket
        from apps.artists.models import ArtistPayment, PaymentStatus
        show = self.get_object()
        performances = Performance.objects.filter(
            show=show, organisation=request.user.organisation
        )
        bookings = Booking.objects.filter(performance__in=performances)
        ticket_revenue = Ticket.objects.filter(
            booking__in=bookings
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        artist_payments_paid = ArtistPayment.objects.filter(
            engagement__operating_context_id=show.operating_context_id,
            status=PaymentStatus.PAID,
            organisation=request.user.organisation,
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return Response({
            'show_id': str(show.id),
            'show_title': show.operating_context.title if show.operating_context else show.title,
            'budget_approved': str(show.budget_approved or 0),
            'revenue_target': str(show.revenue_target or 0),
            'ticket_revenue': str(ticket_revenue),
            'artist_costs_paid': str(artist_payments_paid),
            'net_position': str(ticket_revenue - artist_payments_paid),
        })


class PerformanceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Performance.objects.select_related('show', 'venue', 'space')
    serializer_class = PerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['show', 'venue', 'space', 'performance_date', 'is_cancelled']
    ordering_fields = ['performance_date', 'start_time']
    ordering = ['performance_date', 'start_time']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)


# ── Production Licences ───────────────────────────────────────────────────────

class ProductionLicenceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ProductionLicence.objects.select_related('operating_context')
    serializer_class = ProductionLicenceSerializer
    filterset_fields = ['operating_context', 'licensing_body', 'status']
    search_fields = ['licence_number', 'certificate_reference', 'notes']
    ordering = ['operating_context', 'licensing_body']

    def get_queryset(self):
        qs = super().get_queryset()
        operating_context = self.request.query_params.get('operating_context')
        if operating_context:
            qs = qs.filter(operating_context_id=operating_context)
        return qs

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Production Journal ────────────────────────────────────────────────────────

from .models import ProductionJournalEntry  # noqa: E402
from .serializers import ProductionJournalEntrySerializer  # noqa: E402


class ProductionJournalEntryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ProductionJournalEntry.objects.select_related('operating_context', 'author')
    serializer_class = ProductionJournalEntrySerializer
    filterset_fields = ['operating_context', 'entry_type', 'is_confidential', 'requires_follow_up', 'follow_up_completed']
    search_fields = ['title', 'body']
    ordering_fields = ['entry_date', 'created_at', 'entry_type']
    ordering = ['-entry_date', '-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        operating_context = self.request.query_params.get('operating_context')
        if operating_context:
            qs = qs.filter(operating_context_id=operating_context)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            author=self.request.user,
        )
