from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    user = reset_password_token.user
    reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{reset_password_token.key}/"
    subject = "Waya Password Reset Request"
    message = (
        f"Hi {user.full_name},\n\n"
        f"You requested a password reset. Please click the link below to reset your password:\n"
        f"{reset_url}\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "Thank you!"
    )