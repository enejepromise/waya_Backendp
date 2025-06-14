from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_settings")
    chore_completion = models.BooleanField(default=True)
    reward_redemption = models.BooleanField(default=True)
    chore_reminder = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)

    def __str__(self):
        return f"NotificationSettings for {self.user.username}"


class RewardSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reward_settings")
    reward_approval_required = models.BooleanField(default=False)
    max_daily_reward = models.PositiveIntegerField(default=0)
    allow_savings = models.BooleanField(default=True)

    def __str__(self):
        return f"RewardSettings for {self.user.username}"
