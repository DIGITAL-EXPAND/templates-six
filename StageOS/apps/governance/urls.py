from rest_framework.routers import DefaultRouter
from .views import (
    ExecutiveActionViewSet, KPIViewSet, KPIEvidenceViewSet,
    RiskViewSet, CorrectiveActionViewSet,
)

router = DefaultRouter()
router.register('kpis', KPIViewSet, basename='kpi')
router.register('kpi-evidence', KPIEvidenceViewSet, basename='kpi-evidence')
router.register('risks', RiskViewSet, basename='risk')
router.register('corrective-actions', CorrectiveActionViewSet, basename='corrective-action')
router.register('executive-actions', ExecutiveActionViewSet, basename='executive-action')

urlpatterns = router.urls
