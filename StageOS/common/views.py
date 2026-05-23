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


class ReadOnlyTenantMixin(TenantScopedMixin):
    """For read_only, supplier_external, artist_external, client_external, youth_external users.

    Restricts the viewset to safe HTTP methods only (GET, HEAD, OPTIONS).
    Use this mixin on views that should be readable but not writable by the
    above user types.

    Note on external user scoping:
    - supplier_external: read access is further restricted by CanAccessSupplierData
      which limits them to their own supplier records.
    - artist_external: similarly scoped by CanAccessArtistData.
    - client_external / youth_external: read-only on their own operating context.
      A SupplierScopedMixin (object-level) does not yet exist — this is a documented
      gap to be addressed when supplier self-service views are built.
    """
    http_method_names = ['get', 'head', 'options']
