from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
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


class VenueRentalQuoteViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueRentalQuote.objects.select_related('enquiry')
    serializer_class = VenueRentalQuoteSerializer
    filterset_fields = ['enquiry', 'is_accepted']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
