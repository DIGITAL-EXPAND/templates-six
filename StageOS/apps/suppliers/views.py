from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from common.views import TenantScopedMixin
from common.permissions import (
    CanAccessSupplierData, CanAccessFinance, IsTenantMember, UserRoles, user_type,
)
from .models import Supplier, SupplierDocument, SupplierEngagement, PaymentPack, PurchaseRequisition, PurchaseOrder
from .serializers import (
    SupplierSerializer, SupplierDocumentSerializer,
    SupplierEngagementSerializer, PaymentPackSerializer,
    PurchaseRequisitionSerializer, PurchaseOrderSerializer,
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


class PurchaseRequisitionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PurchaseRequisition.objects.select_related(
        'operating_context', 'department', 'requested_by', 'approved_by',
    )
    serializer_class = PurchaseRequisitionSerializer
    filterset_fields = ['status', 'operating_context', 'department', 'requested_by', 'currency']
    search_fields = ['title', 'description', 'requisition_number']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        requisition = self.get_object()
        requisition.status = 'approved'
        requisition.approved_by = request.user
        requisition.approved_at = timezone.now()
        requisition.save(update_fields=['status', 'approved_by', 'approved_at'])
        return Response(PurchaseRequisitionSerializer(requisition, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        requisition = self.get_object()
        reason = request.data.get('reason', '')
        if not reason.strip():
            return Response(
                {'reason': 'A rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        requisition.status = 'rejected'
        requisition.rejection_reason = reason
        requisition.save(update_fields=['status', 'rejection_reason'])
        return Response(PurchaseRequisitionSerializer(requisition, context={'request': request}).data)


class PurchaseOrderViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related(
        'requisition', 'supplier', 'operating_context',
    )
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['status', 'supplier', 'operating_context', 'requisition', 'currency']
    search_fields = ['po_number', 'description', 'invoice_number']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
