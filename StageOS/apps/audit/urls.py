from django.urls import path
from .views import AuditEventListView, AuditVerifyView

urlpatterns = [
    path('audit/', AuditEventListView.as_view(), name='audit-list'),
    path('audit/verify/', AuditVerifyView.as_view(), name='audit-verify'),
]
