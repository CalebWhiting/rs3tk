"""Shared application logic for CLI and UI."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from rs3tk.clients import CLIENTS_DIR, GameClient, detect_client, get_client_keys, update_client_config
from rs3tk.config import AccountInfo, Settings, load_settings, save_settings

logger = logging.getLogger(__name__)


class AppError(Exception):
    pass


@dataclass(slots=True)
class CharacterInfo:
    account_id: str
    display_name: str
    username: str
    is_member: bool


def do_login(system_browser: bool = False) -> tuple[str, int]:
    from rs3tk.auth.session import login as _login

    try:
        tokens, username = asyncio.run(_login(system_browser=system_browser))
    except RuntimeError as e:
        raise AppError(str(e)) from e

    settings = load_settings()
    existing = [a for a in settings.accounts if a.username == username]
    if not existing:
        settings = settings.model_copy(update={"accounts": settings.accounts + [AccountInfo(username=username)]})
        save_settings(settings)

    return username, len(settings.accounts)


def do_logout(username: str | None = None, *, all_accounts: bool = False) -> None:
    from rs3tk.auth.session import logout_account

    settings = load_settings()

    if all_accounts:
        for account in settings.accounts:
            logout_account(account.username)
        settings = settings.model_copy(update={"accounts": []})
        save_settings(settings)
        return

    if username is None:
        if settings.accounts:
            username = settings.accounts[0].username
        else:
            return

    logout_account(username)
    settings = settings.model_copy(update={"accounts": [a for a in settings.accounts if a.username != username]})
    save_settings(settings)


def get_session_and_profile(username: str | None = None) -> tuple[str, Any]:
    from rs3tk.auth.session import get_session

    if username is None:
        settings = load_settings()
        if not settings.accounts:
            raise AppError("Not logged in. Run `rs3tk login` first.")
        username = settings.accounts[0].username

    try:
        return asyncio.run(get_session(username))
    except RuntimeError as e:
        raise AppError(str(e)) from e


def get_all_characters() -> list[CharacterInfo]:
    settings = load_settings()
    if not settings.accounts:
        return []

    async def _fetch_all() -> list[CharacterInfo]:
        from rs3tk.auth.session import get_session

        failed: list[str] = []

        async def _fetch_one(username: str) -> list[CharacterInfo]:
            try:
                _, profile = await get_session(username)
                return [
                    CharacterInfo(
                        account_id=char.account_id,
                        display_name=char.display_name,
                        username=username,
                        is_member=char.is_member,
                    )
                    for char in profile.characters
                ]
            except Exception:
                logger.debug("Failed to fetch profile for %s", username, exc_info=True)
                failed.append(username)
                return []

        results = await asyncio.gather(*[_fetch_one(a.username) for a in settings.accounts])
        if failed:
            logger.warning("Failed to fetch profiles for: %s", ", ".join(failed))
        return [char for batch in results for char in batch]

    return asyncio.run(_fetch_all())


def get_account_for_character(character_name: str) -> str | None:
    for char in get_all_characters():
        if char.display_name.lower() == character_name.lower():
            return char.username
    return None


def resolve_character(character_name: str, profile: Any) -> tuple[str, str]:  # noqa: ANN401
    for char in profile.characters:
        if char.display_name.lower() == character_name.lower():
            return char.account_id, char.display_name
    raise AppError(f"Character '{character_name}' not found.")


def get_game_client(name: str) -> GameClient:
    client = detect_client(name)
    if not client.is_installed():
        raise AppError(f"{client.name} is not installed.")
    return client


def list_accounts() -> list[AccountInfo]:
    return load_settings().accounts


def remove_account(username: str) -> None:
    from rs3tk.auth.session import logout_account as _logout_account

    _logout_account(username)
    _remove_account_from_settings(username)


def _remove_account_from_settings(username: str) -> Settings:
    settings = load_settings()
    settings = settings.model_copy(update={"accounts": [a for a in settings.accounts if a.username != username]})
    save_settings(settings)
    return settings


def set_default_character(name: str) -> None:
    settings = load_settings()
    save_settings(settings.model_copy(update={"default_character": name}))


def unset_default_character() -> None:
    settings = load_settings()
    save_settings(settings.model_copy(update={"default_character": None}))


def check_game_status() -> dict[str, Any]:
    from rs3tk.game import GameError, check_status

    try:
        return check_status()
    except GameError as e:
        raise AppError(str(e)) from e


def get_news(game: str | None = None, count: int = 5, locale: int = 0) -> list[dict[str, str]]:
    from rs3tk.game import GameError, fetch_news

    settings = load_settings()
    if game is None:
        game = settings.default_game
    try:
        return fetch_news(game, count=count, locale=locale if locale else settings.locale)
    except GameError as e:
        raise AppError(str(e)) from e


def get_config() -> Settings:
    return load_settings()


def update_config(game: str | None = None, client: str | None = None, locale: int | None = None) -> bool:
    settings = load_settings()
    updates: dict[str, str | int] = {}
    if game is not None:
        updates["default_game"] = game
    if client is not None:
        updates["default_client"] = client
    if locale is not None:
        updates["locale"] = locale
    if updates:
        settings = settings.model_copy(update=updates)
        save_settings(settings)
        return True
    return False


def get_client_info() -> list[tuple[GameClient, bool, str | None]]:
    result: list[tuple[GameClient, bool, str | None]] = []
    for key in get_client_keys():
        client = detect_client(key)
        installed = client.is_installed()
        result.append((client, installed, str(client.executable()) if installed else None))
    return result


def do_autoinstall(client_key: str, remove: bool = False) -> str:
    if remove:
        client_dir = CLIENTS_DIR / client_key
        if client_dir.is_dir():
            shutil.rmtree(client_dir)
        update_client_config(client_key, paths=[], env={})
        return f"Removed {client_key}"

    from rs3tk.install import InstallError, install_client

    try:
        exe_path = install_client(client_key)
    except InstallError as e:
        raise AppError(str(e)) from e

    proc = subprocess.run([str(exe_path), "--install-only"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise AppError(proc.stderr or "Install failed")

    update_client_config(client_key, paths=[str(exe_path)])
    return proc.stdout.strip() + f"\nInstalled {client_key} -> {exe_path}"


def launch_game(
    client_key: str,
    character_name: str | None = None,
    *,
    foreground: bool = False,
) -> None:
    game_client = get_game_client(client_key)

    session_id = ""
    character_id: str | None = None
    display_name: str | None = None

    if character_name:
        username = get_account_for_character(character_name)
        if not username:
            raise AppError(f"Character '{character_name}' not found in any stored account.")

        session_id, profile = get_session_and_profile(username)

        character_id, display_name = resolve_character(character_name, profile)
        settings = load_settings()
        save_settings(settings.model_copy(update={"last_character": display_name}))

    from rs3tk.output import console

    console.print(f"[bold green]Launching {game_client.name}...[/]")
    try:
        process = game_client.launch(session_id, character_id, display_name, foreground=foreground)
        console.print(f"  [dim]PID {process.pid}[/]")
    except (FileNotFoundError, RuntimeError) as e:
        raise AppError(str(e)) from e
