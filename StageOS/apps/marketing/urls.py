from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CampaignDeliverableViewSet, SocialPostViewSet, AudienceReportViewSet

router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('deliverables', CampaignDeliverableViewSet, basename='deliverable')
router.register('social-posts', SocialPostViewSet, basename='social-post')
router.register('audience-reports', AudienceReportViewSet, basename='audience-report')
urlpatterns = router.urls
