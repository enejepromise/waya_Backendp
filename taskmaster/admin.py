from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'assigned_to',
        'parent',
        'reward',
        'due_date',
        'status',
        'created_at',
        'completed_at',
    )
    list_filter = ('status', 'due_date', 'created_at')
    search_fields = (
        'title',
        'description',
        'assigned_to__username',
        'parent__email',
        'parent__full_name',
    )
    readonly_fields = ('created_at', 'completed_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'reward',
                'due_date',
                'assigned_to',
                'parent',
                'status',
            )
        }),
        ('Timestamps (Read Only)', {
            'fields': ('created_at', 'completed_at'),
        }),
    )
