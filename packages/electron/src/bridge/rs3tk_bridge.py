"""stdio JSON-RPC bridge between the Electron app and rs3tk-core.

Spawned by the Electron main process as a child process. Reads
JSON-RPC 2.0 requests from stdin, writes responses to stdout, logs to
stderr. The METHODS table is the only place that maps RPC method names
to calls into rs3tk_core.app. Adding a new method = adding one entry.

Protocol:
    Request:    {"id": <int>, "method": <str>, "params": <obj>}
    Response:   {"id": <int>, "result": <any>}
    Error:      {"id": <int|null>, "error": {"code": <int>, "message": <str>}}
    Notification (one-way): {"method": <str>, "params": <obj>}
"""
from __future__ import annotations

import json
import sys
from typing import Any, Callable

METHODS: dict[str, Callable[[dict[str, Any]], Any]] = {}


def method(name: str) -> Callable[[Callable[[dict[str, Any]], Any]], Callable[[dict[str, Any]], Any]]:
    def decorator(fn: Callable[[dict[str, Any]], Any]) -> Callable[[dict[str, Any]], Any]:
        METHODS[name] = fn
        return fn

    return decorator


def _send(msg: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg, default=str) + "\n")
    sys.stdout.flush()


def _log(msg: str) -> None:
    sys.stderr.write(f"[bridge] {msg}\n")
    sys.stderr.flush()


# ── handlers ─────────────────────────────────────────────────────────


@method("get_characters")
def _get_characters(_params: dict[str, Any]) -> dict[str, Any]:
    from rs3tk_core.app import _get_characters_result

    result = _get_characters_result()
    return {
        "characters": [
            {
                "display_name": c.display_name,
                "username": c.username,
                "is_member": c.is_member,
            }
            for c in result.characters
        ],
        "auth_errors": list(result.auth_errors),
    }


@method("get_accounts")
def _get_accounts(_params: dict[str, Any]) -> list[dict[str, Any]]:
    from rs3tk_core.app import list_accounts

    return [
        {
            "username": a.username,
            "display_name": a.display_name,
            "email": a.email or "",
        }
        for a in list_accounts()
    ]


@method("get_clients")
def _get_clients(_params: dict[str, Any]) -> list[dict[str, Any]]:
    from rs3tk_core.app import get_client_info

    return [
        {
            "key": c.key,
            "name": c.name,
            "installed": installed,
        }
        for c, installed, _ in get_client_info()
    ]


@method("get_status")
def _get_status(_params: dict[str, Any]) -> dict[str, str]:
    return {"status": "ok"}


@method("get_metrics")
def _get_metrics(params: dict[str, Any]) -> dict[str, Any]:
    from rs3tk_core.app import run_sync
    from rs3tk_core.rs_api import get_rune_metrics

    name = params.get("name")
    if not name:
        raise ValueError("name is required")
    return run_sync(get_rune_metrics(name, 10)).model_dump()


@method("login")
def _login(params: dict[str, Any]) -> dict[str, Any]:
    from rs3tk_core.app import do_login

    username, count = do_login(system_browser=bool(params.get("system_browser", False)))
    return {"username": username, "account_count": count}


@method("logout")
def _logout(params: dict[str, Any]) -> dict[str, str]:
    from rs3tk_core.app import do_logout

    do_logout(params.get("username"), all_accounts=bool(params.get("all", False)))
    return {"status": "logged_out"}


@method("launch_game")
def _launch(params: dict[str, Any]) -> dict[str, str]:
    from rs3tk_core.app import launch_game

    client_key = params.get("client_key")
    character = params.get("character")
    if not client_key:
        raise ValueError("client_key is required")
    if not character:
        raise ValueError("character is required")
    launch_game(client_key, character)
    return {"status": "launched"}


@method("install_client")
def _install(params: dict[str, Any]) -> dict[str, str]:
    from rs3tk_core.app import do_autoinstall

    client_key = params.get("client_key")
    if not client_key:
        raise ValueError("client_key is required")
    return {"status": "installed", "message": do_autoinstall(client_key)}


# ── dispatcher ──────────────────────────────────────────────────────


def _dispatch(req: dict[str, Any]) -> tuple[int | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Return (id, result, error) for a request."""
    request_id: int | None = req.get("id")
    name = req.get("method")
    params = req.get("params") or {}

    if not isinstance(name, str):
        return request_id, None, {"code": -32600, "message": "method must be a string"}

    handler = METHODS.get(name)
    if handler is None:
        return request_id, None, {"code": -32601, "message": f"Unknown method: {name}"}

    try:
        result = handler(params)
    except Exception as e:
        return request_id, None, {"code": -32000, "message": str(e)}
    return request_id, result, None


def main() -> None:
    _log(f"bridge started, {len(METHODS)} methods registered: {sorted(METHODS)}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            _send({"id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}})
            continue

        if "method" not in req:
            _send({"id": req.get("id"), "error": {"code": -32600, "message": "missing method"}})
            continue

        request_id, result, error = _dispatch(req)
        if error is not None:
            _send({"id": request_id, "error": error})
        elif request_id is not None:
            _send({"id": request_id, "result": result})
        # else: one-way notification, no response


if __name__ == "__main__":
    main()
