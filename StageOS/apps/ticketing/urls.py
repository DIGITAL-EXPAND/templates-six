from rest_framework.routers import DefaultRouter
from .views import (
    TicketingSetupViewSet, SalesImportViewSet,
    PriceCategoryViewSet, BookingViewSet, TicketViewSet, TillReconciliationViewSet,
)

router = DefaultRouter()
router.register('setups', TicketingSetupViewSet, basename='ticketing-setup')
router.register('sales-imports', SalesImportViewSet, basename='sales-import')
router.register('price-categories', PriceCategoryViewSet, basename='price-category')
router.register('bookings', BookingViewSet, basename='booking')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('till-reconciliations', TillReconciliationViewSet, basename='till-reconciliation')

urlpatterns = router.urls
