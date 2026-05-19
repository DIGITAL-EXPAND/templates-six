from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from apps.documents.models import Document
from .models import TicketingSetup, SalesImport, PriceCategory, Booking, Ticket, TillReconciliation
from .serializers import (
    TicketingSetupSerializer, SalesImportSerializer,
    ImportSalesSerializer, SettleSerializer,
    PriceCategorySerializer, BookingSerializer, TicketSerializer, TillReconciliationSerializer,
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


class PriceCategoryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PriceCategory.objects.select_related('ticketing_setup')
    serializer_class = PriceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['ticketing_setup', 'is_comp']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)


class BookingViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('ticketing_setup', 'performance').prefetch_related('tickets')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['ticketing_setup', 'performance', 'channel', 'is_group_booking']
    search_fields = ['booking_reference', 'patron_name', 'patron_email', 'group_name']
    ordering_fields = ['booked_at', 'patron_name', 'total_amount']
    ordering = ['-booked_at']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)


class TicketViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('booking', 'price_category')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['booking', 'status', 'checked_in', 'price_category']
    ordering_fields = ['seat_reference', 'created_at']
    ordering = ['seat_reference']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)


class TillReconciliationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = TillReconciliation.objects.select_related('ticketing_setup', 'performance', 'signed_off_by')
    serializer_class = TillReconciliationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['ticketing_setup', 'performance', 'recon_date']
    ordering_fields = ['recon_date', 'created_at']
    ordering = ['-recon_date']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation_id=self.request.user.organisation_id)
