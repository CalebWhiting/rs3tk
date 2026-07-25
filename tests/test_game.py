"""Test game.py module."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from rs3tk.game import GameError, _fetch_with_retry, check_status, fetch_news


class TestGameError:
    """Test GameError exception class."""

    def test_inheritance(self):
        """Test GameError is an Exception."""
        error = GameError("test error")
        assert isinstance(error, Exception)

    def test_error_message(self):
        """Test GameError stores message."""
        error = GameError("test error")
        assert str(error) == "test error"


class TestCheckStatus:
    """Test check_status function."""

    def test_sync_check_status(self):
        """Test the current sync check_status implementation."""
        # This should work with the current implementation
        with patch('httpx.get') as mock_get:
            mock_response = type('obj', (object,), {'json': lambda: {'status': 'ok'}})()
            mock_get.return_value = mock_response
            mock_response.raise_for_status = lambda: None

            result = check_status()
            assert result == {'status': 'ok'}

    def test_check_status_error_handling(self):
        """Test error handling in check_status."""
        with patch('httpx.get') as mock_get:
            mock_get.side_effect = Exception("Network error")

            with pytest.raises(GameError):
                check_status()


class TestFetchNews:
    """Test fetch_news function."""

    def test_fetch_news_osrs(self):
        """Test fetching OSRS news."""
        with patch('rs3tk.game._fetch_with_retry') as mock_retry:
            mock_retry.return_value = [{'title': 'Test News', 'date': '2024-01-01'}]

            result = fetch_news('osrs', count=1)
            assert len(result) == 1
            assert result[0]['title'] == 'Test News'

    def test_fetch_news_rs3(self):
        """Test fetching RS3 news."""
        with patch('rs3tk.game._fetch_with_retry') as mock_retry:
            mock_retry.return_value = [{'title': 'RS3 News', 'date': '2024-01-01'}]

            result = fetch_news('rs3', count=1, locale=0)
            assert len(result) == 1
            assert result[0]['title'] == 'RS3 News'

    def test_fetch_news_empty(self):
        """Test handling empty news results."""
        with patch('rs3tk.game._fetch_with_retry') as mock_retry:
            mock_retry.return_value = []

            result = fetch_news('osrs', count=5)
            assert result == []


class TestFetchWithRetry:
    def test_raises_after_exhaustion(self) -> None:
        with patch("rs3tk.game.httpx.get", side_effect=httpx.ConnectError("fail")):
            with pytest.raises(GameError, match="Failed to fetch"):
                _fetch_with_retry("http://example.com")
