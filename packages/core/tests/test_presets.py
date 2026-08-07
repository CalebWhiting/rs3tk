"""Test presets.py — launch preset storage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from rs3tk_core import presets as presets_mod
from rs3tk_core.app import AppError


@pytest.fixture(autouse=True)
def _reset_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point preset file at a tmp dir and clear the in-memory cache."""
    presets_file = tmp_path / "presets.json"
    monkeypatch.setattr(presets_mod, "_PRESETS_FILE", presets_file)
    presets_mod._presets_store._presets = None
    yield
    presets_mod._presets_store._presets = None


class TestLoadPresets:
    def test_missing_file_returns_empty(self) -> None:
        assert presets_mod.load_presets() == {}

    def test_corrupt_file_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        presets_file = tmp_path / "presets.json"
        presets_file.write_text("not json!!!", encoding="utf-8")
        monkeypatch.setattr(presets_mod, "_PRESETS_FILE", presets_file)
        presets_mod._presets_store._presets = None
        assert presets_mod.load_presets() == {}

    def test_valid_file_returns_dict(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        presets_file = tmp_path / "presets.json"
        presets_file.write_text(json.dumps({"Daily": [["rs3", "Alice"]]}), encoding="utf-8")
        monkeypatch.setattr(presets_mod, "_PRESETS_FILE", presets_file)
        presets_mod._presets_store._presets = None
        result = presets_mod.load_presets()
        assert result == {"Daily": [["rs3", "Alice"]]}


class TestCreatePreset:
    def test_creates_empty_preset(self) -> None:
        result = presets_mod.create_preset("Daily")
        assert "Created empty preset" in result
        assert presets_mod.load_presets()["Daily"] == []

    def test_duplicate_raises(self) -> None:
        presets_mod.create_preset("Daily")
        with pytest.raises(AppError, match="already exists"):
            presets_mod.create_preset("Daily")


class TestDeletePreset:
    def test_deletes_existing(self) -> None:
        presets_mod.create_preset("Daily")
        result = presets_mod.delete_preset("Daily")
        assert "Deleted preset" in result
        assert "Daily" not in presets_mod.load_presets()

    def test_nonexistent_raises(self) -> None:
        with pytest.raises(AppError, match="No such preset"):
            presets_mod.delete_preset("Ghost")


class TestAddToPreset:
    def test_adds_entry(self) -> None:
        presets_mod.create_preset("Daily")
        result = presets_mod.add_to_preset("Daily", "rs3", "Alice")
        assert "Added" in result
        assert presets_mod.load_presets()["Daily"] == [["rs3", "Alice"]]

    def test_adds_multiple_entries(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        presets_mod.add_to_preset("Daily", "runelite", "Bob")
        entries = presets_mod.load_presets()["Daily"]
        assert len(entries) == 2
        assert entries[0] == ["rs3", "Alice"]
        assert entries[1] == ["runelite", "Bob"]

    def test_invalid_client_raises(self) -> None:
        presets_mod.create_preset("Daily")
        with pytest.raises(AppError, match="Invalid client key"):
            presets_mod.add_to_preset("Daily", "bogus", "Alice")

    def test_nonexistent_preset_raises(self) -> None:
        with pytest.raises(AppError, match="doesn't exist"):
            presets_mod.add_to_preset("Ghost", "rs3", "Alice")

    def test_client_is_lowercased(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "RuneLite", "Alice")
        assert presets_mod.load_presets()["Daily"][0][0] == "runelite"


class TestRemoveFromPreset:
    def test_removes_entry(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        presets_mod.add_to_preset("Daily", "runelite", "Bob")
        result = presets_mod.remove_from_preset("Daily", 1)
        assert "Removed" in result
        assert presets_mod.load_presets()["Daily"] == [["runelite", "Bob"]]

    def test_removes_last_entry(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        presets_mod.remove_from_preset("Daily", 1)
        assert presets_mod.load_presets()["Daily"] == []

    def test_out_of_range_raises(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        with pytest.raises(AppError, match="out of range"):
            presets_mod.remove_from_preset("Daily", 5)

    def test_zero_index_raises(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        with pytest.raises(AppError, match="out of range"):
            presets_mod.remove_from_preset("Daily", 0)

    def test_nonexistent_preset_raises(self) -> None:
        with pytest.raises(AppError, match="doesn't exist"):
            presets_mod.remove_from_preset("Ghost", 1)


class TestGetPreset:
    def test_returns_entries(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        entries = presets_mod.get_preset("Daily")
        assert entries == [["rs3", "Alice"]]

    def test_nonexistent_raises(self) -> None:
        with pytest.raises(AppError, match="doesn't exist"):
            presets_mod.get_preset("Ghost")


class TestListPresets:
    def test_empty(self) -> None:
        assert presets_mod.list_presets() == {}

    def test_multiple(self) -> None:
        presets_mod.create_preset("Daily")
        presets_mod.create_preset("Weekly")
        presets_mod.add_to_preset("Daily", "rs3", "Alice")
        presets_mod.add_to_preset("Weekly", "runelite", "Bob")
        result = presets_mod.list_presets()
        assert len(result) == 2
        assert "Daily" in result
        assert "Weekly" in result
