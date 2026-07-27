from __future__ import annotations

from rich.table import Table

from rs3tk.app import CharacterInfo
from rs3tk.clients import GameClient
from rs3tk.config import Settings
from rs3tk.tables import (
    build_characters_table,
    build_clients_table,
    build_config_display,
    build_news_table,
)


def test_build_characters_table_basic() -> None:
    chars = [CharacterInfo(account_id="1", display_name="Alice", username="u1", is_member=True)]
    settings = Settings()
    table = build_characters_table(chars, settings)
    assert isinstance(table, Table)
    assert table.title == "Characters"


def test_build_characters_table_censored() -> None:
    chars = [CharacterInfo(account_id="1", display_name="Alice", username="u1", is_member=True)]
    settings = Settings()
    table = build_characters_table(chars, settings, censor=True)
    assert isinstance(table, Table)


def test_build_characters_table_empty() -> None:
    settings = Settings()
    table = build_characters_table([], settings)
    assert isinstance(table, Table)


def test_build_clients_table() -> None:
    client = GameClient(key="runelite", name="RuneLite")
    table = build_clients_table([(client, True, "/usr/bin/runelite")])
    assert isinstance(table, Table)


def test_build_news_table() -> None:
    articles = [{"title": "Update", "formattedDate": "2025-01-01"}]
    table = build_news_table(articles, "News")
    assert isinstance(table, Table)
    assert table.title == "News"


def test_build_config_display() -> None:
    settings = Settings()
    table = build_config_display(settings)
    assert isinstance(table, Table)
    assert table.title == "Settings"
