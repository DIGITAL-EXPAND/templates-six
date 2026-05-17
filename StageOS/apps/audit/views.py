from rest_framework import generics
from common.views import TenantScopedMixin
from common.permissions import CanAccessAudit
from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventListView(TenantScopedMixin, generics.ListAPIView):
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessAudit]
