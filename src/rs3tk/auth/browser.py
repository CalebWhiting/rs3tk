"""Electron-based browser for OAuth2 login."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

_ELECTRON_DIR = Path(__file__).parent / "electron"
_MAIN_JS = _ELECTRON_DIR / "main.js"
_USER_DATA_DIR = Path(tempfile.gettempdir()) / f"rs3tk-electron-{os.getuid()}"


def _find_electron() -> list[str]:
    node_modules = Path(__file__).parent.parent.parent.parent / "node_modules" / ".bin" / "electron"
    if node_modules.exists():
        return [str(node_modules)]

    result = subprocess.run(
        ["which", "electron"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode == 0:
        return [result.stdout.strip()]

    return ["npx", "electron"]


def _run_electron(url: str, redirect_host: str) -> dict[str, str | None]:
    electron = _find_electron()
    _USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [*electron, str(_MAIN_JS), url, redirect_host, str(_USER_DATA_DIR)],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    result: dict[str, str | None] = {}
    try:
        if proc.stdout is not None:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    result = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
    finally:
        if proc.stdout is not None:
            proc.stdout.close()

    try:
        proc.wait(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    return result


def open_login_browser(url: str) -> tuple[str | None, str | None]:
    result = _run_electron(url, "secure.runescape.com")
    return result.get("code"), result.get("state")


def open_consent_browser(url: str) -> tuple[str | None, str | None]:
    result = _run_electron(url, "localhost")
    return result.get("id_token"), result.get("state")
