"""Test backend.py — HTTP server backing the Electron GUI."""

from __future__ import annotations

import json
import socket
import threading
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rs3tk import backend as backend_module
from rs3tk.app import AppError
from rs3tk.backend import ReusableHTTPServer, main

# ── helpers ─────────────────────────────────────────────────────────────────


def _free_port() -> int:
    """Find a free port by binding to 0 and asking the OS."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def server_url() -> str:
    """Start the server on a free port; tear it down after the test."""
    port = _free_port()
    server = ReusableHTTPServer(("127.0.0.1", port), backend_module.RS3TKHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _get(url: str, path: str) -> tuple[int, dict[str, str] | str]:
    parsed = url.replace("http://", "").split(":", 1)
    host = parsed[0]
    port = int(parsed[1])
    conn = HTTPConnection(host, port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read()
    try:
        return resp.status, json.loads(body) if body else {}
    except json.JSONDecodeError:
        return resp.status, body.decode("utf-8", errors="replace")


def _post(url: str, path: str, body: dict[str, object] | None = None) -> tuple[int, dict[str, str]]:
    parsed = url.replace("http://", "").split(":", 1)
    host = parsed[0]
    port = int(parsed[1])
    conn = HTTPConnection(host, port, timeout=5)
    data = json.dumps(body or {}).encode("utf-8")
    conn.request("POST", path, body=data, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    raw = resp.read()
    return resp.status, json.loads(raw) if raw else {}


def _options(url: str, path: str) -> int:
    parsed = url.replace("http://", "").split(":", 1)
    host = parsed[0]
    port = int(parsed[1])
    conn = HTTPConnection(host, port, timeout=5)
    conn.request("OPTIONS", path)
    return conn.getresponse().status


# ── /api/status ─────────────────────────────────────────────────────────────


class TestStatus:
    def test_returns_ok(self, server_url: str) -> None:
        status, body = _get(server_url, "/api/status")
        assert status == 200
        assert body == {"status": "ok"}


# ── /api/characters ─────────────────────────────────────────────────────────


class TestCharacters:
    @patch("rs3tk.backend._get_characters_result")
    def test_returns_characters(self, mock_gcr: MagicMock, server_url: str) -> None:
        from rs3tk.app import CharacterInfo, CharactersResult

        result = CharactersResult(
            characters=[CharacterInfo(account_id="a", display_name="Alice", username="u1", is_member=True)],
            auth_errors=[],
        )
        mock_gcr.return_value = result

        status, body = _get(server_url, "/api/characters")
        assert status == 200
        assert body == {
            "characters": [{"display_name": "Alice", "username": "u1", "is_member": True}],
            "auth_errors": [],
        }


# ── /api/accounts ───────────────────────────────────────────────────────────


class TestAccounts:
    @patch("rs3tk.backend.list_accounts")
    def test_returns_accounts(self, mock_la: MagicMock, server_url: str) -> None:
        from rs3tk.config import AccountInfo

        mock_la.return_value = [
            AccountInfo(username="alice", display_name="Ali", email="a@example.com"),
            AccountInfo(username="bob", display_name=None, email=""),
        ]

        status, body = _get(server_url, "/api/accounts")
        assert status == 200
        assert body == [
            {"username": "alice", "display_name": "Ali", "email": "a@example.com"},
            {"username": "bob", "display_name": None, "email": ""},
        ]


# ── /api/clients ────────────────────────────────────────────────────────────


class TestClients:
    @patch("rs3tk.backend.get_client_info")
    def test_returns_clients(self, mock_gci: MagicMock, server_url: str) -> None:
        c1 = MagicMock()
        c1.key = "runelite"
        c1.name = "RuneLite"
        c2 = MagicMock()
        c2.key = "hdos"
        c2.name = "HDOS"
        mock_gci.return_value = [(c1, True, "/usr/bin/runelite"), (c2, False, None)]

        status, body = _get(server_url, "/api/clients")
        assert status == 200
        assert body == [
            {"key": "runelite", "name": "RuneLite", "installed": True},
            {"key": "hdos", "name": "HDOS", "installed": False},
        ]


# ── /api/metrics/{name} ─────────────────────────────────────────────────────


class TestMetrics:
    @patch("rs3tk.backend.run_sync")
    def test_returns_metrics(self, mock_run: MagicMock, server_url: str) -> None:
        from rs3tk.rs_api import RuneMetricsProfile

        # Use model_validate with the camelCase keys the API would send, since
        # the model's before-validator expects the raw API shape.
        profile = RuneMetricsProfile.model_validate({"name": "Alice", "combatlevel": 100, "totalxp": 1000})
        mock_run.return_value = profile

        status, body = _get(server_url, "/api/metrics/Alice")
        assert status == 200
        assert body["name"] == "Alice"
        assert body["combat_level"] == 100
        assert body["total_xp"] == 1000


# ── /api/avatar/{name} ──────────────────────────────────────────────────────


class TestAvatar:
    @patch("rs3tk.backend.config_dir")
    def test_missing_avatar_returns_404(self, mock_cd: MagicMock, tmp_path: Path, server_url: str) -> None:
        mock_cd.return_value = tmp_path
        # No cache file exists -> 404 with empty body
        status, body = _get(server_url, "/api/avatar/MissingUser")
        assert status == 404
        # The 404 path in the handler doesn't write a JSON body
        assert body == {}

    @patch("rs3tk.backend.config_dir")
    def test_present_avatar_returns_200(self, mock_cd: MagicMock, tmp_path: Path, server_url: str) -> None:
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "avatar_Alice.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        mock_cd.return_value = tmp_path

        parsed = server_url.replace("http://", "").split(":", 1)
        host = parsed[0]
        port = int(parsed[1])
        conn = HTTPConnection(host, port, timeout=5)
        conn.request("GET", "/api/avatar/Alice")
        resp = conn.getresponse()
        body = resp.read()

        assert resp.status == 200
        assert resp.getheader("Content-Type") == "image/png"
        assert body == b"\x89PNG\r\n\x1a\n"

    def test_unsafe_name_sanitized(self, server_url: str) -> None:
        # Slashes in the name get replaced with underscores, so 404
        status, _ = _get(server_url, "/api/avatar/../etc/passwd")
        # Depending on URL parsing, may be 404 or 400. Just ensure no crash.
        assert status in (400, 404)


# ── POST /api/launch ────────────────────────────────────────────────────────


class TestLaunch:
    @patch("rs3tk.backend.launch_game")
    def test_no_character_returns_error(self, mock_lg: MagicMock, server_url: str) -> None:
        status, body = _post(server_url, "/api/launch", {"client_key": "runelite"})
        assert status == 200
        assert "error" in body
        mock_lg.assert_not_called()

    @patch("rs3tk.backend.launch_game")
    def test_with_character_invokes(self, mock_lg: MagicMock, server_url: str) -> None:
        status, body = _post(server_url, "/api/launch", {"client_key": "runelite", "character": "Alice"})
        assert status == 200
        assert body == {"status": "launched"}
        mock_lg.assert_called_once_with("runelite", "Alice")


# ── POST /api/login ─────────────────────────────────────────────────────────


class TestLogin:
    @patch("rs3tk.backend.do_login")
    def test_returns_username_and_count(self, mock_do: MagicMock, server_url: str) -> None:
        mock_do.return_value = ("alice", 2)

        status, body = _post(server_url, "/api/login", {"system_browser": False})
        assert status == 200
        assert body == {"username": "alice", "account_count": 2}
        mock_do.assert_called_once_with(system_browser=False)

    @patch("rs3tk.backend.do_login")
    def test_passes_system_browser(self, mock_do: MagicMock, server_url: str) -> None:
        mock_do.return_value = ("bob", 1)

        status, body = _post(server_url, "/api/login", {"system_browser": True})
        assert status == 200
        mock_do.assert_called_once_with(system_browser=True)


# ── POST /api/logout ────────────────────────────────────────────────────────


class TestLogout:
    @patch("rs3tk.backend.do_logout")
    def test_returns_status(self, mock_do: MagicMock, server_url: str) -> None:
        status, body = _post(server_url, "/api/logout", {"username": "alice", "all": False})
        assert status == 200
        assert body == {"status": "logged_out"}
        mock_do.assert_called_once_with(username="alice", all_accounts=False)

    @patch("rs3tk.backend.do_logout")
    def test_exception_returns_error(self, mock_do: MagicMock, server_url: str) -> None:
        mock_do.side_effect = AppError("oops")

        status, body = _post(server_url, "/api/logout", {})
        assert status == 200
        assert body == {"error": "oops"}


# ── POST /api/install ───────────────────────────────────────────────────────


class TestInstall:
    @patch("rs3tk.backend.do_autoinstall")
    def test_no_client_returns_error(self, mock_do: MagicMock, server_url: str) -> None:
        status, body = _post(server_url, "/api/install", {})
        assert status == 200
        assert body == {"error": "No client_key provided"}
        mock_do.assert_not_called()

    @patch("rs3tk.backend.do_autoinstall")
    def test_invokes(self, mock_do: MagicMock, server_url: str) -> None:
        mock_do.return_value = "Installed runelite"

        status, body = _post(server_url, "/api/install", {"client_key": "runelite"})
        assert status == 200
        assert body == {"status": "installed", "message": "Installed runelite"}
        mock_do.assert_called_once_with("runelite")

    @patch("rs3tk.backend.do_autoinstall")
    def test_exception_returns_error(self, mock_do: MagicMock, server_url: str) -> None:
        mock_do.side_effect = AppError("deps missing")

        status, body = _post(server_url, "/api/install", {"client_key": "runelite"})
        assert status == 200
        assert body == {"error": "deps missing"}


# ── error / 404 paths ──────────────────────────────────────────────────────


class TestErrors:
    def test_unknown_get_route_returns_404(self, server_url: str) -> None:
        status, body = _get(server_url, "/api/nope")
        assert status == 404
        assert body == {"error": "Not found"}

    def test_unknown_post_route_returns_404(self, server_url: str) -> None:
        status, body = _post(server_url, "/api/nope", {})
        assert status == 404
        assert body == {"error": "Not found"}

    @patch("rs3tk.backend._get_characters_result", side_effect=Exception("boom"))
    def test_unhandled_exception_returns_500(self, _mock: MagicMock, server_url: str) -> None:
        status, body = _get(server_url, "/api/characters")
        assert status == 500
        assert body == {"error": "boom"}


# ── CORS / OPTIONS ──────────────────────────────────────────────────────────


class TestCors:
    def test_options_preflight(self, server_url: str) -> None:
        status = _options(server_url, "/api/anything")
        assert status == 200

    def test_response_has_cors_header(self, server_url: str) -> None:
        parsed = server_url.replace("http://", "").split(":", 1)
        host = parsed[0]
        port = int(parsed[1])
        conn = HTTPConnection(host, port, timeout=5)
        conn.request("GET", "/api/status")
        resp = conn.getresponse()
        resp.read()
        assert resp.getheader("Access-Control-Allow-Origin") == "*"


# ── large body protection ───────────────────────────────────────────────────


class TestBodySize:
    def test_oversized_body_rejected(self, server_url: str) -> None:
        parsed = server_url.replace("http://", "").split(":", 1)
        host = parsed[0]
        port = int(parsed[1])
        conn = HTTPConnection(host, port, timeout=5)
        large = b"x" * (1_048_577)  # 1 byte over the limit
        conn.request("POST", "/api/login", body=large, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        body = json.loads(resp.read())
        assert resp.status == 413
        assert "too large" in body["error"].lower()


# ── main entry point ────────────────────────────────────────────────────────


class TestMainEntry:
    @patch("rs3tk.backend.ReusableHTTPServer")
    def test_uses_default_port(self, mock_server_cls: MagicMock) -> None:
        with patch("rs3tk.backend.sys") as mock_sys:
            mock_sys.argv = ["rs3tk-backend"]
            main()
        mock_server_cls.assert_called_once()
        args = mock_server_cls.call_args.args
        assert args[0] == ("127.0.0.1", 8765)

    @patch("rs3tk.backend.ReusableHTTPServer")
    def test_uses_custom_port(self, mock_server_cls: MagicMock) -> None:
        with patch("rs3tk.backend.sys") as mock_sys:
            mock_sys.argv = ["rs3tk-backend", "9999"]
            main()
        args = mock_server_cls.call_args.args
        assert args[0] == ("127.0.0.1", 9999)

    @patch("rs3tk.backend.ReusableHTTPServer")
    def test_prints_startup_message(self, mock_server_cls: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        server = MagicMock()
        mock_server_cls.return_value = server

        with patch("rs3tk.backend.sys") as mock_sys:
            mock_sys.argv = ["rs3tk-backend"]
            main()

        captured = capsys.readouterr()
        assert "RS3TK backend running" in captured.out
