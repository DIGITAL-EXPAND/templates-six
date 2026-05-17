from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, TaskCommentViewSet, TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
router.register('comments', TaskCommentViewSet, basename='taskcomment')
router.register('notifications', NotificationViewSet, basename='notification')
urlpatterns = router.urls
