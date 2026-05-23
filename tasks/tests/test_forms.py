"""Unit tests for TaskForm.

ModelForm's `_post_clean` triggers `validate_unique` which can hit the database.
We patch it out so validation stays purely in-memory.
"""

from unittest.mock import patch

from tasks.forms import TaskForm


def _bypass_db_validation():
    return patch.object(TaskForm, '_post_clean', lambda self: None)


class TestTaskForm:
    def test_valid_with_minimum_fields(self):
        form = TaskForm(data={'title': 'Write tests', 'priority': 'MEDIUM'})
        with _bypass_db_validation():
            assert form.is_valid(), form.errors

    def test_valid_with_all_fields(self):
        form = TaskForm(
            data={
                'title': 'Full',
                'description': 'desc',
                'priority': 'HIGH',
                'due_date': '2026-12-31',
                'is_done': 'on',
            }
        )
        with _bypass_db_validation():
            assert form.is_valid(), form.errors
        assert form.cleaned_data['is_done'] is True
        assert form.cleaned_data['priority'] == 'HIGH'

    def test_missing_title_is_invalid(self):
        form = TaskForm(data={'priority': 'MEDIUM'})
        with _bypass_db_validation():
            assert not form.is_valid()
        assert 'title' in form.errors

    def test_invalid_priority_choice_rejected(self):
        form = TaskForm(data={'title': 't', 'priority': 'URGENT'})
        with _bypass_db_validation():
            assert not form.is_valid()
        assert 'priority' in form.errors

    def test_invalid_due_date_rejected(self):
        form = TaskForm(
            data={'title': 't', 'priority': 'LOW', 'due_date': 'not-a-date'}
        )
        with _bypass_db_validation():
            assert not form.is_valid()
        assert 'due_date' in form.errors
