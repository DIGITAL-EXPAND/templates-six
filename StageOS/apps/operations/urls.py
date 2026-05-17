from rest_framework.routers import DefaultRouter
from .views import FOHPlanViewSet, ShowDayChecklistViewSet, IncidentViewSet

router = DefaultRouter()
router.register('foh-plans', FOHPlanViewSet, basename='foh-plan')
router.register('checklists', ShowDayChecklistViewSet, basename='checklist')
router.register('incidents', IncidentViewSet, basename='incident')
urlpatterns = router.urls
