"""Configuration: paths, settings, and token storage."""

from __future__ import annotations

import contextlib
import functools
import json
import logging
import os
from enum import StrEnum
from pathlib import Path

import keyring
from pydantic import BaseModel

_SERVICE = "rs3tk"
logger = logging.getLogger(__name__)


class Game(StrEnum):
    RS3 = "rs3"
    OSRS = "osrs"


class ClientType(StrEnum):
    RS3 = "rs3"
    OFFICIAL = "official"
    RUNELITE = "runelite"
    HDOS = "hdos"


GAME_KEYS: tuple[str, ...] = tuple(g.value for g in Game)
CLIENT_KEYS: tuple[str, ...] = tuple(c.value for c in ClientType)


class AccountInfo(BaseModel):
    username: str
    display_name: str | None = None
    email: str | None = None


class Settings(BaseModel):
    default_game: Game = Game.OSRS
    default_client: ClientType = ClientType.OFFICIAL
    locale: int = 0
    last_character: str | None = None
    default_character: str | None = None
    accounts: list[AccountInfo] = []
    model_config = {"use_enum_values": True}


@functools.lru_cache(maxsize=1)
def config_dir() -> Path:
    """Return the rs3tk config directory, creating it if needed.

    Cached for the process lifetime; the XDG_CONFIG_HOME env var is only
    consulted on the first call.
    """
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config = base / "rs3tk"
    config.mkdir(parents=True, exist_ok=True, mode=0o700)
    return config


def fix_permissions() -> None:
    d = config_dir()
    d.chmod(0o700)
    for f in d.iterdir():
        if f.is_file():
            f.chmod(0o600)
        elif f.is_dir():
            f.chmod(0o700)


class _SettingsStore:
    """In-memory cache for the parsed settings.json, with explicit invalidation.

    The store keeps the parsed `Settings` object in memory and the in-memory
    value is the source of truth between save and load. After a successful
    `save_settings`, the in-memory cache is updated; no re-read of disk is
    needed until the next process start.
    """

    def __init__(self) -> None:
        self._settings: Settings | None = None
        self._permissions_fixed: bool = False

    def load(self) -> Settings:
        if self._settings is not None:
            return self._settings
        if not self._permissions_fixed:
            fix_permissions()
            self._permissions_fixed = True
        path = config_dir() / "settings.json"
        if path.exists():
            try:
                self._settings = Settings.model_validate(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                logger.warning("Failed to parse %s, using defaults", path)
                self._settings = Settings()
        else:
            self._settings = Settings()
        return self._settings

    def save(self, settings: Settings) -> None:
        path = config_dir() / "settings.json"
        path.write_text(settings.model_dump_json(indent=2), encoding="utf-8")
        path.chmod(0o600)
        self._settings = settings


_settings_store = _SettingsStore()


def load_settings() -> Settings:
    return _settings_store.load()


def save_settings(settings: Settings) -> None:
    _settings_store.save(settings)


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
