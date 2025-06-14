from datetime import datetime
from collections import defaultdict
from django.utils.dateparse import parse_datetime
from taskmaster.models import Task
from children.models import Child


class ChoreStatistics:

    @staticmethod
    def get_dashboard_stats(parent, from_date=None, to_date=None, child_id=None):
        chores = Task.objects.filter(created_by=parent)

        if from_date:
            chores = chores.filter(created_at__gte=from_date)
        if to_date:
            chores = chores.filter(created_at__lte=to_date)
        if child_id:
            chores = chores.filter(assigned_to_id=child_id)

        total = chores.count()
        completed = chores.filter(status='completed').count()
        pending = chores.filter(status='pending').count()

        activities = []
        individual_activities = defaultdict(list)
        daily_summary = defaultdict(lambda: {'total': 0, 'completed': 0, 'pending': 0})

        for chore in chores.order_by('-created_at'):
            day = chore.created_at.date().isoformat()

            activity = {
                'id': chore.id,
                'activity_type': f"chore_{chore.status}",
                'description': chore.title,
                'child_name': chore.assigned_to.name if chore.assigned_to else None,
                'points': chore.points,
                'timestamp': chore.created_at
            }
            activities.append(activity)

            if chore.assigned_to:
                individual_activities[chore.assigned_to.name].append(activity)

            # For chart summary
            daily_summary[day]['total'] += 1
            daily_summary[day][chore.status] += 1

        return {
            'total_chores': total,
            'completed_chores': completed,
            'pending_chores': pending,
            'activities': activities,
            'individual_activities': individual_activities,
            'daily_summary': daily_summary
        }
