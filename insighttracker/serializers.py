# from rest_framework import serializers
# from .models import InsightTracker

# class InsightTrackerSerializer(serializers.ModelSerializer):
#     child_username = serializers.CharField(source='child.username', read_only=True)

#     class Meta:
#         model = InsightTracker
#         fields = ['id', 'child', 'child_username', 'activity_type', 'description', 'value', 'created_at']
#         read_only_fields = ['id', 'created_at']
