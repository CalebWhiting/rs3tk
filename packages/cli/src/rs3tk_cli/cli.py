"""CLI entry point for RS3TK."""

from __future__ import annotations

import logging

import click
from rich.prompt import Prompt
from rich.table import Table
from rs3tk_core import __version__
from rs3tk_core.app import (
    CharacterInfo,
    check_game_status,
    do_autoinstall,
    do_login,
    do_logout,
    get_all_characters,
    get_client_info,
    get_config,
    get_news,
    launch_game,
    launch_without_character,
    list_accounts,
    set_default_character,
    unset_default_character,
    update_config,
)
from rs3tk_core.clients import detect_client, get_client_keys
from rs3tk_core.config import CLIENT_KEYS, GAME_KEYS, Settings, load_settings, save_settings

from rs3tk_cli.output import cli_error, console
from rs3tk_cli.tables import build_characters_table, build_clients_table, build_config_display, build_news_table


def _censor_value(value: str) -> str:
    return "*" * len(value)


def _find_default_char_index(characters: list[CharacterInfo], last_character: str | None) -> int | None:
    if last_character:
        for i, char in enumerate(characters, 1):
            if char.display_name.lower() == last_character.lower():
                return i
    return None


def pick_client(settings: Settings) -> str:
    keys = get_client_keys()
    console.print("[bold]Available clients:[/]")
    for i, key in enumerate(keys, 1):
        c = detect_client(key)
        tag = "[green]installed[/]" if c.is_installed() else "[red]not installed[/]"
        console.print(f"  {i}. {c.name} ({tag})")

    default_idx = keys.index(settings.default_client) + 1 if settings.default_client in keys else 1
    choice = Prompt.ask(
        "\n[bold]Select client[/]",
        choices=[str(i) for i in range(1, len(keys) + 1)],
        default=str(default_idx),
    )
    return keys[int(choice) - 1]


def pick_character(characters: list[CharacterInfo], settings: Settings) -> str:
    if not characters:
        raise ValueError("pick_character requires at least one character")

    console.print("\n[bold]Characters:[/]")
    for i, char in enumerate(characters, 1):
        console.print(f"  {i}. {char.display_name}")

    preferred = settings.default_character or settings.last_character
    default_idx = _find_default_char_index(characters, preferred)
    ch = Prompt.ask(
        "\n[bold]Select character[/]",
        choices=[str(i) for i in range(1, len(characters) + 1)],
        default=str(default_idx) if default_idx is not None else "1",
    )
    return characters[int(ch) - 1].display_name


@click.group()
@click.version_option(__version__, prog_name="RS3TK")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.option("-#", "--censor", is_flag=True, help="Censor sensitive data.")
@click.pass_context
def main(ctx: click.Context, verbose: bool, censor: bool) -> None:
    """RS3 ToolKit — Open-source Jagex Launcher replacement."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["censor"] = censor

    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


# ── auth ─────────────────────────────────────────────────────────────────────


@main.group()
def auth() -> None:
    """Manage Jagex account authentication."""


@auth.command("login")
@click.option("-b", "--system-browser", is_flag=True, help="Use system browser with manual URL paste.")
@click.pass_context
@cli_error
def auth_login(ctx: click.Context, system_browser: bool) -> None:
    """Log in to your Jagex Account."""
    username, count = do_login(system_browser=system_browser)
    console.print(f"[bold green]Logged in as {username}. Stored accounts: {count}[/]")


@auth.command("logout")
@click.option("-a", "--all", "all_accounts", is_flag=True, help="Log out of all accounts.")
@click.option("-u", "--username", default=None, help="Account username to log out.")
@click.pass_context
@cli_error
def auth_logout(ctx: click.Context, all_accounts: bool, username: str | None) -> None:
    """Log out and clear stored tokens."""
    do_logout(username, all_accounts=all_accounts)
    console.print("[bold yellow]Logged out.[/]")


@auth.command("list")
@click.pass_context
def auth_list(ctx: click.Context) -> None:
    """List stored Jagex accounts."""
    accounts_list = list_accounts()
    if not accounts_list:
        console.print("[yellow]No accounts found.[/]")
        return

    table = Table()
    table.add_column("Username", style="bold")
    for account in accounts_list:
        username = _censor_value(account.username) if ctx.obj["censor"] else account.username
        table.add_row(username)
    console.print(table)


# ── accounts ─────────────────────────────────────────────────────────────────


@main.group(invoke_without_command=True)
@click.pass_context
def accounts(ctx: click.Context) -> None:
    """Manage characters across accounts."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(accounts_list)


@accounts.command("list")
@click.pass_context
def accounts_list(ctx: click.Context) -> None:
    """List characters across all accounts."""
    all_characters = get_all_characters()
    if not all_characters:
        console.print("[yellow]No characters found.[/]")
        return

    settings = load_settings()
    table = build_characters_table(all_characters, settings, censor=ctx.obj["censor"])
    console.print(table)


@accounts.command("set-default")
@click.argument("name")
def accounts_set_default(name: str) -> None:
    """Set a default character for quick launching."""
    all_characters = get_all_characters()
    if not any(c.display_name.lower() == name.lower() for c in all_characters):
        raise click.ClickException(f"Character '{name}' not found in any stored account.")

    set_default_character(name)
    console.print(f"[bold green]Default character set to {name}.[/]")


