"""Game client launchers — config-driven."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import TypedDict

from rs3tk.config import config_dir

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


class GameClient:
    __slots__ = ("key", "name", "args", "bin_names", "_paths", "env")

    def __init__(self) -> None:
        self.key = ""
        self.name = "Unknown"
        self.args: list[str] | None = None
        self.bin_names: list[str] | None = None
        self._paths: list[Path] | None = None
        self.env: dict[str, str] | None = None

    def executable(self) -> Path | None:
        if self.key:
            install_dir = CLIENTS_DIR / self.key
            if install_dir.is_dir():
                for f in sorted(install_dir.iterdir()):
                    if f.is_file() and os.access(f, os.X_OK):
                        return f
        for name in self.bin_names or []:
            found = shutil.which(name)
            if found:
                return Path(found)
        for p in self._paths or []:
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
            cmd = ["wine", str(exe), *(self.args or [])]
        elif exe.suffix == ".jar":
            java = shutil.which("java")
            if not java:
                raise FileNotFoundError("Java is required to run HDOS but was not found in PATH")
            cmd = [java, "-jar", str(exe), *(self.args or [])]
        else:
            cmd = [str(exe), *(self.args or [])]
        logger.info("Launching %s: %s", self.name, " ".join(cmd))

        env = os.environ.copy()
        env.update(self.env or {})
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


class ConfigClient(GameClient):
    def __init__(self, key: str, cfg: ClientSpec) -> None:
        self.key = key
        self.name = cfg.get("name", "Unknown")
        self.args = cfg.get("args", [])
        self.bin_names = cfg.get("bin_names", [])
        self._paths = [Path(p).expanduser() for p in cfg.get("paths", [])]
        raw_env = cfg.get("env")
        if raw_env:
            self.env = {k: str(Path(v).expanduser()) if v.startswith("~") else v for k, v in raw_env.items()}
        else:
            self.env = None


def _load_clients_config() -> dict[str, ClientSpec]:
    global _clients_config  # noqa: PLW0603
    if _clients_config is not None:
        return _clients_config
    if not CLIENTS_FILE.exists():
        CLIENTS_FILE.write_text(json.dumps(DEFAULT_CLIENTS, indent=2), encoding="utf-8")
    _clients_config = json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))
    return _clients_config


_clients_config: dict[str, ClientSpec] | None = None


def get_all_clients() -> dict[str, GameClient]:
    cfg = _load_clients_config()
    return {key: ConfigClient(key, val) for key, val in cfg.items()}


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
    global _clients_config  # noqa: PLW0603
    cfg = _load_clients_config()
    if client_key not in cfg:
        cfg[client_key] = ClientSpec(name=client_key.title())
    cfg[client_key].update(kwargs)  # type: ignore[typeddict-item]
    CLIENTS_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    CLIENTS_FILE.chmod(0o600)
    _clients_config = None
