"""Python backend server for electron GUI."""

from __future__ import annotations

import contextlib
import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import unquote, urlparse

from rs3tk.app import (
    _get_characters_result,
    do_autoinstall,
    do_login,
    do_logout,
    get_client_info,
    launch_game,
    list_accounts,
    run_sync,
)
from rs3tk.config import config_dir
from rs3tk.rs_api import get_rune_metrics


class RS3TKHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/characters":
                data: dict[str, Any] | list[dict[str, Any]] = self._get_characters()
            elif path == "/api/accounts":
                data = self._get_accounts()
            elif path == "/api/clients":
                data = self._get_clients()
            elif path.startswith("/api/metrics/"):
                name = unquote(path.split("/api/metrics/", 1)[1])
                data = self._get_metrics(name)
            elif path == "/api/status":
                data = {"status": "ok"}
            elif path.startswith("/api/avatar/"):
                name = unquote(path.split("/api/avatar/", 1)[1])
                self._serve_avatar(name)
                return
            else:
                self._json_response(404, {"error": "Not found"})
                return

            self._json_response(200, data)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 1_048_576:
            self._json_response(413, {"error": "Request body too large"})
            return
        body: dict[str, Any] = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        try:
            if path == "/api/launch":
                data = self._launch_game(body)
            elif path == "/api/login":
                data = self._login(body)
            elif path == "/api/logout":
                data = self._logout(body)
            elif path == "/api/install":
                data = self._install_client(body)
            else:
                self._json_response(404, {"error": "Not found"})
                return

            self._json_response(200, data)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _json_response(self, code: int, data: dict[str, Any] | list[dict[str, Any]]) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _get_characters(self) -> dict[str, Any]:
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
            "auth_errors": result.auth_errors,
        }

    def _get_accounts(self) -> list[dict[str, Any]]:
        accounts = list_accounts()
        return [
            {
                "username": a.username,
                "display_name": a.display_name,
                "email": a.email or "",
            }
            for a in accounts
        ]

    def _get_clients(self) -> list[dict[str, Any]]:
        clients = get_client_info()
        return [
            {
                "key": c.key,
                "name": c.name,
                "installed": installed,
            }
            for c, installed, _ in clients
        ]

    def _get_metrics(self, name: str) -> dict[str, Any]:
        profile = run_sync(get_rune_metrics(name, 10))
        return profile.model_dump()

    def _serve_avatar(self, name: str) -> None:
        # TODO: the avatar cache is never populated — this endpoint always 404s
        # until a download path is added (e.g., re-introduce get_player_avatar
        # in rs_api.py and write the fetched PNG into config_dir()/cache/).
        safe = name.replace("/", "_").replace("\\", "_")
        avatar_path = config_dir() / "cache" / f"avatar_{safe}.png"
        if avatar_path.exists():
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            with open(avatar_path, "rb") as f:
                while chunk := f.read(8192):
                    self.wfile.write(chunk)
        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

    def _launch_game(self, body: dict[str, Any]) -> dict[str, str]:
        client_key = body.get("client_key", "official")
        character = body.get("character")
        if not character:
            return {"error": "No character specified"}
        launch_game(client_key, character)
        return {"status": "launched"}

    def _login(self, body: dict[str, Any]) -> dict[str, Any]:
        system_browser = body.get("system_browser", False)
        username, count = do_login(system_browser=system_browser)
        return {"username": username, "account_count": count}

    def _logout(self, body: dict[str, Any]) -> dict[str, str]:
        username = body.get("username")
        all_accounts = body.get("all", False)
        try:
            do_logout(username=username, all_accounts=all_accounts)
            return {"status": "logged_out"}
        except Exception as e:
            return {"error": str(e)}

    def _install_client(self, body: dict[str, Any]) -> dict[str, str]:
        client_key = body.get("client_key")
        if not client_key:
            return {"error": "No client_key provided"}
        try:
            result = do_autoinstall(client_key)
            return {"status": "installed", "message": result}
        except Exception as e:
            return {"error": str(e)}

    def log_message(self, fmt: str, *args: object) -> None:
        if args:
            print(f"[backend] {fmt % args}")


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def server_bind(self) -> None:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with contextlib.suppress(AttributeError, OSError):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        super().server_bind()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ReusableHTTPServer(("127.0.0.1", port), RS3TKHandler)
    print(f"RS3TK backend running on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
