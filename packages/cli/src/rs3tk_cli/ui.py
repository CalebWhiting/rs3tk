"""Rich terminal UI for rs3tk."""

from __future__ import annotations

import contextlib

from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rs3tk_core.app import (
    AppError,
    check_game_status,
    do_login,
    do_logout,
    get_all_characters,
    get_client_info,
    get_config,
    get_news,
    launch_game,
    update_config,
)
from rs3tk_core.config import load_settings

from rs3tk_cli.cli import pick_character, pick_client
from rs3tk_cli.output import console
from rs3tk_cli.tables import build_characters_table, build_clients_table, build_config_display, build_news_table

_MENU = [
    ("1", "Play"),
    ("2", "Login"),
    ("3", "Logout"),
    ("4", "Accounts"),
    ("5", "Clients"),
    ("6", "Status"),
    ("7", "News"),
    ("8", "Config"),
    ("0", "Exit"),
]


def _clear() -> None:
    console.clear()


def _pause() -> None:
    console.input("\n[dim]Press Enter to continue...[/]")


def _show_menu() -> str:
    _clear()
    console.print(Panel("[bold]RS3 ToolKit[/]", title="RS3TK", expand=False))
    for key, label in _MENU:
        console.print(f"  [bold]{key}[/]. {label}")
    console.print()
    choices = [k for k, _ in _MENU]
    return Prompt.ask("Select", choices=choices, default="0")


def _do_play() -> None:
    from rs3tk_core.app import launch_without_character

    settings = load_settings()

    client_key = pick_client(settings)

    no_character = Confirm.ask("Launch without character?", default=False)

    if no_character:
        try:
            launch_without_character(client_key)
        except AppError as e:
            console.print(f"[bold red]Error:[/] {e}")
        return

    characters = get_all_characters()
    if not characters:
        console.print("[bold red]Error:[/] Not logged in. Run `rs3tk auth login` first.")
        return

    character = pick_character(characters, settings)

    try:
        launch_game(client_key, character)
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")


def _do_login() -> None:
    console.print("\n[bold]Login[/]")
    try:
        username, count = do_login()
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return
    console.print(f"[bold green]Logged in as {username}. Stored accounts: {count}[/]")


def _do_logout() -> None:
    try:
        do_logout()
        console.print("[bold yellow]Logged out.[/]")
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")


def _do_accounts() -> None:
    characters = get_all_characters()
    if not characters:
        console.print("[yellow]No characters found.[/]")
        return

    settings = load_settings()
    table = build_characters_table(characters, settings)
    console.print(table)


def _do_clients() -> None:
    table = build_clients_table(get_client_info())
    console.print(table)


def _do_status() -> None:
    try:
        data = check_game_status()
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    if data.get("playDisabled"):
        console.print("[bold red]Game is currently offline for maintenance.[/]")
    elif data.get("psaEnabled"):
        console.print(f"[bold yellow]PSA:[/] {data.get('psaMessage', '')}")
    else:
        console.print("[bold green]All systems operational.[/]")


def _do_news() -> None:
    try:
        articles = get_news()
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    if not articles:
        console.print("[yellow]No news found.[/]")
        return

    table = build_news_table(articles, "News")
    console.print(table)


def _do_config() -> None:
    settings = get_config()

    table = build_config_display(settings)
    console.print(table)

    if not Confirm.ask("\nEdit settings?", default=False):
        return

    game = Prompt.ask("Default game", default=settings.default_game)
    client = Prompt.ask("Default client", default=settings.default_client)
    locale_str = Prompt.ask("Locale (0=en, 1=de, 2=fr, 3=pt-br)", default=str(settings.locale))

    locale_int = settings.locale
    with contextlib.suppress(ValueError):
        locale_int = int(locale_str)

    if update_config(
        game=game if game != settings.default_game else None,
        client=client if client != settings.default_client else None,
        locale=locale_int if locale_int != settings.locale else None,
    ):
        console.print("[bold green]Settings updated.[/]")
    else:
        console.print("[dim]No changes.[/]")


_ACTIONS = {
    "1": _do_play,
    "2": _do_login,
    "3": _do_logout,
    "4": _do_accounts,
    "5": _do_clients,
    "6": _do_status,
    "7": _do_news,
    "8": _do_config,
}


def run_ui() -> None:
    while True:
        choice = _show_menu()
        if choice == "0":
            _clear()
            break
        action = _ACTIONS.get(choice)
        if action:
            _clear()
            action()
            _pause()
