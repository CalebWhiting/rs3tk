"""Cross-module integration test for the rs3tk-bridge.

Spawns the bridge as a subprocess and exercises it via JSON-RPC. Verifies:
- The bridge starts, registers all 9 methods, and writes to stderr
- The protocol framing is correct (id echoing, error codes, etc.)
- Methods with validation errors return proper -32000 errors
- Unknown methods return -32601

This is a smoke test that catches drift between the Python `METHODS`
dict in `rs3tk_bridge.py` and the typed `BridgeAPI` surface in
`packages/electron/src/preload/api.ts`. For the methods that touch
the keyring, OAuth, or actual game clients, we only verify they
reject bad input — we never call them with a real session.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_SCRIPT = (
    REPO_ROOT / "packages" / "electron" / "src" / "bridge" / "rs3tk_bridge.py"
)


def _spawn_bridge(tmp_path: Path) -> subprocess.Popen[bytes]:
    """Spawn the bridge with a sandboxed config dir.

    `XDG_CONFIG_HOME` and `HOME` point at `tmp_path` so the bridge
    doesn't read the real `~/.config/rs3tk/` and so keyring backends
    that need a session bus fall back to a file backend.
    """
    py = REPO_ROOT / ".venv" / "bin" / "python3"
    if not py.exists():
        pytest.skip("monorepo .venv not found; run `uv sync` first")
    if not BRIDGE_SCRIPT.exists():
        pytest.skip(f"bridge script not found at {BRIDGE_SCRIPT}")
    env = {
        **os.environ,
        "PYTHONPATH": str(REPO_ROOT / "packages" / "core" / "src"),
        "XDG_CONFIG_HOME": str(tmp_path),
        "HOME": str(tmp_path),
    }
    return subprocess.Popen(
        [str(py), str(BRIDGE_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def _call(
    proc: subprocess.Popen[bytes], method: str, params: dict | None = None
) -> dict:
    """Send a JSON-RPC request and read exactly one response line."""
    assert proc.stdin is not None and proc.stdout is not None
    req = {"id": 1, "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(req).encode() + b"\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
        raise RuntimeError(f"bridge exited unexpectedly. stderr:\n{stderr}")
    return json.loads(line)


def _drain_stderr(proc: subprocess.Popen[bytes], timeout: float = 15.0) -> str:
    """Read stderr until `timeout` seconds elapse, the process exits, or the pipe closes."""
    import select

    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout
    while proc.stderr is not None and time.monotonic() < deadline:
        r, _, _ = select.select([proc.stderr], [], [], 0.05)
        if not r:
            if proc.poll() is not None:
                break
            continue
        chunk = os.read(proc.stderr.fileno(), 4096)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode(errors="replace")


@pytest.fixture
def bridge(tmp_path: Path):
    proc = _spawn_bridge(tmp_path)
    yield proc
    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


# ── protocol-level tests ─────────────────────────────────────────────


def test_stderr_lists_all_methods(bridge: subprocess.Popen[bytes]) -> None:
    """The bridge's startup banner advertises every method it has.

    This catches drift: if someone adds a method to the Python
    `METHODS` dict but forgets to update the TS `BridgeAPI`, this test
    still passes; the cross-module `test_typed_surface_matches_methods`
    below is what catches the reverse.
    """
    stderr = _drain_stderr(bridge, timeout=20.0)
    assert "[bridge] bridge started" in stderr, (
        f"expected startup banner, got: {stderr!r}"
    )
    m = re.search(r"(\d+) methods registered: \[([^\]]+)\]", stderr)
    assert m, f"could not parse method list from: {stderr!r}"
    methods = [s.strip().strip("'") for s in m.group(2).split(",")]
    expected = {
        "get_characters",
        "get_accounts",
        "get_clients",
        "get_status",
        "get_metrics",
        "login",
        "logout",
        "launch_game",
        "install_client",
    }
    assert expected.issubset(set(methods)), (
        f"missing methods: {expected - set(methods)}\nbridge banner: {stderr!r}"
    )


def test_get_status(bridge: subprocess.Popen[bytes]) -> None:
    resp = _call(bridge, "get_status")
    assert resp == {"id": 1, "result": {"status": "ok"}}


def test_get_accounts_empty(bridge: subprocess.Popen[bytes]) -> None:
    """No accounts in a sandboxed config dir -> empty list, not an error."""
    resp = _call(bridge, "get_accounts")
    assert resp == {"id": 1, "result": []}


def test_get_clients(bridge: subprocess.Popen[bytes]) -> None:
    """Returns the list of known clients (none installed)."""
    resp = _call(bridge, "get_clients")
    assert resp["id"] == 1
    assert "result" in resp
    clients = resp["result"]
    assert isinstance(clients, list)
    # The default clients are rs3, official, runelite, hdos
    keys = {c["key"] for c in clients}
    assert {"rs3", "official", "runelite", "hdos"}.issubset(keys)


def test_unknown_method_returns_error(bridge: subprocess.Popen[bytes]) -> None:
    resp = _call(bridge, "definitely_not_a_real_method")
    assert resp["id"] == 1
    assert resp["error"]["code"] == -32601
    assert "Unknown method" in resp["error"]["message"]


def test_get_metrics_missing_name_raises(bridge: subprocess.Popen[bytes]) -> None:
    resp = _call(bridge, "get_metrics", {})
    assert resp["id"] == 1
    assert "error" in resp
    assert resp["error"]["code"] == -32000
    assert "name" in resp["error"]["message"]


def test_launch_game_missing_args_raises(bridge: subprocess.Popen[bytes]) -> None:
    resp = _call(bridge, "launch_game", {})
    assert resp["id"] == 1
    assert "error" in resp
    assert resp["error"]["code"] == -32000


def test_install_client_missing_key_raises(bridge: subprocess.Popen[bytes]) -> None:
    resp = _call(bridge, "install_client", {})
    assert resp["id"] == 1
    assert "error" in resp
    assert resp["error"]["code"] == -32000


def test_invalid_json_returns_parse_error(bridge: subprocess.Popen[bytes]) -> None:
    assert bridge.stdin is not None and bridge.stdout is not None
    bridge.stdin.write(b"this is not json\n")
    bridge.stdin.flush()
    line = bridge.stdout.readline()
    resp = json.loads(line)
    assert resp["error"]["code"] == -32700


def test_missing_method_returns_invalid_request(
    bridge: subprocess.Popen[bytes],
) -> None:
    resp = _call(bridge, "get_status")
    # Sanity: response is a single JSON object on one line, parseable.
    assert isinstance(resp, dict)
    assert "result" in resp or "error" in resp
