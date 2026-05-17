from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, EvidenceSubmissionViewSet

router = DefaultRouter()
router.register('documents', DocumentViewSet, basename='document')
router.register('evidence', EvidenceSubmissionViewSet, basename='evidence')
urlpatterns = router.urls
