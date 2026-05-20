from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganisationListView, TenantEntityConfigViewSet

router = DefaultRouter()
router.register('entity-config', TenantEntityConfigViewSet, basename='entity-config')

urlpatterns = [
    path('organisations/', OrganisationListView.as_view(), name='organisation-list'),
    path('', include(router.urls)),
]
