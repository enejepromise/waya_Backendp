from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationView,
    ForgotPasswordView,
    ResetPasswordConfirmView,
    GoogleLoginView,
    home,
    ResendVerificationEmailView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('email-verify/', EmailVerificationView.as_view(), name='verify-email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('', home, name='home'),
    path('social-login/google/', GoogleLoginView.as_view(), name='google-login'), 
    path('resend-email/', ResendVerificationEmailView.as_view(), name='resend-verification-email'),
]
