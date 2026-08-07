"""Game client launchers — config-driven."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

from rs3tk_core.config import config_dir

logger = logging.getLogger(__name__)

CLIENTS_FILE = config_dir() / "clients.json"
CLIENTS_DIR = config_dir() / "clients"


class ClientSpec(TypedDict, total=False):
    name: str
    args: list[str]
    bin_names: list[str]
    paths: list[str]
    env: dict[str, str]


DEFAULT_CLIENTS: dict[str, ClientSpec] = {
    "rs3": {
        "name": "RS3",
        "bin_names": ["runescape-launcher", "RuneScape"],
    },
    "official": {
        "name": "OSRS Official",
        "bin_names": ["osclient"],
    },
    "runelite": {
        "name": "RuneLite",
        "bin_names": ["runelite", "RuneLite"],
    },
    "hdos": {
        "name": "HDOS",
        "bin_names": ["hdos", "HDOS"],
    },
}


@dataclass
class GameClient:
    key: str = ""
    name: str = "Unknown"
    args: list[str] = field(default_factory=list)
    bin_names: list[str] = field(default_factory=list)
    paths: list[Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_config(cls, key: str, cfg: ClientSpec) -> GameClient:
        raw_env = cfg.get("env") or {}
        env = {k: str(Path(v).expanduser()) if v.startswith("~") else v for k, v in raw_env.items()}
        return cls(
            key=key,
            name=cfg.get("name", "Unknown"),
            args=list(cfg.get("args", [])),
            bin_names=list(cfg.get("bin_names", [])),
            paths=[Path(p).expanduser() for p in cfg.get("paths", [])],
            env=env,
        )

    def executable(self) -> Path | None:
        if self.key:
            install_dir = CLIENTS_DIR / self.key
            if install_dir.is_dir():
                for f in sorted(install_dir.iterdir()):
                    if f.is_file() and os.access(f, os.X_OK):
                        return f
        for name in self.bin_names:
            found = shutil.which(name)
            if found:
                return Path(found)
        for p in self.paths:
            if p.exists():
                return p
        return None

    def is_installed(self) -> bool:
        return self.executable() is not None

    def launch(
        self,
        session_id: str,
        character_id: str | None = None,
        display_name: str | None = None,
        foreground: bool = False,
    ) -> subprocess.Popen[bytes]:
        exe = self.executable()
        if exe is None:
            raise FileNotFoundError(f"{self.name} client not found.")

        cmd: list[str]
        if exe.suffix == ".exe":
            cmd = ["wine", str(exe), *self.args]
        elif exe.suffix == ".jar":
            java = shutil.which("java")
            if not java:
                raise FileNotFoundError(f"Java is required to run {self.name} but was not found in PATH")
            cmd = [java, "-jar", str(exe), *self.args]
        else:
            cmd = [str(exe), *self.args]
        logger.info("Launching %s: %s", self.name, " ".join(cmd))

        env = os.environ.copy()
        env.update(self.env)
        env["JX_SESSION_ID"] = session_id
        if character_id:
            env["JX_CHARACTER_ID"] = character_id
        if display_name:
            env["JX_DISPLAY_NAME"] = display_name

        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=None if foreground else subprocess.DEVNULL,
                stderr=None if foreground else subprocess.DEVNULL,
            )
            logger.info("Launched %s (PID %d)", self.name, process.pid)
            return process
        except OSError as e:
            raise RuntimeError(f"Failed to launch {self.name}: {e}") from e


class _ClientsStore:
    """In-memory cache for the parsed clients.json config.

    `load()` returns the parsed dict (populating on first call);
    `invalidate()` forces the next call to re-read from disk.
    """

    def __init__(self) -> None:
        self._config: dict[str, ClientSpec] | None = None

    def load(self) -> dict[str, ClientSpec]:
        if self._config is None:
            if not CLIENTS_FILE.exists():
                CLIENTS_FILE.write_text(json.dumps(DEFAULT_CLIENTS, indent=2), encoding="utf-8")
            self._config = json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))
        return self._config

    def invalidate(self) -> None:
        self._config = None


_clients_store = _ClientsStore()


def _load_clients_config() -> dict[str, ClientSpec]:
    return _clients_store.load()


def get_all_clients() -> dict[str, GameClient]:
    cfg = _load_clients_config()
    return {key: GameClient.from_config(key, val) for key, val in cfg.items()}


def get_client_keys() -> list[str]:
    return list(_load_clients_config().keys())


def detect_client(name: str) -> GameClient:
    clients = get_all_clients()
    key = name.lower()
    if key not in clients:
        raise ValueError(f"Unknown client: {name}. Available: {', '.join(clients.keys())}")
    return clients[key]


def update_client_config(client_key: str, **kwargs: object) -> None:
    """Update a client's config in clients.json."""
    cfg = _load_clients_config()
    if client_key not in cfg:
        cfg[client_key] = ClientSpec(name=client_key.title())
    cfg[client_key].update(kwargs)  # type: ignore[typeddict-item]
    CLIENTS_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    CLIENTS_FILE.chmod(0o600)
    _clients_store.invalidate()
