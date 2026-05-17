from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from apps.documents.models import Document
from .models import TicketingSetup, SalesImport
from .serializers import (
    TicketingSetupSerializer, SalesImportSerializer,
    ImportSalesSerializer, SettleSerializer,
)
from .services import create_ticketing_setup, go_live, import_sales, settle_ticketing


class TicketingSetupViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = TicketingSetup.objects.select_related('operating_context')
    serializer_class = TicketingSetupSerializer
    filterset_fields = ['operating_context', 'provider', 'setup_status', 'settlement_status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        setup = create_ticketing_setup(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = setup

    @action(detail=True, methods=['post'], url_path='go-live')
    def go_live(self, request, pk=None):
        setup = self.get_object()
        updated = go_live(setup, request.user)
        return Response(TicketingSetupSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='import-sales')
    def import_sales(self, request, pk=None):
        setup = self.get_object()
        input_ser = ImportSalesSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)

        data = dict(input_ser.validated_data)
        source_file_id = data.pop('source_file', None)
        if source_file_id:
            try:
                data['source_file'] = Document.objects.get(
                    id=source_file_id, organisation=request.user.organisation,
                )
            except Document.DoesNotExist:
                return Response(
                    {'source_file': 'Document not found in your organisation.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data['source_file'] = None

        sale = import_sales(setup, request.user, data)
        return Response(SalesImportSerializer(sale, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        setup = self.get_object()
        input_ser = SettleSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        updated = settle_ticketing(setup, request.user, input_ser.validated_data['amount'])
        return Response(TicketingSetupSerializer(updated, context={'request': request}).data)


class SalesImportViewSet(TenantScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SalesImport.objects.select_related('ticketing_setup', 'imported_by', 'source_file')
    serializer_class = SalesImportSerializer
    http_method_names = ['get', 'head', 'options']
    filterset_fields = ['ticketing_setup']
    ordering = ['-import_date']
