from django.urls import path
from .views import AuditEventListView, AuditVerifyView, NotificationListView, NotificationMarkReadView

urlpatterns = [
    path('audit/', AuditEventListView.as_view(), name='audit-list'),
    path('audit/verify/', AuditVerifyView.as_view(), name='audit-verify'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]
