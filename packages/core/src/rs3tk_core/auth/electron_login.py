"""Electron-based OAuth2 login browser.

Spawns a headless Electron window that navigates to the Jagex OAuth URL,
intercepts the redirect, and returns the authorization code (login) or
ID token (consent) via stdout JSON.

Discovery order:
    script:
        1. installed package: <site-packages>/rs3tk_core/data/electron_login.cjs
        2. dev checkout: <monorepo>/packages/core/src/rs3tk_core/data/electron_login.cjs
        3. user install: ~/.local/share/rs3tk-electron/electron_login/main.cjs
        4. /usr/lib/rs3tk-electron/electron_login/main.cjs
        5. /opt/rs3tk-electron/resources/electron_login/main.cjs
    runtime:
        1. dev checkout: <monorepo>/packages/electron/node_modules/.bin/electron
        2. dev checkout: <monorepo>/node_modules/.bin/electron
        3. system PATH: `which electron`

Raises RuntimeError if neither the Electron runtime nor the login script
can be found on the system.
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

# Resolve paths relative to this file's package.
_CORE_DATA = Path(__file__).resolve().parent.parent / "data"

# Resolve dev-checkout paths relative to the monorepo root (5 levels up
# from this file: auth/ -> rs3tk_core/ -> src/ -> core/ -> packages/ -> root).
_MONOREPO_ROOT = Path(__file__).resolve().parents[5]

_LOGIN_SCRIPT_CANDIDATES: tuple[Path, ...] = (
    _CORE_DATA / "electron_login.cjs",
    _MONOREPO_ROOT / "packages/core/src/rs3tk_core/data/electron_login.cjs",
    Path.home() / ".local/share/rs3tk-electron/electron_login/main.cjs",
    Path("/usr/lib/rs3tk-electron/electron_login/main.cjs"),
    Path("/opt/rs3tk-electron/resources/electron_login/main.cjs"),
)

_USER_DATA_DIR = Path(tempfile.gettempdir()) / f"rs3tk-electron-{os.getuid()}"

_RUNTIME_ERROR = (
    "Electron runtime not found. Electron is required for login.\n"
    "Install Electron globally (npm i -g electron) or run from the dev checkout."
)

_SCRIPT_ERROR = "Electron login script not found. Electron is required for login.\nExpected at one of:\n" + "\n".join(
    f"  {p}" for p in _LOGIN_SCRIPT_CANDIDATES
)


def _find_script() -> Path:
    """Return the path to the headless login script.

    Raises:
        RuntimeError: If the script is not found at any candidate path.
    """
    for candidate in _LOGIN_SCRIPT_CANDIDATES:
        try:
            if candidate.is_file():
                logger.debug("Found login script: %s", candidate)
                return candidate
        except OSError:
            continue
    raise RuntimeError(_SCRIPT_ERROR)


def _find_runtime() -> list[str]:
    """Return a command to spawn Electron.

    Raises:
        RuntimeError: If Electron is not found on the system.
    """
    dev_candidates = [
        _MONOREPO_ROOT / "node_modules/.bin/electron",
        _MONOREPO_ROOT / "packages/electron/node_modules/.bin/electron",
    ]
    for dev in dev_candidates:
        try:
            if dev.is_file():
                logger.debug("Found Electron dev binary: %s", dev)
                return [str(dev.resolve())]
        except OSError:
            pass

    try:
        r = subprocess.run(["which", "electron"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            logger.debug("Found Electron on PATH: %s", r.stdout.strip())
            return [r.stdout.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise RuntimeError(_RUNTIME_ERROR)


def _drain_stderr(proc: subprocess.Popen[bytes], output: list[str]) -> None:
    """Read stderr in a background thread to prevent pipe deadlock."""
    assert proc.stderr is not None
    chunks: list[str] = []
    while True:
        chunk = proc.stderr.read(4096)
        if not chunk:
            break
        chunks.append(chunk)
    output.append("".join(chunks))


def _run_electron(script: Path, url: str, redirect_host: str) -> dict[str, str | None]:
    """Spawn Electron with the login script and return the parsed JSON result.

    The Electron process is given three positional arguments after the script
    path: the OAuth URL, the expected redirect hostname, and a temporary
    user-data directory. It outputs a single JSON line to stdout with the
    result (code/state for login, id_token/state for consent).

    Raises:
        RuntimeError: If Electron exits with a non-zero code or produces no output.
    """
    _USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    runtime = _find_runtime()

    proc = subprocess.Popen(
        [*runtime, "--no-sandbox", "--no-zygote", str(script), url, redirect_host, str(_USER_DATA_DIR)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

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
        raise RuntimeError(f"Electron login failed (exit code {proc.returncode}).\n{stderr_output.strip()}")

    if stderr_output:
        logger.debug("Electron stderr: %s", stderr_output.strip())

    return result


def open_login_browser(url: str) -> tuple[str, str]:
    """Open an Electron browser window for OAuth2 login.

    Navigates to the Jagex authorization URL and intercepts the redirect
    to ``secure.runescape.com`` to extract the authorization code and state.

    Args:
        url: The full OAuth2 authorization URL to open.

    Returns:
        Tuple of (authorization_code, state).

    Raises:
        RuntimeError: If Electron is not found or the login fails.
    """
    script = _find_script()
    result = _run_electron(script, url, "secure.runescape.com")
    code = result.get("code")
    state = result.get("state")
    if not code or not state:
        raise RuntimeError("Login failed — no authorization code received from Electron.")
    return code, state


def open_consent_browser(url: str) -> tuple[str, str]:
    """Open an Electron browser window for OAuth2 consent.

    Navigates to the Jagex consent URL and intercepts the redirect to
    ``localhost`` to extract the ID token and state from the URL fragment.

    Args:
        url: The full OAuth2 consent URL to open.

    Returns:
        Tuple of (id_token, state).

    Raises:
        RuntimeError: If Electron is not found or the consent fails.
    """
    script = _find_script()
    result = _run_electron(script, url, "localhost")
    id_token = result.get("id_token")
    state = result.get("state")
    if not id_token or not state:
        raise RuntimeError("Consent failed — no ID token received from Electron.")
    return id_token, state
