from rest_framework import viewsets, mixins

from common.views import TenantScopedMixin
from .models import IntegrationProvider, ExternalReference
from .serializers import IntegrationProviderSerializer, ExternalReferenceSerializer


class IntegrationProviderViewSet(
    TenantScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = IntegrationProvider.objects.all()
    serializer_class = IntegrationProviderSerializer
    http_method_names = ['get', 'head', 'options']
    filterset_fields = ['provider_type', 'is_enabled']
    ordering = ['name']


class ExternalReferenceViewSet(
    TenantScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExternalReference.objects.select_related('provider', 'operating_context')
    serializer_class = ExternalReferenceSerializer
    http_method_names = ['get', 'head', 'options']
    filterset_fields = ['provider', 'operating_context', 'reference_type']
    ordering = ['provider', 'reference_type']
