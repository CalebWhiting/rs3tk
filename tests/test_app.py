from __future__ import annotations

from unittest.mock import patch

from rs3tk.app import CharacterInfo, _get_characters_result, get_all_characters, get_config
from rs3tk.cli import _find_default_char_index


def test_find_default_char_index_with_match() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
        CharacterInfo(account_id="b", display_name="Bob", username="u2", is_member=False),
    ]
    assert _find_default_char_index(chars, "Bob") == 2


def test_find_default_char_index_no_match() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
    ]
    assert _find_default_char_index(chars, "Unknown") is None


def test_find_default_char_index_none_last() -> None:
    chars = [
        CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True),
    ]
    assert _find_default_char_index(chars, None) is None


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


@patch("rs3tk.app.load_settings")
def test_get_characters_result_empty(mock_load: object) -> None:
    from rs3tk.config import Settings

    mock_load.return_value = Settings(accounts=[])
    result = _get_characters_result()
    assert result.characters == []
    assert result.auth_errors == []


@patch("rs3tk.app.load_settings")
def test_get_characters_result_no_accounts(mock_load: object) -> None:
    from rs3tk.config import Settings

    mock_load.return_value = Settings(accounts=[])
    result = _get_characters_result()
    assert isinstance(result.characters, list)
    assert isinstance(result.auth_errors, list)
