from rest_framework import serializers


class ActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    activity_type = serializers.CharField()
    description = serializers.CharField()
    child_name = serializers.CharField(allow_null=True)
    points = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class DashboardStatsSerializer(serializers.Serializer):
    total_chores = serializers.IntegerField()
    completed_chores = serializers.IntegerField()
    pending_chores = serializers.IntegerField()
    activities = ActivitySerializer(many=True)
    individual_activities = serializers.DictField(
        child=ActivitySerializer(many=True)
    )
    daily_summary = serializers.DictField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
