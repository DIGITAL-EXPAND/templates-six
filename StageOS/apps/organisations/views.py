from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from common.views import TenantScopedMixin
from .models import Organisation, TenantEntityConfig
from .serializers import OrganisationSerializer, TenantEntityConfigSerializer


class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.organisation_id:
            return Organisation.objects.none()
        return Organisation.objects.filter(id=self.request.user.organisation_id)


class TenantEntityConfigViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = TenantEntityConfig.objects.all()
    serializer_class = TenantEntityConfigSerializer
    ordering = ['created_at']
