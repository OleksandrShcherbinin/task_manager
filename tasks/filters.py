from datetime import timedelta

import django_filters
from django.utils import timezone

from .models import Task


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('expired', 'Expired'),
]

PRESET_CHOICES = [
    ('today', 'Today'),
    ('week', 'This Week'),
    ('overdue', 'Overdue'),
]


class TaskFilter(django_filters.FilterSet):
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    status = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES, method='filter_status'
    )
    due_from = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_to = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    preset = django_filters.ChoiceFilter(
        choices=PRESET_CHOICES, method='filter_preset'
    )

    class Meta:
        model = Task
        fields = ['priority', 'status', 'due_from', 'due_to', 'preset']

    def filter_status(self, qs, name, value):
        today = timezone.localdate()
        if value == 'done':
            return qs.filter(is_done=True)
        if value == 'pending':
            return qs.filter(is_done=False).exclude(due_date__lt=today)
        if value == 'expired':
            return qs.filter(is_done=False, due_date__lt=today)
        return qs

    def filter_preset(self, qs, name, value):
        today = timezone.localdate()
        if value == 'today':
            return qs.filter(due_date=today)
        if value == 'week':
            return qs.filter(
                due_date__gte=today, due_date__lte=today + timedelta(days=7)
            )
        if value == 'overdue':
            return qs.filter(is_done=False, due_date__lt=today)
        return qs
