from rest_framework.routers import DefaultRouter
from .views import PatronViewSet, PatronAttendanceViewSet, PatronCommunicationViewSet, DonorViewSet, DonationViewSet

router = DefaultRouter()
router.register('', PatronViewSet, basename='patron')
router.register('attendances', PatronAttendanceViewSet, basename='patron-attendance')
router.register('communications', PatronCommunicationViewSet, basename='patron-communication')
router.register('donors', DonorViewSet, basename='donor')
router.register('donations', DonationViewSet, basename='donation')

urlpatterns = router.urls
