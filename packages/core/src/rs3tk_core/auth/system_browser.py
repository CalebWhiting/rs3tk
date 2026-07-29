"""System browser with manual URL paste for OAuth2 login.

Uses plain `print()` for output so the core has no Rich/UI dependency.
The cli package is the one driving the user-facing flows.
"""

from __future__ import annotations

import webbrowser
from urllib.parse import parse_qs, urlparse


def _log(msg: str = "") -> None:
    print(msg)


def open_login_system(url: str) -> tuple[str | None, str | None]:
    _log()
    _log("[bold cyan]Step 1/2:[/] Login")
    webbrowser.open(url)
    _log("A browser window has opened. Log in to your Jagex Account.")
    _log()
    _log("After logging in, paste the redirect URL below.")
    _log("It will look like:")
    _log("  [dim]https://secure.runescape.com/m=weblogin/launcher-redirect?code=...&state=...[/]")
    _log()

    try:
        user_input = input("Paste URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None, None

    if not user_input:
        return None, None

    parsed = urlparse(user_input)
    if parsed.hostname != "secure.runescape.com":
        _log("[bold red]Error:[/] URL host doesn't match expected (secure.runescape.com)")
        return None, None
    params = parse_qs(parsed.query)
    return params.get("code", [None])[0], params.get("state", [None])[0]


def open_consent_system(url: str) -> tuple[str | None, str | None]:
    _log()
    _log("[bold cyan]Step 2/2:[/] Consent")
    webbrowser.open(url)
    _log("A browser window has opened for consent.")
    _log("It will redirect automatically — no action needed.")
    _log()
    _log("After the redirect, paste the URL below.")
    _log("It will look like:")
    _log("  [dim]http://localhost#id_token=...&state=...[/]")
    _log()

    try:
        user_input = input("Paste URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None, None

    if not user_input:
        return None, None

    parsed = urlparse(user_input)
    if parsed.hostname not in ("localhost", "127.0.0.1"):
        _log("[bold red]Error:[/] URL host doesn't match expected (localhost)")
        return None, None
    fragment = parsed.fragment
    if not fragment and "#" in user_input:
        fragment = user_input.split("#", 1)[1]

    if not fragment:
        return None, None

    params = parse_qs(fragment)
    return params.get("id_token", [None])[0], params.get("state", [None])[0]
