#!/usr/bin/env python3
"""Test fixtures and base test classes for rs3tk tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from rs3tk.config import Settings


@pytest.fixture
def temp_config_dir() -> Path:
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rs3tk"
        config_dir.mkdir(parents=True, exist_ok=True)
        yield config_dir


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        default_game="rs3",
        default_client="official",
        locale=0,
        accounts=[],
    )


@pytest.fixture
def app_error_base_class():
    """Import AppError for testing."""
    from rs3tk.app import AppError
    yield AppError


def assert_app_error(func, *args, **kwargs):
    """Assert that a function raises AppError."""
    import pytest
    with pytest.raises(Exception) as exc_info:
        func(*args, **kwargs)
    assert "AppError" in str(type(exc_info.value).__name__)
    return exc_info.value
