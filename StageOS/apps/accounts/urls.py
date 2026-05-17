from django.urls import path
from .views import MeView, MyDashboardView, MyNavigationView, MyOperatingProfileView, MyPermissionsView, UserListCreateView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('me/operating-profile/', MyOperatingProfileView.as_view(), name='me-operating-profile'),
    path('me/permissions/', MyPermissionsView.as_view(), name='me-permissions'),
    path('me/dashboard/', MyDashboardView.as_view(), name='me-dashboard'),
    path('me/navigation/', MyNavigationView.as_view(), name='me-navigation'),
    path('users/', UserListCreateView.as_view(), name='user-list'),
]
