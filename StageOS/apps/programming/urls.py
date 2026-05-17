from rest_framework.routers import DefaultRouter
from .views import (
    CalendarIssueViewSet, IntakeRequestViewSet, IntakeReviewViewSet, ProducerAssignmentViewSet,
    VenueHoldViewSet, CalendarSlotViewSet,
)

router = DefaultRouter()
router.register('intake-requests', IntakeRequestViewSet, basename='intake-request')
router.register('intake-reviews', IntakeReviewViewSet, basename='intake-review')
router.register('producer-assignments', ProducerAssignmentViewSet, basename='producer-assignment')
router.register('venue-holds', VenueHoldViewSet, basename='venue-hold')
router.register('calendar-slots', CalendarSlotViewSet, basename='calendar-slot')
router.register('calendar-issues', CalendarIssueViewSet, basename='calendar-issue')
urlpatterns = router.urls
