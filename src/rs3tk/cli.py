"""CLI entry point for RS3TK."""

from __future__ import annotations

import logging

import click
from rich.console import Console
from rich.table import Table

from rs3tk import __version__
from rs3tk.app import (
    AppError,
    check_game_status,
    do_autoinstall,
    do_login,
    do_logout,
    get_all_characters,
    get_client_info,
    get_config,
    get_game_client,
    get_news,
    launch_game,
    list_accounts,
    pick_character,
    pick_client,
    update_config,
)

console = Console()


def _censor_value(value: str) -> str:
    return "*" * len(value)


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
def auth_login(system_browser: bool) -> None:
    """Log in to your Jagex Account."""
    try:
        username, count = do_login(system_browser=system_browser)
    except AppError as e:
        raise click.ClickException(str(e)) from None
    console.print(f"[bold green]Logged in as {username}. Stored accounts: {count}[/]")


@auth.command("logout")
@click.option("-a", "--all", "all_accounts", is_flag=True, help="Log out of all accounts.")
@click.option("-u", "--username", default=None, help="Account username to log out.")
def auth_logout(all_accounts: bool, username: str | None) -> None:
    """Log out and clear stored tokens."""
    try:
        do_logout(username, all_accounts=all_accounts)
    except AppError as e:
        raise click.ClickException(str(e)) from None
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

    from rs3tk.config import load_settings

    settings = load_settings()
    table = Table()
    table.add_column("Name", style="bold")
    table.add_column("Account", style="dim")
    table.add_column("Membership", justify="center")
    table.add_column("Default", justify="center")
    table.add_column("Last Played", justify="center")
    for char in all_characters:
        tag = "[green]Yes[/]" if char.is_member else "[dim]No[/]"
        account = _censor_value(char.username) if ctx.obj["censor"] else char.username
        default = "[green]*[/]" if settings.default_character == char.display_name else ""
        last = "[green]*[/]" if settings.last_character == char.display_name else ""
        table.add_row(char.display_name, account, tag, default, last)
    console.print(table)


@accounts.command("set-default")
@click.argument("name")
def accounts_set_default(name: str) -> None:
    """Set a default character for quick launching."""
    from rs3tk.config import load_settings, save_settings

    all_characters = get_all_characters()
    if not any(c.display_name.lower() == name.lower() for c in all_characters):
        raise click.ClickException(f"Character '{name}' not found in any stored account.")

    settings = load_settings()
    save_settings(settings.model_copy(update={"default_character": name}))
    console.print(f"[bold green]Default character set to {name}.[/]")


@accounts.command("unset-default")
def accounts_unset_default() -> None:
    """Clear the default character."""
    from rs3tk.config import load_settings, save_settings

    settings = load_settings()
    if not settings.default_character:
        console.print("[dim]No default character set.[/]")
        return

    save_settings(settings.model_copy(update={"default_character": None}))
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
    table = Table()
    table.add_column("Client", style="bold")
    table.add_column("Installed", justify="center")
    table.add_column("Path")
    for client, installed, path in get_client_info():
        tag = "[green]Yes[/]" if installed else "[red]No[/]"
        table.add_row(client.name, tag, path or "-")
    console.print(table)


@clients.command("install")
@click.argument("client", type=click.Choice(["rs3", "official", "runelite", "hdos"], case_sensitive=False))
def clients_install(client: str) -> None:
    """Install a game client."""
    with console.status(f"[bold green]Installing {client}..."):
        try:
            result = do_autoinstall(client)
        except AppError as e:
            raise click.ClickException(str(e)) from None
    console.print(f"[bold green]{result}[/]")


@clients.command("remove")
@click.argument("client", type=click.Choice(["rs3", "official", "runelite", "hdos"], case_sensitive=False))
def clients_remove(client: str) -> None:
    """Remove a game client."""
    with console.status(f"[bold yellow]Removing {client}..."):
        try:
            result = do_autoinstall(client, remove=True)
        except AppError as e:
            raise click.ClickException(str(e)) from None
    console.print(f"[bold green]{result}[/]")


@clients.command("set-default")
@click.argument("client", type=click.Choice(["rs3", "official", "runelite", "hdos"], case_sensitive=False))
def clients_set_default(client: str) -> None:
    """Set the default game client."""
    from rs3tk.config import load_settings, save_settings

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
def play(
    ctx: click.Context,
    client: str | None,
    character: str | None,
    interactive: bool,
    foreground: bool,
    no_character: bool,
) -> None:
    """Launch a game client. CLIENT is one of: rs3, official, runelite, hdos."""
    from rs3tk.config import load_settings

    settings = load_settings()

    if interactive or client is None:
        client = pick_client(settings)

    if no_character:
        try:
            game_client = get_game_client(client)
        except AppError as e:
            raise click.ClickException(str(e)) from None
        console.print(f"[bold green]Launching {game_client.name}...[/]")
        try:
            process = game_client.launch("", None, None, foreground=foreground)
            console.print(f"  [dim]PID {process.pid}[/]")
        except (FileNotFoundError, RuntimeError) as e:
            raise click.ClickException(str(e)) from None
        return

    characters = get_all_characters()
    if not characters:
        raise click.ClickException("Not logged in. Run `rs3tk auth login` first.")

    if not character:
        character = pick_character(characters, settings)

    try:
        launch_game(client, character, foreground=foreground)
    except AppError as e:
        raise click.ClickException(str(e)) from None


# ── info ─────────────────────────────────────────────────────────────────────


@main.command()
def status() -> None:
    """Check game server status."""
    try:
        data = check_game_status()
    except AppError as e:
        raise click.ClickException(str(e)) from None

    if data.get("playDisabled"):
        console.print("[bold red]Game is currently offline for maintenance.[/]")
    elif data.get("psaEnabled"):
        console.print(f"[bold yellow]PSA:[/] {data.get('psaMessage', '')}")
    else:
        console.print("[bold green]All systems operational.[/]")


@main.command()
@click.option("--count", "-n", default=5, help="Number of news items.")
@click.option("--game", type=click.Choice(["rs3", "osrs"], case_sensitive=False), default=None)
def news(count: int, game: str | None) -> None:
    """Fetch latest game news."""
    from rs3tk.config import load_settings

    resolved_game = game or load_settings().default_game

    try:
        articles = get_news(game=game, count=count)
    except AppError as e:
        raise click.ClickException(str(e)) from None

    if not articles:
        console.print("[yellow]No news found.[/]")
        return

    table = Table(title=f"Latest {resolved_game.upper()} News")
    table.add_column("Title", style="bold")
    table.add_column("Date", style="dim")
    for article in articles:
        table.add_row(article.get("title", "Untitled"), article.get("formattedDate", ""))
    console.print(table)


# ── config ───────────────────────────────────────────────────────────────────


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx: click.Context) -> None:
    """View or modify rs3tk settings."""
    if ctx.invoked_subcommand is None:
        s = get_config()
        for label, val in [
            ("Default game", s.default_game),
            ("Default client", s.default_client),
            ("Default character", s.default_character or "(none)"),
            ("Last character", s.last_character or "(none)"),
            ("Locale", f"{s.locale} (0=en, 1=de, 2=fr, 3=pt-br)"),
        ]:
            console.print(f"{label}: [bold]{val}[/]")


@config.command("set")
@click.option("--game", type=click.Choice(["rs3", "osrs"], case_sensitive=False))
@click.option("--client", type=click.Choice(["rs3", "official", "runelite", "hdos"], case_sensitive=False))
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
    from rs3tk.ui import run_ui

    run_ui()
