from django.contrib import admin
from .models import NotificationSettings, RewardSettings
from users.models import User
from children.models import Child

# Register models from settings_waya
@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'chore_completion', 'reward_redemption', 'chore_reminder', 'weekly_summary')

@admin.register(RewardSettings)
class RewardSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_approval_required', 'max_daily_reward', 'allow_savings')

