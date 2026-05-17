from rest_framework.routers import DefaultRouter
from .views import OperatingContextViewSet

router = DefaultRouter()
router.register('contexts', OperatingContextViewSet, basename='context')

urlpatterns = router.urls
