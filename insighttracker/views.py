from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_datetime, parse_date

from insighttracker.utils.statistics import ChoreStatistics
from insighttracker.serializers import DashboardStatsSerializer


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        child_id = request.query_params.get('child_id')

        # Convert to Python dates
        from_date = parse_date(from_date) if from_date else None
        to_date = parse_date(to_date) if to_date else None

        stats = ChoreStatistics.get_dashboard_stats(
            parent=request.user,
            from_date=from_date,
            to_date=to_date,
            child_id=child_id
        )

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
