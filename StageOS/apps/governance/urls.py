from rest_framework.routers import DefaultRouter
from .views import (
    ExecutiveActionViewSet, KPIViewSet, KPIEvidenceViewSet,
    RiskViewSet, CorrectiveActionViewSet,
    BudgetViewSet, BudgetLineViewSet,
    BoardMeetingViewSet, BoardResolutionViewSet,
    DelegationMatrixViewSet, DelegationRuleViewSet,
    ShareholderCompactViewSet, CompactTargetViewSet, CompactActualViewSet, FundingTrancheViewSet,
    IUFWIncidentViewSet, IUFWInvestigationViewSet, IUFWRecoveryViewSet,
    IUFWDisciplinaryReferralViewSet, IUFWCondonementViewSet,
    AGAuditRequestViewSet, AGAuditEvidenceViewSet,
    ConflictOfInterestViewSet, PerformanceReportViewSet,
    BoardMemberProfileViewSet,
    Section32ReportViewSet, AnnualReportViewSet,
    ExpiryAlertViewSet,
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
router.register('delegation-matrices', DelegationMatrixViewSet, basename='delegation-matrix')
router.register('delegation-rules', DelegationRuleViewSet, basename='delegation-rule')
router.register('shareholder-compacts', ShareholderCompactViewSet, basename='shareholder-compact')
router.register('compact-targets', CompactTargetViewSet, basename='compact-target')
router.register('compact-actuals', CompactActualViewSet, basename='compact-actual')
router.register('funding-tranches', FundingTrancheViewSet, basename='funding-tranche')
router.register('iufw-incidents', IUFWIncidentViewSet, basename='iufw-incident')
router.register('iufw-investigations', IUFWInvestigationViewSet, basename='iufw-investigation')
router.register('iufw-recoveries', IUFWRecoveryViewSet, basename='iufw-recovery')
router.register('ag-audit-requests', AGAuditRequestViewSet, basename='ag-audit-request')
router.register('ag-audit-evidence', AGAuditEvidenceViewSet, basename='ag-audit-evidence')
router.register('conflict-of-interest', ConflictOfInterestViewSet, basename='conflict-of-interest')
router.register('performance-reports', PerformanceReportViewSet, basename='performance-report')
router.register('board-members', BoardMemberProfileViewSet, basename='board-member')
router.register('section32', Section32ReportViewSet, basename='section32')
router.register('annual-reports', AnnualReportViewSet, basename='annual-report')
router.register('iufw-disciplinary', IUFWDisciplinaryReferralViewSet, basename='iufw-disciplinary')
router.register('iufw-condonements', IUFWCondonementViewSet, basename='iufw-condonement')
router.register('expiry-alerts', ExpiryAlertViewSet, basename='expiry-alert')

urlpatterns = router.urls
