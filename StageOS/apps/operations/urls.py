from rest_framework.routers import DefaultRouter
from .views import (
    FOHPlanViewSet, ShowDayChecklistViewSet, IncidentViewSet,
    ShowCallViewSet, PostShowReportViewSet, StaffCallViewSet,
    LiquorLicenceViewSet, SafetyComplianceRecordViewSet,
    UnionAgreementViewSet, UnionCallRateViewSet, CrewCallUnionCheckViewSet,
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
urlpatterns = router.urls
