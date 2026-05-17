from rest_framework.routers import DefaultRouter
from .views import IntegrationProviderViewSet, ExternalReferenceViewSet

router = DefaultRouter()
router.register('providers', IntegrationProviderViewSet, basename='integration-provider')
router.register('references', ExternalReferenceViewSet, basename='external-reference')

urlpatterns = router.urls
