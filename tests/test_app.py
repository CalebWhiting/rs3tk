from __future__ import annotations

from unittest.mock import patch

from rs3tk.app import AppError, CharacterInfo, get_all_characters, get_config
from rs3tk.cli import find_default_char_index


def test_find_default_char_index_with_match() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
        CharacterInfo(account_id="b", display_name="Bob", username="u2", is_member=False),
    ]
    assert find_default_char_index(chars, "Bob") == 2


def test_find_default_char_index_no_match() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
    ]
    assert find_default_char_index(chars, "Unknown") is None


def test_find_default_char_index_none_last() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
    ]
    assert find_default_char_index(chars, None) is None


def test_get_config_returns_settings() -> None:
    from rs3tk.config import Settings

    settings = get_config()
    assert isinstance(settings, Settings)


@patch("rs3tk.app.load_settings")
def test_get_all_characters_empty(mock_load: object) -> None:
    from rs3tk.config import Settings

    mock_load.return_value = Settings(accounts=[])
    result = get_all_characters()
    assert result == []
