from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcceptInviteView,
    InviteUserView,
    LeaveRequestViewSet,
    MeView,
    MyDashboardView,
    MyNavigationView,
    MyOperatingProfileView,
    MyPermissionsView,
    MyScorecardView,
    POPIAConsentView,
    POPIAErasureRequestView,
    POPIAMyDataView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserListCreateView,
)

router = DefaultRouter()
router.register('leave-requests', LeaveRequestViewSet, basename='leave-request')

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('me/operating-profile/', MyOperatingProfileView.as_view(), name='me-operating-profile'),
    path('me/permissions/', MyPermissionsView.as_view(), name='me-permissions'),
    path('me/dashboard/', MyDashboardView.as_view(), name='me-dashboard'),
    path('me/navigation/', MyNavigationView.as_view(), name='me-navigation'),
    path('me/scorecard/', MyScorecardView.as_view(), name='me-scorecard'),
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
    # HR
    path('', include(router.urls)),
]
