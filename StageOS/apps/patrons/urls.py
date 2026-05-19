from rest_framework.routers import DefaultRouter
from .views import PatronViewSet, PatronAttendanceViewSet, PatronCommunicationViewSet

router = DefaultRouter()
router.register('', PatronViewSet, basename='patron')
router.register('attendances', PatronAttendanceViewSet, basename='patron-attendance')
router.register('communications', PatronCommunicationViewSet, basename='patron-communication')

urlpatterns = router.urls
