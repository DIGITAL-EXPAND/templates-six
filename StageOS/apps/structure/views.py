from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
import datetime
from .models import (
    ApprovalPolicy,
    Department,
    EvidenceRule,
    ModuleActivation,
    OrganisationOperatingModel,
    Position,
    Site,
    SOPTemplate,
    Space,
    UserDepartmentMembership,
    Venue,
    VenueCapacityConfig,
    VenueRentalEnquiry,
    VenueRentalQuote,
    RentalBooking,
    RentalInvoice,
    ResidentCompany,
    VenueHoldExpiry,
)
from .serializers import (
    ApprovalPolicySerializer,
    DepartmentSerializer,
    EvidenceRuleSerializer,
    ModuleActivationSerializer,
    OrganisationOperatingModelSerializer,
    PositionSerializer,
    SiteSerializer,
    SOPTemplateSerializer,
    SpaceSerializer,
    UserDepartmentMembershipSerializer,
    VenueCapacityConfigSerializer,
    VenueSerializer,
    VenueRentalEnquirySerializer,
    VenueRentalQuoteSerializer,
    RentalBookingSerializer,
    RentalInvoiceSerializer,
    ResidentCompanySerializer,
    VenueHoldExpirySerializer,
)


class SiteViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class VenueViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Venue.objects.select_related('site')
    serializer_class = VenueSerializer


class SpaceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Space.objects.select_related('venue__site')
    serializer_class = SpaceSerializer


class DepartmentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Department.objects.select_related('site')
    serializer_class = DepartmentSerializer


class PositionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Position.objects.select_related('department', 'site', 'reports_to')
    serializer_class = PositionSerializer


class OrganisationOperatingModelViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = OrganisationOperatingModel.objects.all()
    serializer_class = OrganisationOperatingModelSerializer


class UserDepartmentMembershipViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = UserDepartmentMembership.objects.select_related('user', 'site', 'department', 'position', 'reports_to')
    serializer_class = UserDepartmentMembershipSerializer


class ModuleActivationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ModuleActivation.objects.all()
    serializer_class = ModuleActivationSerializer


class ApprovalPolicyViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ApprovalPolicy.objects.select_related('department')
    serializer_class = ApprovalPolicySerializer


class EvidenceRuleViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = EvidenceRule.objects.select_related('department')
    serializer_class = EvidenceRuleSerializer


class SOPTemplateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SOPTemplate.objects.select_related('operating_model', 'department')
    serializer_class = SOPTemplateSerializer


class VenueCapacityConfigViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueCapacityConfig.objects.select_related('space', 'space__venue')
    serializer_class = VenueCapacityConfigSerializer
    filterset_fields = ['space', 'configuration', 'is_default']
    ordering = ['space', 'configuration']


# ── Venue Rental ──────────────────────────────────────────────────────────────

class VenueRentalEnquiryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueRentalEnquiry.objects.select_related('venue', 'space', 'assigned_to').prefetch_related('quotes')
    serializer_class = VenueRentalEnquirySerializer
    filterset_fields = ['venue', 'space', 'status', 'assigned_to']
    search_fields = ['reference_number', 'client_name', 'client_email', 'event_name', 'event_type']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def quote(self, request, pk=None):
        enquiry = self.get_object()
        data = request.data.copy()
        data['enquiry'] = str(enquiry.id)
        serializer = VenueRentalQuoteSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        quote = serializer.save(organisation_id=request.user.organisation_id)
        enquiry.status = 'quote_sent'
        enquiry.save(update_fields=['status'])
        return Response(VenueRentalQuoteSerializer(quote, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def convert_to_production(self, request, pk=None):
        """Convert a confirmed rental enquiry into an OperatingContext (production)."""
        from apps.contexts.models import OperatingContext
        enquiry = self.get_object()
        if enquiry.status not in ['quote_accepted', 'agreement_signed', 'deposit_received', 'confirmed']:
            return Response({'error': 'Enquiry must be at quote_accepted or later stage to convert.'}, status=400)
        # Resolve required FK fields from the enquiry venue
        site = enquiry.venue.site if enquiry.venue else None
        owner = request.user
        ctx = OperatingContext.objects.create(
            organisation=enquiry.organisation,
            title=enquiry.event_name,
            context_type='venue_rental',
            start_date=enquiry.event_date,
            end_date=enquiry.event_end_date or enquiry.event_date,
            status='confirmed',
            synopsis=f'Created from rental enquiry {enquiry.reference_number}',
            site=site,
            owner=owner,
        )
        enquiry.status = 'confirmed'
        enquiry.save()
        return Response({'production_id': str(ctx.id), 'title': ctx.title, 'message': 'Production created successfully.'})


class VenueRentalQuoteViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueRentalQuote.objects.select_related('enquiry')
    serializer_class = VenueRentalQuoteSerializer
    filterset_fields = ['enquiry', 'is_accepted']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Rental Booking & Invoice ──────────────────────────────────────────────────

class RentalBookingViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = RentalBooking.objects.select_related('enquiry', 'quote').prefetch_related('invoices')
    serializer_class = RentalBookingSerializer
    filterset_fields = ['enquiry', 'status', 'contract_signed']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark booking as completed."""
        booking = self.get_object()
        booking.status = 'completed'
        booking.save(update_fields=['status', 'updated_at'])
        return Response(RentalBookingSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def invoice(self, request, pk=None):
        """Create a RentalInvoice for this booking."""
        booking = self.get_object()
        data = request.data.copy()
        data['booking'] = str(booking.id)
        serializer = RentalInvoiceSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        inv = serializer.save(organisation_id=request.user.organisation_id)
        return Response(RentalInvoiceSerializer(inv, context={'request': request}).data, status=status.HTTP_201_CREATED)


class RentalInvoiceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = RentalInvoice.objects.select_related('booking')
    serializer_class = RentalInvoiceSerializer
    filterset_fields = ['booking', 'invoice_type', 'is_paid']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid."""
        invoice = self.get_object()
        invoice.is_paid = True
        invoice.paid_date = datetime.date.today()
        paid_amount = request.data.get('paid_amount', invoice.total)
        invoice.paid_amount = paid_amount
        invoice.save(update_fields=['is_paid', 'paid_date', 'paid_amount'])
        return Response(RentalInvoiceSerializer(invoice, context={'request': request}).data)


# ── Resident Companies ────────────────────────────────────────────────────────

class ResidentCompanyViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ResidentCompany.objects.select_related('venue')
    serializer_class = ResidentCompanySerializer
    filterset_fields = ['venue', 'status', 'company_type']
    search_fields = ['name', 'artistic_director', 'contact_email', 'agreement_reference']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Venue Hold Expiry ─────────────────────────────────────────────────────────

class VenueHoldExpiryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueHoldExpiry.objects.select_related('enquiry')
    serializer_class = VenueHoldExpirySerializer
    filterset_fields = ['enquiry', 'is_expired', 'reminder_sent']
    ordering = ['hold_expiry_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def expire(self, request, pk=None):
        """Mark the hold as expired and cancel the associated enquiry."""
        from django.utils import timezone
        hold_expiry = self.get_object()
        hold_expiry.is_expired = True
        hold_expiry.expired_at = timezone.now()
        hold_expiry.save(update_fields=['is_expired', 'expired_at'])
        enquiry = hold_expiry.enquiry
        enquiry.status = 'cancelled'
        enquiry.save(update_fields=['status'])
        return Response(VenueHoldExpirySerializer(hold_expiry, context={'request': request}).data)