@accounts.command("unset-default")
def accounts_unset_default() -> None:
    """Clear the default character."""
    settings = load_settings()
    if not settings.default_character:
        console.print("[dim]No default character set.[/]")
        return

    unset_default_character()
    console.print("[bold yellow]Default character cleared.[/]")


# ── clients ──────────────────────────────────────────────────────────────────


@main.group(invoke_without_command=True)
@click.pass_context
def clients(ctx: click.Context) -> None:
    """Manage game clients."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(clients_list)


@clients.command("list")
def clients_list() -> None:
    """Show detected game clients and their install paths."""
    table = build_clients_table(get_client_info())
    console.print(table)


@clients.command("install")
@click.argument("client", type=click.Choice(list(CLIENT_KEYS), case_sensitive=False))
@click.pass_context
@cli_error
def clients_install(ctx: click.Context, client: str) -> None:
    """Install a game client."""
    with console.status(f"[bold green]Installing {client}..."):
        result = do_autoinstall(client)
    console.print(f"[bold green]{result}[/]")


@clients.command("remove")
@click.argument("client", type=click.Choice(list(CLIENT_KEYS), case_sensitive=False))
@click.pass_context
@cli_error
def clients_remove(ctx: click.Context, client: str) -> None:
    """Remove a game client."""
    with console.status(f"[bold yellow]Removing {client}..."):
        result = do_autoinstall(client, remove=True)
    console.print(f"[bold green]{result}[/]")


@clients.command("set-default")
@click.argument("client", type=click.Choice(list(CLIENT_KEYS), case_sensitive=False))
def clients_set_default(client: str) -> None:
    """Set the default game client."""
    settings = load_settings()
    save_settings(settings.model_copy(update={"default_client": client}))
    console.print(f"[bold green]Default client set to {client}.[/]")


# ── play ─────────────────────────────────────────────────────────────────────


@main.command()
@click.argument("client", required=False, default=None)
@click.option("--character", "-c", default=None, help="Character name to play.")
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode.")
@click.option("-f", "--foreground", is_flag=True, help="Run client in foreground (show logs).")
@click.option("-n", "--no-character", is_flag=True, help="Launch without JX_* env variables.")
@click.pass_context
@cli_error
def play(
    ctx: click.Context,
    client: str | None,
    character: str | None,
    interactive: bool,
    foreground: bool,
    no_character: bool,
) -> None:
    """Launch a game client. CLIENT is one of: rs3, official, runelite, hdos."""
    settings = load_settings()

    if interactive or client is None:
        client = pick_client(settings)

    if no_character:
        launch_without_character(client, foreground=foreground)
        return

    characters = get_all_characters()
    if not characters:
        raise click.ClickException("Not logged in. Run `rs3tk auth login` first.")

    if not character:
        character = pick_character(characters, settings)

    launch_game(client, character, foreground=foreground)


# ── info ─────────────────────────────────────────────────────────────────────


@main.command()
@click.pass_context
@cli_error
def status(ctx: click.Context) -> None:
    """Check game server status."""
    data = check_game_status()

    if data.get("playDisabled"):
        console.print("[bold red]Game is currently offline for maintenance.[/]")
    elif data.get("psaEnabled"):
        console.print(f"[bold yellow]PSA:[/] {data.get('psaMessage', '')}")
    else:
        console.print("[bold green]All systems operational.[/]")


@main.command()
@click.option("--count", "-n", default=5, help="Number of news items.")
@click.option("--game", type=click.Choice(list(GAME_KEYS), case_sensitive=False), default=None)
@click.pass_context
@cli_error
def news(ctx: click.Context, count: int, game: str | None) -> None:
    """Fetch latest game news."""
    resolved_game = game or load_settings().default_game

    articles = get_news(game=resolved_game, count=count)

    if not articles:
        console.print("[yellow]No news found.[/]")
        return

    table = build_news_table(articles, f"Latest {resolved_game.upper()} News")
    console.print(table)


# ── config ───────────────────────────────────────────────────────────────────


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx: click.Context) -> None:
    """View or modify rs3tk settings."""
    if ctx.invoked_subcommand is None:
        s = get_config()
        table = build_config_display(s)
        console.print(table)


@config.command("set")
@click.option("--game", type=click.Choice(list(GAME_KEYS), case_sensitive=False))
@click.option("--client", type=click.Choice(list(CLIENT_KEYS), case_sensitive=False))
@click.option("--locale", type=int, help="Language locale (0=en, 1=de, 2=fr, 3=pt-br).")
def config_set(game: str | None, client: str | None, locale: int | None) -> None:
    """Update a setting."""
    if update_config(game=game, client=client, locale=locale):
        console.print("[bold green]Settings updated.[/]")
    else:
        console.print("[dim]No changes.[/]")


# ── ui ───────────────────────────────────────────────────────────────────────


@main.command()
def ui() -> None:
    """Open interactive terminal UI."""
    from rs3tk_cli.ui import run_ui

    run_ui()
