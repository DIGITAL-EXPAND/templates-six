from rest_framework.routers import DefaultRouter
from .views import (
    ApprovalPolicyViewSet,
    DepartmentViewSet,
    EvidenceRuleViewSet,
    ModuleActivationViewSet,
    OrganisationOperatingModelViewSet,
    PositionViewSet,
    SOPTemplateViewSet,
    SiteViewSet,
    SpaceViewSet,
    UserDepartmentMembershipViewSet,
    VenueCapacityConfigViewSet,
    VenueViewSet,
    VenueRentalEnquiryViewSet,
    VenueRentalQuoteViewSet,
    RentalBookingViewSet,
    RentalInvoiceViewSet,
    ResidentCompanyViewSet,
    VenueHoldExpiryViewSet,
)

router = DefaultRouter()
router.register('sites', SiteViewSet, basename='site')
router.register('venues', VenueViewSet, basename='venue')
router.register('spaces', SpaceViewSet, basename='space')
router.register('departments', DepartmentViewSet, basename='department')
router.register('positions', PositionViewSet, basename='position')
router.register('operating-models', OrganisationOperatingModelViewSet, basename='operating-model')
router.register('user-department-memberships', UserDepartmentMembershipViewSet, basename='user-department-membership')
router.register('module-activations', ModuleActivationViewSet, basename='module-activation')
router.register('approval-policies', ApprovalPolicyViewSet, basename='approval-policy')
router.register('evidence-rules', EvidenceRuleViewSet, basename='evidence-rule')
router.register('sop-templates', SOPTemplateViewSet, basename='sop-template')
router.register('venue-capacity-configs', VenueCapacityConfigViewSet, basename='venue-capacity-config')
router.register('rental-enquiries', VenueRentalEnquiryViewSet, basename='rental-enquiry')
router.register('rental-quotes', VenueRentalQuoteViewSet, basename='rental-quote')
router.register('rental-bookings', RentalBookingViewSet, basename='rental-booking')
router.register('rental-invoices', RentalInvoiceViewSet, basename='rental-invoice')
router.register('resident-companies', ResidentCompanyViewSet, basename='resident-company')
router.register('venue-hold-expiries', VenueHoldExpiryViewSet, basename='venue-hold-expiry')

urlpatterns = router.urls
