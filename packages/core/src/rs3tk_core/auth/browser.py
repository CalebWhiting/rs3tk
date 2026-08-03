"""Electron-based browser for OAuth2 login.

The headless Electron script (`main.js`) lives in the electron module
under `packages/electron/src/bridge/electron_login/`. This module is
responsible for finding the script and the Electron runtime on the
user's system, then spawning the script for the OAuth flow.

Discovery order:
    script:
        1. dev checkout: <monorepo>/packages/electron/src/bridge/electron_login/main.cjs
        2. user install: ~/.local/share/rs3tk-electron/electron_login/main.cjs
        3. /usr/lib/rs3tk-electron/electron_login/main.cjs
        4. /opt/rs3tk-electron/resources/electron_login/main.cjs
    runtime:
        1. dev checkout: <monorepo>/node_modules/.bin/electron
        2. system PATH: `which electron`
        3. npm-global: `npx electron` (works when global bin isn't on PATH)
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve dev-checkout paths relative to the monorepo root (5 levels up
# from this file: auth/ -> rs3tk_core/ -> src/ -> core/ -> packages/ -> root).
_MONOREPO_ROOT = Path(__file__).resolve().parents[5]

_LOGIN_SCRIPT_CANDIDATES: tuple[Path, ...] = (
    _MONOREPO_ROOT / "packages/electron/src/bridge/electron_login/main.cjs",
    Path.home() / ".local/share/rs3tk-electron/electron_login/main.cjs",
    Path("/usr/lib/rs3tk-electron/electron_login/main.cjs"),
    Path("/opt/rs3tk-electron/resources/electron_login/main.cjs"),
)


def find_electron_login_script() -> Path | None:
    """Return the path to the headless login script, or None if not found."""
    for c in _LOGIN_SCRIPT_CANDIDATES:
        try:
            if c.is_file():
                return c
        except OSError:
            continue
    return None


def find_electron_runtime() -> list[str] | None:
    """Return a command to spawn Electron, or None if not available."""
    dev = _MONOREPO_ROOT / "node_modules/.bin/electron"
    try:
        if dev.is_file():
            return [str(dev.resolve())]
    except OSError:
        pass

    try:
        r = subprocess.run(["which", "electron"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return [r.stdout.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        r = subprocess.run(["which", "npx"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return [r.stdout.strip(), "electron"]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


_USER_DATA_DIR = Path(tempfile.gettempdir()) / f"rs3tk-electron-{os.getuid()}"


def _drain_stderr(proc: subprocess.Popen[bytes], output: list[str]) -> None:  # type: ignore[type-arg]
    """Read stderr in a background thread to prevent pipe deadlock."""
    assert proc.stderr is not None
    chunks: list[str] = []
    while True:
        chunk = proc.stderr.read(4096)
        if not chunk:
            break
        chunks.append(chunk)
    output.append("".join(chunks))


def _run_electron(runtime: list[str], script: Path, url: str, redirect_host: str) -> dict[str, str | None]:
    _USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [*runtime, "--no-sandbox", str(script), url, redirect_host, str(_USER_DATA_DIR)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Drain stderr in a background thread to prevent pipe buffer deadlock.
    # Electron emits many GPU/fontconfig warnings that fill the 64KB pipe
    # buffer, blocking the child from writing anything to stdout.
    stderr_chunks: list[str] = []
    stderr_thread = threading.Thread(target=_drain_stderr, args=(proc, stderr_chunks), daemon=True)
    stderr_thread.start()

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
                    logger.debug("Electron stdout (non-JSON): %s", line)
                    continue
    finally:
        if proc.stdout is not None:
            proc.stdout.close()

    try:
        proc.wait(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    stderr_thread.join(timeout=5)
    stderr_output = stderr_chunks[0] if stderr_chunks else ""

    if not result and proc.returncode != 0:
        raise RuntimeError(f"Electron login failed (exit code {proc.returncode}).\nstderr: {stderr_output.strip()}")

    if stderr_output:
        logger.debug("Electron stderr: %s", stderr_output.strip())

    return result


def open_login_browser(runtime: list[str], script: Path, url: str) -> tuple[str | None, str | None]:
    result = _run_electron(runtime, script, url, "secure.runescape.com")
    return result.get("code"), result.get("state")


def open_consent_browser(runtime: list[str], script: Path, url: str) -> tuple[str | None, str | None]:
    result = _run_electron(runtime, script, url, "localhost")
    return result.get("id_token"), result.get("state")
