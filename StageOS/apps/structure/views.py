from rest_framework import viewsets
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
    VenueSerializer,
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
