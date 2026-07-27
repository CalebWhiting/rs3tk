"""Test helpers and utilities."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


def assert_app_error(func: Callable[..., Any], *args: object, **kwargs: object) -> BaseException:
    """Assert that a function raises AppError."""
    with pytest.raises(Exception) as exc_info:
        func(*args, **kwargs)

    assert "AppError" in type(exc_info.value).__name__
    return exc_info.value
