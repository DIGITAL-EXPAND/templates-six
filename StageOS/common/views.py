from rest_framework import permissions, status
from rest_framework.response import Response

from common.permissions import IsTenantMember, IsInternalMutableUser


class TenantScopedMixin:
    """Mixin for ViewSets that automatically scopes querysets and creates to the
    requesting user's organisation.

    Apply as the first base class: class MyViewSet(TenantScopedMixin, ModelViewSet).
    """
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, IsInternalMutableUser]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.organisation_id:
            return qs.none()
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    def destroy(self, request, *args, **kwargs):
        self.get_object()  # enforces tenant isolation — raises 404 if not found/not owned
        return Response(
            {'detail': 'Hard deletion is not permitted. Archive or cancel this record instead.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
