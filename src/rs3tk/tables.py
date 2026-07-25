from __future__ import annotations

from typing import Any

from rich.table import Table

from rs3tk.app import CharacterInfo
from rs3tk.clients import GameClient
from rs3tk.config import Settings


def build_accounts_table(characters: list[CharacterInfo], censor: bool = False) -> Table:
    table = Table(title="Accounts")
    table.add_column("Account", style="cyan")
    table.add_column("Character", style="green")
    table.add_column("Member", justify="center")
    for c in characters:
        name = "*" * len(c.display_name) if censor else c.display_name
        table.add_row(c.username, name, "Yes" if c.is_member else "No")
    return table


def build_characters_table(characters: list[CharacterInfo], settings: Settings, censor: bool = False) -> Table:
    table = Table(title="Characters")
    table.add_column("Name", style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Account", style="dim")
    table.add_column("Membership", justify="center")
    table.add_column("Default", justify="center")
    table.add_column("Last Played", justify="center")
    for char in characters:
        tag = "[green]Yes[/]" if char.is_member else "[dim]No[/]"
        account = "*" * len(char.username) if censor else char.username
        char_id = "*" * len(char.account_id) if censor else char.account_id
        default = "[green]*[/]" if settings.default_character == char.display_name else ""
        last = "[green]*[/]" if settings.last_character == char.display_name else ""
        table.add_row(char.display_name, char_id, account, tag, default, last)
    return table


def build_clients_table(clients: list[tuple[GameClient, bool, str | None]]) -> Table:
    table = Table(title="Game Clients")
    table.add_column("Client", style="bold")
    table.add_column("Installed", justify="center")
    table.add_column("Path")
    for client, installed, path in clients:
        tag = "[green]Yes[/]" if installed else "[red]No[/]"
        table.add_row(client.name, tag, path or "-")
    return table


def build_status_table(status: dict[str, Any]) -> Table:
    table = Table(title="Game Status")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for key, value in status.items():
        table.add_row(key, str(value))
    return table


def build_news_table(articles: list[dict[str, str]], title: str) -> Table:
    table = Table(title=title)
    table.add_column("Title", style="bold")
    table.add_column("Date", style="dim")
    for article in articles:
        table.add_row(article.get("title", "Untitled"), article.get("formattedDate", ""))
    return table


def build_config_display(settings: Settings) -> Table:
    table = Table(title="Settings")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_row("Default game", settings.default_game)
    table.add_row("Default client", settings.default_client)
    table.add_row("Default character", settings.default_character or "(none)")
    table.add_row("Last character", settings.last_character or "(none)")
    table.add_row("Locale", f"{settings.locale} (0=en, 1=de, 2=fr, 3=pt-br)")
    return table
