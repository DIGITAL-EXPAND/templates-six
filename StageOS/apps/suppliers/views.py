from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from common.permissions import (
    CanAccessSupplierData, CanAccessFinance, IsTenantMember, UserRoles, user_type,
)
from .models import Supplier, SupplierDocument, SupplierEngagement, PaymentPack
from .serializers import (
    SupplierSerializer, SupplierDocumentSerializer,
    SupplierEngagementSerializer, PaymentPackSerializer,
)
from .services import (
    verify_supplier, send_payment_to_erp, upload_supplier_document,
    verify_supplier_document, reject_supplier_document, suspend_supplier,
)


class SupplierViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessSupplierData]
    filterset_fields = ['status', 'bee_level', 'category', 'panel']
    search_fields = ['name', 'contact_name']
    ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.SUPPLIER_EXTERNAL:
            return qs.filter(contact_email=self.request.user.email)
        return qs

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        supplier = self.get_object()
        updated = verify_supplier(supplier, request.user)
        return Response(SupplierSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        updated = suspend_supplier(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(SupplierSerializer(updated, context={'request': request}).data)


class SupplierDocumentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SupplierDocument.objects.select_related('supplier', 'document', 'verified_by')
    serializer_class = SupplierDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessSupplierData]
    filterset_fields = ['supplier', 'document_type', 'status']
    ordering = ['document_type']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.SUPPLIER_EXTERNAL:
            return qs.filter(supplier__contact_email=self.request.user.email)
        return qs

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        updated = verify_supplier_document(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(SupplierDocumentSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        updated = reject_supplier_document(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(SupplierDocumentSerializer(updated, context={'request': request}).data)


class SupplierEngagementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SupplierEngagement.objects.select_related('supplier', 'operating_context')
    serializer_class = SupplierEngagementSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessSupplierData]
    filterset_fields = ['supplier', 'operating_context', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.SUPPLIER_EXTERNAL:
            return qs.filter(supplier__contact_email=self.request.user.email)
        return qs


class PaymentPackViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PaymentPack.objects.select_related('supplier_engagement', 'operating_context')
    serializer_class = PaymentPackSerializer
    permission_classes = TenantScopedMixin.permission_classes + [CanAccessFinance]
    filterset_fields = ['operating_context', 'status', 'supplier_engagement']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='send-to-erp')
    def send_to_erp(self, request, pk=None):
        pack = self.get_object()
        updated = send_payment_to_erp(pack, request.user)
        return Response(PaymentPackSerializer(updated, context={'request': request}).data)
