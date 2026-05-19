from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.views import TenantScopedMixin
from common.permissions import CanAccessAudit, is_admin_user
from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventListView(TenantScopedMixin, generics.ListAPIView):
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessAudit]


class AuditVerifyView(TenantScopedMixin, APIView):
    """GET /api/v1/audit/verify/ — verify the hash chain for the current organisation."""
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessAudit]

    def get(self, request):
        if not is_admin_user(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only internal admins may verify the audit chain.')

        events = list(
            AuditEvent.objects.filter(organisation_id=request.user.organisation_id)
            .order_by('created_at')
        )

        expected_previous = ''
        for event in events:
            recomputed = event.compute_hash(expected_previous)
            if recomputed != event.record_hash:
                return Response({'valid': False, 'first_broken_at': str(event.id)})
            expected_previous = event.record_hash

        return Response({'valid': True, 'checked': len(events)})


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from apps.tasks.models import Notification
        return Notification.objects.filter(
            organisation_id=self.request.user.organisation_id,
            recipient=self.request.user,
        )

    def get_serializer_class(self):
        from apps.tasks.models import Notification

        class NotificationSerializer(serializers.ModelSerializer):
            class Meta:
                model = Notification
                fields = ['id', 'message', 'notification_type', 'title', 'related_id', 'read_at', 'created_at']

        return NotificationSerializer


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from apps.tasks.models import Notification
        from django.utils import timezone
        try:
            notif = Notification.objects.get(
                id=pk,
                recipient=request.user,
                organisation_id=request.user.organisation_id,
            )
            notif.read_at = timezone.now()
            notif.save(update_fields=['read_at'])
            return Response({'status': 'marked read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
