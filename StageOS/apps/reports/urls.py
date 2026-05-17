from django.urls import path
from .views import (
    ExecutiveSummaryView, ContextReadinessView, ContextAuditTrailView,
    DepartmentReadinessView, YouthSummaryView, AuditExportView,
    RiskRegisterView, ContractStatusReportView, SupplierReadinessReportView,
    EvidenceGapsReportView, CalendarIssuesReportView, BoardSummaryView,
)

urlpatterns = [
    path('executive-summary/', ExecutiveSummaryView.as_view(), name='executive-summary'),
    path('context-readiness/<uuid:context_id>/', ContextReadinessView.as_view(), name='context-readiness'),
    path('context-audit/<uuid:context_id>/', ContextAuditTrailView.as_view(), name='context-audit'),
    path('department-readiness/<uuid:department_id>/', DepartmentReadinessView.as_view(), name='department-readiness'),
    path('youth-summary/<uuid:project_id>/', YouthSummaryView.as_view(), name='youth-summary'),
    path('risk-register/', RiskRegisterView.as_view(), name='risk-register'),
    path('contract-status/', ContractStatusReportView.as_view(), name='contract-status-report'),
    path('supplier-readiness/', SupplierReadinessReportView.as_view(), name='supplier-readiness-report'),
    path('evidence-gaps/', EvidenceGapsReportView.as_view(), name='evidence-gaps-report'),
    path('calendar-issues/', CalendarIssuesReportView.as_view(), name='calendar-issues-report'),
    path('board-summary/', BoardSummaryView.as_view(), name='board-summary'),
    path('audit-export/', AuditExportView.as_view(), name='audit-export'),
]
