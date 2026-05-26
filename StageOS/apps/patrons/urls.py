from rest_framework.routers import DefaultRouter
from .views import PatronViewSet, PatronAttendanceViewSet, PatronCommunicationViewSet, DonorViewSet, DonationViewSet

# Specific sub-resources must be registered first so their URL patterns take
# priority over the empty-prefix PatronViewSet's {pk} wildcard pattern.
specific_router = DefaultRouter()
specific_router.register('attendances', PatronAttendanceViewSet, basename='patron-attendance')
specific_router.register('communications', PatronCommunicationViewSet, basename='patron-communication')
specific_router.register('donors', DonorViewSet, basename='donor')
specific_router.register('donations', DonationViewSet, basename='donation')

patron_router = DefaultRouter()
patron_router.register('', PatronViewSet, basename='patron')

urlpatterns = specific_router.urls + patron_router.urls
