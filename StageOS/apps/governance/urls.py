from rest_framework.routers import DefaultRouter
from .views import (
    ExecutiveActionViewSet, KPIViewSet, KPIEvidenceViewSet,
    RiskViewSet, CorrectiveActionViewSet,
    BudgetViewSet, BudgetLineViewSet,
    BoardMeetingViewSet, BoardResolutionViewSet,
)

router = DefaultRouter()
router.register('kpis', KPIViewSet, basename='kpi')
router.register('kpi-evidence', KPIEvidenceViewSet, basename='kpi-evidence')
router.register('risks', RiskViewSet, basename='risk')
router.register('corrective-actions', CorrectiveActionViewSet, basename='corrective-action')
router.register('executive-actions', ExecutiveActionViewSet, basename='executive-action')
router.register('budgets', BudgetViewSet, basename='budget')
router.register('budget-lines', BudgetLineViewSet, basename='budget-line')
router.register('board-meetings', BoardMeetingViewSet, basename='board-meeting')
router.register('board-resolutions', BoardResolutionViewSet, basename='board-resolution')

urlpatterns = router.urls
