from django.urls import path
from .views import OrganisationListView

urlpatterns = [
    path('organisations/', OrganisationListView.as_view(), name='organisation-list'),
]
