from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CampaignDeliverableViewSet

router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('deliverables', CampaignDeliverableViewSet, basename='deliverable')
urlpatterns = router.urls
