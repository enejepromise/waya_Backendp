from django.urls import path
from .views import (
    UserProfileView,
    ChildView,
    PasswordResetView,
    NotificationSettingsView,
    RewardSettingsView
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('children/<int:child_id>/profile/', ChildView.as_view(), name='child-profile'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('notifications/', NotificationSettingsView.as_view(), name='notification-settings'),
    path('rewards/', RewardSettingsView.as_view(), name='reward-settings'),
]
