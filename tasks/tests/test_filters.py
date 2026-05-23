"""Unit tests for TaskFilter.

The queryset is a MagicMock — assertions verify the right ORM calls are made
without ever touching the database.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from tasks.filters import TaskFilter


FIXED_TODAY = date(2026, 5, 23)


@pytest.fixture
def task_filter():
    return TaskFilter()


@pytest.fixture
def qs():
    mock_qs = MagicMock(name='QuerySet')
    mock_qs.filter.return_value = mock_qs
    mock_qs.exclude.return_value = mock_qs
    return mock_qs


@patch('tasks.filters.timezone')
class TestFilterStatus:
    def test_done(self, mock_tz, task_filter, qs):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_status(qs, 'status', 'done')
        qs.filter.assert_called_once_with(is_done=True)
        assert result is qs

    def test_pending_filters_not_done_and_excludes_overdue(
        self, mock_tz, task_filter, qs
    ):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_status(qs, 'status', 'pending')
        qs.filter.assert_called_once_with(is_done=False)
        qs.exclude.assert_called_once_with(due_date__lt=FIXED_TODAY)
        assert result is qs

    def test_expired(self, mock_tz, task_filter, qs):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_status(qs, 'status', 'expired')
        qs.filter.assert_called_once_with(is_done=False, due_date__lt=FIXED_TODAY)
        assert result is qs

    def test_unknown_value_returns_queryset_unchanged(
        self, mock_tz, task_filter, qs
    ):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_status(qs, 'status', 'bogus')
        qs.filter.assert_not_called()
        qs.exclude.assert_not_called()
        assert result is qs


@patch('tasks.filters.timezone')
class TestFilterPreset:
    def test_today(self, mock_tz, task_filter, qs):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_preset(qs, 'preset', 'today')
        qs.filter.assert_called_once_with(due_date=FIXED_TODAY)
        assert result is qs

    def test_week_filters_by_7_day_range(self, mock_tz, task_filter, qs):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_preset(qs, 'preset', 'week')
        qs.filter.assert_called_once_with(
            due_date__gte=FIXED_TODAY,
            due_date__lte=FIXED_TODAY + timedelta(days=7),
        )
        assert result is qs

    def test_overdue(self, mock_tz, task_filter, qs):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_preset(qs, 'preset', 'overdue')
        qs.filter.assert_called_once_with(is_done=False, due_date__lt=FIXED_TODAY)
        assert result is qs

    def test_unknown_value_returns_queryset_unchanged(
        self, mock_tz, task_filter, qs
    ):
        mock_tz.localdate.return_value = FIXED_TODAY
        result = task_filter.filter_preset(qs, 'preset', 'bogus')
        qs.filter.assert_not_called()
        assert result is qs
