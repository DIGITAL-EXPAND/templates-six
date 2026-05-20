from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import (
    SupplierViewSet, SupplierDocumentViewSet, SupplierEngagementViewSet, PaymentPackViewSet,
    PurchaseRequisitionViewSet, PurchaseOrderViewSet, SupplierCSDVerificationViewSet,
)

# Sub-resource routes must come BEFORE the empty-prefix Supplier routes
# so that /documents/, /engagements/, /payment-packs/ are matched before
# the {pk} wildcard from the main router.
sub_router = SimpleRouter()
sub_router.register('documents', SupplierDocumentViewSet, basename='supplier-document')
sub_router.register('engagements', SupplierEngagementViewSet, basename='supplier-engagement')
sub_router.register('payment-packs', PaymentPackViewSet, basename='payment-pack')
sub_router.register('requisitions', PurchaseRequisitionViewSet, basename='purchase-requisition')
sub_router.register('purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
sub_router.register('csd-verifications', SupplierCSDVerificationViewSet, basename='csd-verification')

main_router = DefaultRouter()
main_router.register('', SupplierViewSet, basename='supplier')

urlpatterns = sub_router.urls + main_router.urls
