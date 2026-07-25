"""Test helpers and utilities."""

from __future__ import annotations

import pytest


def assert_app_error(func, *args, **kwargs):
    """Assert that a function raises AppError."""
    import pytest

    with pytest.raises(Exception) as exc_info:
        func(*args, **kwargs)

    # Check that it's an AppError
    assert "AppError" in str(type(exc_info.value).__name__)
    return exc_info.value
