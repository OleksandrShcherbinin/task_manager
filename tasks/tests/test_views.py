"""Unit tests for view functions.

All DB access is mocked: `get_object_or_404` returns a fake Task, and `redirect`
is patched so we don't need a URL resolver.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

from tasks.views import toggle_done


@pytest.fixture
def rf():
    return RequestFactory()


class TestToggleDoneMethodGuard:
    def test_get_returns_405(self, rf):
        request = rf.get('/task/1/toggle/')
        response = toggle_done(request, pk=1)
        assert response.status_code == 405

    def test_put_returns_405(self, rf):
        request = rf.put('/task/1/toggle/')
        response = toggle_done(request, pk=1)
        assert response.status_code == 405


@patch('tasks.views.redirect')
@patch('tasks.views.get_object_or_404')
class TestToggleDoneBehavior:
    def test_post_flips_pending_to_done(self, mock_get, mock_redirect, rf):
        task = MagicMock(is_done=False)
        mock_get.return_value = task

        request = rf.post('/task/1/toggle/', {'next': '/some/path/'})
        toggle_done(request, pk=1)

        assert task.is_done is True
        task.save.assert_called_once_with(update_fields=['is_done'])
        mock_redirect.assert_called_once_with('/some/path/')

    def test_post_flips_done_to_pending(self, mock_get, mock_redirect, rf):
        task = MagicMock(is_done=True)
        mock_get.return_value = task

        request = rf.post('/task/1/toggle/', {'next': '/'})
        toggle_done(request, pk=1)

        assert task.is_done is False
        task.save.assert_called_once_with(update_fields=['is_done'])

    def test_post_without_next_falls_back_to_list_url(
        self, mock_get, mock_redirect, rf
    ):
        task = MagicMock(is_done=False)
        mock_get.return_value = task

        request = rf.post('/task/1/toggle/', {})
        toggle_done(request, pk=1)

        task.save.assert_called_once()
        # The fallback uses reverse_lazy('tasks:list'); we don't assert the
        # exact URL string (that's Django's job), only that redirect was called.
        mock_redirect.assert_called_once()

    def test_post_uses_pk_from_url(self, mock_get, mock_redirect, rf):
        mock_get.return_value = MagicMock(is_done=False)

        request = rf.post('/task/42/toggle/', {'next': '/'})
        toggle_done(request, pk=42)

        # First positional arg is the model class, second is pk
        args, kwargs = mock_get.call_args
        assert kwargs.get('pk') == 42 or 42 in args
