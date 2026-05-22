from rest_framework.routers import DefaultRouter
from .views import (
    FestivalViewSet,
    FestivalVenueViewSet,
    FestivalPassViewSet,
    FestivalVenueSlotViewSet,
)

router = DefaultRouter()
router.register('festivals', FestivalViewSet, basename='festival')
router.register('festival-venues', FestivalVenueViewSet, basename='festival-venue')
router.register('festival-passes', FestivalPassViewSet, basename='festival-pass')
router.register('festival-venue-slots', FestivalVenueSlotViewSet, basename='festival-venue-slot')

urlpatterns = router.urls
