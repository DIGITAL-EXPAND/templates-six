from rest_framework.routers import DefaultRouter
from .views import ApprovalRouteViewSet, ApprovalStepViewSet, ApprovalRequestViewSet

router = DefaultRouter()
router.register('approvals/routes', ApprovalRouteViewSet, basename='approval-route')
router.register('approvals/steps', ApprovalStepViewSet, basename='approval-step')
router.register('approvals/requests', ApprovalRequestViewSet, basename='approval-request')

urlpatterns = router.urls
