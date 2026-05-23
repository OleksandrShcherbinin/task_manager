"""Unit tests for the Task model. No DB access — timezone.localdate is mocked."""

from datetime import date
from unittest.mock import patch

from tasks.models import Task


FIXED_TODAY = date(2026, 5, 23)


class TestTaskStr:
    def test_str_returns_title(self):
        task = Task(title='Buy milk')
        assert str(task) == 'Buy milk'


@patch('tasks.models.timezone')
class TestTaskIsExpired:
    def test_no_due_date_is_not_expired(self, mock_tz):
        mock_tz.localdate.return_value = FIXED_TODAY
        task = Task(title='x', due_date=None, is_done=False)
        assert task.is_expired is False

    def test_done_task_is_never_expired(self, mock_tz):
        mock_tz.localdate.return_value = FIXED_TODAY
        task = Task(title='x', due_date=date(2020, 1, 1), is_done=True)
        assert task.is_expired is False

    def test_past_due_pending_is_expired(self, mock_tz):
        mock_tz.localdate.return_value = FIXED_TODAY
        task = Task(title='x', due_date=date(2026, 5, 22), is_done=False)
        assert task.is_expired is True

    def test_due_today_pending_is_not_expired(self, mock_tz):
        mock_tz.localdate.return_value = FIXED_TODAY
        task = Task(title='x', due_date=FIXED_TODAY, is_done=False)
        assert task.is_expired is False

    def test_future_due_pending_is_not_expired(self, mock_tz):
        mock_tz.localdate.return_value = FIXED_TODAY
        task = Task(title='x', due_date=date(2026, 12, 1), is_done=False)
        assert task.is_expired is False
