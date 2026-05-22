from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, CampaignDeliverableViewSet, SocialPostViewSet, AudienceReportViewSet,
    MediaContactViewSet, NewsletterCampaignViewSet, CIComplianceCheckViewSet,
)

router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('deliverables', CampaignDeliverableViewSet, basename='deliverable')
router.register('social-posts', SocialPostViewSet, basename='social-post')
router.register('audience-reports', AudienceReportViewSet, basename='audience-report')
router.register('media-contacts', MediaContactViewSet, basename='media-contact')
router.register('newsletters', NewsletterCampaignViewSet, basename='newsletter')
router.register('ci-compliance', CIComplianceCheckViewSet, basename='ci-compliance')
urlpatterns = router.urls
