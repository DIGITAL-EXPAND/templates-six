from rest_framework.routers import DefaultRouter
from .views import (
    FOHPlanViewSet, ShowDayChecklistViewSet, IncidentViewSet,
    ShowCallViewSet, PostShowReportViewSet, StaffCallViewSet,
)

router = DefaultRouter()
router.register('foh-plans', FOHPlanViewSet, basename='foh-plan')
router.register('checklists', ShowDayChecklistViewSet, basename='checklist')
router.register('incidents', IncidentViewSet, basename='incident')
router.register('show-calls', ShowCallViewSet, basename='show-call')
router.register('post-show-reports', PostShowReportViewSet, basename='post-show-report')
router.register('staff-calls', StaffCallViewSet, basename='staff-call')
urlpatterns = router.urls
