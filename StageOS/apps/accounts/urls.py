from django.urls import path
from .views import (
    AcceptInviteView,
    InviteUserView,
    MeView,
    MyDashboardView,
    MyNavigationView,
    MyOperatingProfileView,
    MyPermissionsView,
    POPIAConsentView,
    POPIAErasureRequestView,
    POPIAMyDataView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserListCreateView,
)

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('me/operating-profile/', MyOperatingProfileView.as_view(), name='me-operating-profile'),
    path('me/permissions/', MyPermissionsView.as_view(), name='me-permissions'),
    path('me/dashboard/', MyDashboardView.as_view(), name='me-dashboard'),
    path('me/navigation/', MyNavigationView.as_view(), name='me-navigation'),
    path('users/', UserListCreateView.as_view(), name='user-list'),
    # Invite system
    path('invite/', InviteUserView.as_view(), name='invite-user'),
    path('invite/accept/', AcceptInviteView.as_view(), name='accept-invite'),
    # Password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # POPIA
    path('popia/consent/', POPIAConsentView.as_view(), name='popia-consent'),
    path('popia/my-data/', POPIAMyDataView.as_view(), name='popia-my-data'),
    path('popia/erasure-request/', POPIAErasureRequestView.as_view(), name='popia-erasure-request'),
]
