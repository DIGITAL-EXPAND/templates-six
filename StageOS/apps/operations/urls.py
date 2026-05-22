from rest_framework.routers import DefaultRouter
from .views import (
    FOHPlanViewSet, ShowDayChecklistViewSet, IncidentViewSet,
    ShowCallViewSet, PostShowReportViewSet, StaffCallViewSet,
    LiquorLicenceViewSet, SafetyComplianceRecordViewSet,
    UnionAgreementViewSet, UnionCallRateViewSet, CrewCallUnionCheckViewSet,
    MaintenanceTicketViewSet, MaintenanceScheduleViewSet,
    InspectionRecordViewSet, VenueDowntimeViewSet,
    AudienceComplaintViewSet, AccessibilityRequirementViewSet, LateSeatingPolicyViewSet,
)

router = DefaultRouter()
router.register('foh-plans', FOHPlanViewSet, basename='foh-plan')
router.register('checklists', ShowDayChecklistViewSet, basename='checklist')
router.register('incidents', IncidentViewSet, basename='incident')
router.register('show-calls', ShowCallViewSet, basename='show-call')
router.register('post-show-reports', PostShowReportViewSet, basename='post-show-report')
router.register('staff-calls', StaffCallViewSet, basename='staff-call')
router.register('liquor-licences', LiquorLicenceViewSet, basename='liquor-licence')
router.register('safety-compliance', SafetyComplianceRecordViewSet, basename='safety-compliance')
router.register('union-agreements', UnionAgreementViewSet, basename='union-agreement')
router.register('union-rates', UnionCallRateViewSet, basename='union-rate')
router.register('crew-call-union-checks', CrewCallUnionCheckViewSet, basename='crew-call-union-check')
router.register('maintenance-tickets', MaintenanceTicketViewSet, basename='maintenance-ticket')
router.register('maintenance-schedules', MaintenanceScheduleViewSet, basename='maintenance-schedule')
router.register('inspections', InspectionRecordViewSet, basename='inspection')
router.register('venue-downtime', VenueDowntimeViewSet, basename='venue-downtime')
router.register('complaints', AudienceComplaintViewSet, basename='complaint')
router.register('accessibility', AccessibilityRequirementViewSet, basename='accessibility')
router.register('late-seating', LateSeatingPolicyViewSet, basename='late-seating')
urlpatterns = router.urls
