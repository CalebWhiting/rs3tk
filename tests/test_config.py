"""Test config.py module."""

from __future__ import annotations

import json

from rs3tk.config import AccountInfo, ClientType, Game, Settings


class TestSettingsModel:
    """Test Settings Pydantic model."""

    def test_settings_defaults(self) -> None:
        """Test Settings model has correct defaults."""
        settings = Settings()
        assert settings.default_game == "rs3" or settings.default_game == Game.OSRS
        assert settings.default_client == "official" or settings.default_client == ClientType.OFFICIAL
        assert settings.locale == 0
        assert settings.last_character is None
        assert settings.default_character is None
        assert settings.accounts == []

    def test_settings_with_values(self) -> None:
        """Test Settings model can be created with custom values."""
        settings = Settings(
            default_game="osrs",
            default_client="runelite",
            locale=1,
            last_character="TestChar",
            default_character="DefaultChar",
            accounts=[AccountInfo(username="testuser")],
        )
        assert settings.default_game == "osrs"
        assert settings.default_client == "runelite"
        assert settings.locale == 1
        assert settings.last_character == "TestChar"
        assert settings.default_character == "DefaultChar"
        assert len(settings.accounts) == 1
        assert settings.accounts[0].username == "testuser"

    def test_settings_model_dump_json(self) -> None:
        """Test Settings.model_dump_json works."""
        settings = Settings(default_game="osrs", last_character="TestChar")
        json_str = settings.model_dump_json()
        data = json.loads(json_str)
        assert data["default_game"] == "osrs"
        assert data["last_character"] == "TestChar"


class TestEnumTypes:
    """Test enum types."""

    def test_game_enum(self) -> None:
        """Test Game enum values."""
        assert Game.RS3 == "rs3"
        assert Game.OSRS == "osrs"

    def test_client_type_enum(self) -> None:
        """Test ClientType enum values."""
        assert ClientType.RS3 == "rs3"
        assert ClientType.OFFICIAL == "official"
        assert ClientType.RUNELITE == "runelite"
        assert ClientType.HDOS == "hdos"


class TestAccountInfoModel:
    """Test AccountInfo Pydantic model."""

    def test_account_info_minimum(self) -> None:
        """Test AccountInfo with minimum fields."""
        account = AccountInfo(username="testuser")
        assert account.username == "testuser"
        assert account.display_name is None
        assert account.email is None

    def test_account_info_with_all_fields(self) -> None:
        """Test AccountInfo with all fields."""
        account = AccountInfo(username="testuser", display_name="Display Name", email="test@example.com")
        assert account.username == "testuser"
        assert account.display_name == "Display Name"
        assert account.email == "test@example.com"
