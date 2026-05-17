from rest_framework.routers import DefaultRouter
from .views import TicketingSetupViewSet, SalesImportViewSet

router = DefaultRouter()
router.register('setups', TicketingSetupViewSet, basename='ticketing-setup')
router.register('sales-imports', SalesImportViewSet, basename='sales-import')

urlpatterns = router.urls
