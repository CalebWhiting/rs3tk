"""Launch presets — named lists of (client, character) pairs."""

from __future__ import annotations

import json
import logging

from rs3tk_core.app import AppError
from rs3tk_core.config import CLIENT_KEYS, config_dir

logger = logging.getLogger(__name__)

_PRESETS_FILE = config_dir() / "presets.json"


class _PresetsStore:
    """In-memory cache for presets.json.

    Follows the same pattern as _SettingsStore / _ClientsStore: the
    in-memory dict is the source of truth between save and load.  A
    missing file is treated as an empty dict; a corrupt file is logged
    and treated as empty.
    """

    def __init__(self) -> None:
        self._presets: dict[str, list[list[str]]] | None = None

    def load(self) -> dict[str, list[list[str]]]:
        if self._presets is not None:
            return self._presets
        if _PRESETS_FILE.exists():
            try:
                data = json.loads(_PRESETS_FILE.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("presets.json root must be an object")
                self._presets = data
            except Exception:
                logger.warning("Failed to parse %s, using empty presets", _PRESETS_FILE)
                self._presets = {}
        else:
            self._presets = {}
        return self._presets

    def save(self, presets: dict[str, list[list[str]]]) -> None:
        _PRESETS_FILE.write_text(json.dumps(presets, indent=2), encoding="utf-8")
        _PRESETS_FILE.chmod(0o600)
        self._presets = presets

    def invalidate(self) -> None:
        self._presets = None


_presets_store = _PresetsStore()


def load_presets() -> dict[str, list[list[str]]]:
    return _presets_store.load()


list_presets = load_presets


def save_presets(presets: dict[str, list[list[str]]]) -> None:
    _presets_store.save(presets)


def create_preset(name: str) -> str:
    presets = load_presets()
    if name in presets:
        raise AppError(f'Preset "{name}" already exists.')
    presets[name] = []
    save_presets(presets)
    return f'Created empty preset "{name}".'


def delete_preset(name: str) -> str:
    presets = load_presets()
    if name not in presets:
        raise AppError(f'No such preset "{name}".')
    del presets[name]
    save_presets(presets)
    return f'Deleted preset "{name}".'


def add_to_preset(name: str, client: str, character: str) -> str:
    presets = load_presets()
    if name not in presets:
        raise AppError(f'Preset "{name}" doesn\'t exist.')
    if client.lower() not in CLIENT_KEYS:
        raise AppError(f"Invalid client key: {client}. Available: {', '.join(CLIENT_KEYS)}")
    presets[name].append([client.lower(), character])
    save_presets(presets)
    return f'Added [{client.lower()}, "{character}"] to preset "{name}".'


def remove_from_preset(name: str, index: int) -> str:
    presets = load_presets()
    if name not in presets:
        raise AppError(f'Preset "{name}" doesn\'t exist.')
    count = len(presets[name])
    if index < 1 or index > count:
        noun = "entry" if count == 1 else "entries"
        raise AppError(f'Index {index} out of range. Preset "{name}" has {count} {noun}.')
    removed = presets[name].pop(index - 1)
    save_presets(presets)
    return f'Removed [{removed[0]}, "{removed[1]}"] from preset "{name}".'


def get_preset(name: str) -> list[list[str]]:
    presets = load_presets()
    if name not in presets:
        raise AppError(f'Preset "{name}" doesn\'t exist.')
    return presets[name]
