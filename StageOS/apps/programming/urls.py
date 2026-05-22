from rest_framework.routers import DefaultRouter
from .views import (
    CalendarIssueViewSet, IntakeRequestViewSet, IntakeReviewViewSet, ProducerAssignmentViewSet,
    VenueHoldViewSet, CalendarSlotViewSet, SeasonViewSet, ShowViewSet, PerformanceViewSet,
    ProductionLicenceViewSet, ProductionJournalEntryViewSet,
    SetlistWorkViewSet, CoProducerViewSet, CoProductionSettlementViewSet,
    CoProductionSettlementLineViewSet,
    TouringProductionViewSet, TouringVenueDateViewSet, RecurringProductionViewSet,
)

router = DefaultRouter()
router.register('intake-requests', IntakeRequestViewSet, basename='intake-request')
router.register('intake-reviews', IntakeReviewViewSet, basename='intake-review')
router.register('producer-assignments', ProducerAssignmentViewSet, basename='producer-assignment')
router.register('venue-holds', VenueHoldViewSet, basename='venue-hold')
router.register('calendar-slots', CalendarSlotViewSet, basename='calendar-slot')
router.register('calendar-issues', CalendarIssueViewSet, basename='calendar-issue')
router.register('seasons', SeasonViewSet, basename='season')
router.register('shows', ShowViewSet, basename='show')
router.register('performances', PerformanceViewSet, basename='performance')
router.register('production-licences', ProductionLicenceViewSet, basename='production-licence')
router.register('journal', ProductionJournalEntryViewSet, basename='production-journal')
router.register('setlist-works', SetlistWorkViewSet, basename='setlist-work')
router.register('co-producers', CoProducerViewSet, basename='co-producer')
router.register('co-production-settlements', CoProductionSettlementViewSet, basename='co-production-settlement')
router.register('co-production-settlement-lines', CoProductionSettlementLineViewSet, basename='co-production-settlement-line')
router.register('touring-productions', TouringProductionViewSet, basename='touring-production')
router.register('touring-venue-dates', TouringVenueDateViewSet, basename='touring-venue-date')
router.register('recurring-productions', RecurringProductionViewSet, basename='recurring-production')
urlpatterns = router.urls
