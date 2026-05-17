from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import ArtistViewSet, ArtistDocumentViewSet, ArtistEngagementViewSet

# Sub-resource routes must come BEFORE the empty-prefix Artist routes
# so that /documents/ and /engagements/ are matched before the {pk} wildcard.
sub_router = SimpleRouter()
sub_router.register('documents', ArtistDocumentViewSet, basename='artist-document')
sub_router.register('engagements', ArtistEngagementViewSet, basename='artist-engagement')

main_router = DefaultRouter()
main_router.register('', ArtistViewSet, basename='artist')

urlpatterns = sub_router.urls + main_router.urls
