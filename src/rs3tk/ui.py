"""Rich terminal UI for rs3tk."""

from __future__ import annotations

import contextlib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rs3tk.app import (
    AppError,
    check_game_status,
    do_login,
    do_logout,
    get_all_characters,
    get_client_info,
    get_config,
    get_news,
    launch_game,
    pick_character,
    pick_client,
    update_config,
)

console = Console()

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
    from rich.prompt import Prompt

    choices = [k for k, _ in _MENU]
    return Prompt.ask("Select", choices=choices, default="0")


def _do_play() -> None:
    from rs3tk.config import load_settings

    settings = load_settings()

    client_key = pick_client(settings)

    from rich.prompt import Confirm

    no_character = Confirm.ask("Launch without character?", default=False)

    if no_character:
        try:
            game_client = __import__("rs3tk.app", fromlist=["get_game_client"]).get_game_client(client_key)
        except AppError as e:
            console.print(f"[bold red]Error:[/] {e}")
            return
        console.print(f"[bold green]Launching {game_client.name}...[/]")
        try:
            process = game_client.launch("", None, None)
            console.print(f"  [dim]PID {process.pid}[/]")
        except (FileNotFoundError, RuntimeError) as e:
            console.print(f"[bold red]Error:[/] {e}")
        return

    characters = get_all_characters()
    if not characters:
        console.print("[bold red]Error:[/] Not logged in. Run `rs3tk auth login` first.")
        return

    character = pick_character(characters, settings)
    if not character:
        return

    try:
        launch_game(client_key, character)
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")


def _do_login() -> None:
    console.print("\n[bold]Login[/]")
    from rich.prompt import Confirm

    system = Confirm.ask("Use system browser?", default=False)
    try:
        username, count = do_login(system_browser=system)
    except AppError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return
    console.print(f"[bold green]Logged in as {username}. Stored accounts: {count}[/]")


def _do_logout() -> None:
    do_logout()
    console.print("[bold yellow]Logged out.[/]")


def _do_accounts() -> None:
    characters = get_all_characters()
    if not characters:
        console.print("[yellow]No characters found.[/]")
        return

    from rs3tk.config import load_settings

    settings = load_settings()
    table = Table(title="Characters")
    table.add_column("Name", style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Account", style="dim")
    table.add_column("Membership", justify="center")
    table.add_column("Default", justify="center")
    table.add_column("Last Played", justify="center")
    for char in characters:
        tag = "[green]Yes[/]" if char.is_member else "[dim]No[/]"
        default = "[green]*[/]" if settings.default_character == char.display_name else ""
        last = "[green]*[/]" if settings.last_character == char.display_name else ""
        table.add_row(char.display_name, char.account_id, char.username, tag, default, last)
    console.print(table)


def _do_clients() -> None:
    table = Table(title="Game Clients")
    table.add_column("Client", style="bold")
    table.add_column("Installed", justify="center")
    table.add_column("Path")
    for client, installed, path in get_client_info():
        tag = "[green]Yes[/]" if installed else "[red]No[/]"
        table.add_row(client.name, tag, path or "-")
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

    table = Table()
    table.add_column("Title", style="bold")
    table.add_column("Date", style="dim")
    for article in articles:
        table.add_row(article.get("title", "Untitled"), article.get("formattedDate", ""))
    console.print(table)


def _do_config() -> None:
    settings = get_config()

    table = Table(title="Settings")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_row("Default game", settings.default_game)
    table.add_row("Default client", settings.default_client)
    table.add_row("Default character", settings.default_character or "(none)")
    table.add_row("Last character", settings.last_character or "(none)")
    table.add_row("Locale", f"{settings.locale} (0=en, 1=de, 2=fr, 3=pt-br)")
    console.print(table)

    from rich.prompt import Confirm

    if not Confirm.ask("\nEdit settings?", default=False):
        return

    from rich.prompt import Prompt

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
