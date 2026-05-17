from rest_framework.routers import DefaultRouter
from .views import ContractTemplateViewSet, ContractRecordViewSet, SignatureRecordViewSet

router = DefaultRouter()
router.register('templates', ContractTemplateViewSet, basename='contract-template')
router.register('records', ContractRecordViewSet, basename='contract-record')
router.register('signatures', SignatureRecordViewSet, basename='signature-record')
urlpatterns = router.urls
