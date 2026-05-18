from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HospitalityNoteViewSet, HospitalityRequestViewSet

router = DefaultRouter()
router.register('requests', HospitalityRequestViewSet, basename='hospitality-request')
router.register('notes', HospitalityNoteViewSet, basename='hospitality-note')

urlpatterns = [
    path('', include(router.urls)),
]
