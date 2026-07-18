"""Configuration: paths, settings, and token storage."""

from __future__ import annotations

import contextlib
import json
import os
from enum import StrEnum
from pathlib import Path

import keyring
from pydantic import BaseModel

_SERVICE = "rs3tk"

_config_dir: Path | None = None


def config_dir() -> Path:
    global _config_dir  # noqa: PLW0603
    if _config_dir is not None:
        return _config_dir
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config = base / "rs3tk"
    config.mkdir(parents=True, exist_ok=True, mode=0o700)
    _config_dir = config
    return config


def settings_file() -> Path:
    return config_dir() / "settings.json"


class Game(StrEnum):
    RS3 = "rs3"
    OSRS = "osrs"


class ClientType(StrEnum):
    RS3 = "rs3"
    OFFICIAL = "official"
    RUNELITE = "runelite"
    HDOS = "hdos"


class AccountInfo(BaseModel):
    username: str
    display_name: str | None = None


class Settings(BaseModel):
    default_game: Game = Game.OSRS
    default_client: ClientType = ClientType.OFFICIAL
    locale: int = 0
    last_character: str | None = None
    default_character: str | None = None
    accounts: list[AccountInfo] = []
    model_config = {"use_enum_values": True}


_settings: Settings | None = None
_permissions_fixed: bool = False


def load_settings() -> Settings:
    global _settings  # noqa: PLW0603
    global _permissions_fixed  # noqa: PLW0603
    if _settings is not None:
        return _settings
    if not _permissions_fixed:
        fix_permissions()
        _permissions_fixed = True
    path = settings_file()
    if path.exists():
        try:
            _settings = Settings.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            _settings = Settings()
    else:
        _settings = Settings()
    return _settings


def save_settings(settings: Settings) -> None:
    global _settings  # noqa: PLW0603
    _settings = settings
    path = settings_file()
    path.write_text(settings.model_dump_json(indent=2), encoding="utf-8")
    path.chmod(0o600)


def set_token(key: str, value: str) -> None:
    keyring.set_password(_SERVICE, key, value)


def get_token(key: str) -> str | None:
    try:
        return keyring.get_password(_SERVICE, key)
    except Exception:
        return None


def delete_token(key: str) -> None:
    with contextlib.suppress(keyring.errors.PasswordDeleteError):
        keyring.delete_password(_SERVICE, key)


_ACCOUNT_TOKENS = ("access_token", "refresh_token", "id_token", "consent_id_token", "session_id", "token_issued_at")


def _account_key(username: str, key: str) -> str:
    return f"accounts/{username}/{key}"


def set_account_token(username: str, key: str, value: str) -> None:
    keyring.set_password(_SERVICE, _account_key(username, key), value)


def get_account_token(username: str, key: str) -> str | None:
    try:
        return keyring.get_password(_SERVICE, _account_key(username, key))
    except Exception:
        return None


def delete_account_token(username: str, key: str) -> None:
    with contextlib.suppress(keyring.errors.PasswordDeleteError):
        keyring.delete_password(_SERVICE, _account_key(username, key))


def clear_account(username: str) -> None:
    for key in _ACCOUNT_TOKENS:
        delete_account_token(username, key)


def clear_all() -> None:
    for key in _ACCOUNT_TOKENS:
        delete_token(key)


def fix_permissions() -> None:
    d = config_dir()
    d.chmod(0o700)
    for f in d.iterdir():
        if f.is_file():
            f.chmod(0o600)
        elif f.is_dir():
            f.chmod(0o700)
