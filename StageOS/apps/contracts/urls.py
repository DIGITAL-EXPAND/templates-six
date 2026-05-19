from rest_framework.routers import DefaultRouter
from .views import ContractTemplateViewSet, ContractRecordViewSet, SignatureRecordViewSet, ContractObligationViewSet

router = DefaultRouter()
router.register('templates', ContractTemplateViewSet, basename='contract-template')
router.register('records', ContractRecordViewSet, basename='contract-record')
router.register('signatures', SignatureRecordViewSet, basename='signature-record')
router.register('obligations', ContractObligationViewSet, basename='contract-obligation')
urlpatterns = router.urls
