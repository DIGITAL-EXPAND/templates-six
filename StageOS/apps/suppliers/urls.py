from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import SupplierViewSet, SupplierDocumentViewSet, SupplierEngagementViewSet, PaymentPackViewSet

# Sub-resource routes must come BEFORE the empty-prefix Supplier routes
# so that /documents/, /engagements/, /payment-packs/ are matched before
# the {pk} wildcard from the main router.
sub_router = SimpleRouter()
sub_router.register('documents', SupplierDocumentViewSet, basename='supplier-document')
sub_router.register('engagements', SupplierEngagementViewSet, basename='supplier-engagement')
sub_router.register('payment-packs', PaymentPackViewSet, basename='payment-pack')

main_router = DefaultRouter()
main_router.register('', SupplierViewSet, basename='supplier')

urlpatterns = sub_router.urls + main_router.urls
