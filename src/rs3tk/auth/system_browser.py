"""System browser with manual URL paste for OAuth2 login."""

from __future__ import annotations

import webbrowser
from urllib.parse import parse_qs, urlparse

from rs3tk.output import console


def open_login_system(url: str) -> tuple[str | None, str | None]:
    console.print()
    console.print("[bold cyan]Step 1/2:[/] Login")
    webbrowser.open(url)
    console.print("A browser window has opened. Log in to your Jagex Account.")
    console.print()
    console.print("After logging in, paste the redirect URL below.")
    console.print("It will look like:")
    console.print("  [dim]https://secure.runescape.com/m=weblogin/launcher-redirect?code=...&state=...[/]")
    console.print()

    try:
        user_input = input("Paste URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None, None

    if not user_input:
        return None, None

    parsed = urlparse(user_input)
    if parsed.hostname != "secure.runescape.com":
        console.print("[bold red]Error:[/] URL host doesn't match expected (secure.runescape.com)")
        return None, None
    params = parse_qs(parsed.query)
    return params.get("code", [None])[0], params.get("state", [None])[0]


def open_consent_system(url: str) -> tuple[str | None, str | None]:
    console.print()
    console.print("[bold cyan]Step 2/2:[/] Consent")
    webbrowser.open(url)
    console.print("A browser window has opened for consent.")
    console.print("It will redirect automatically — no action needed.")
    console.print()
    console.print("After the redirect, paste the URL below.")
    console.print("It will look like:")
    console.print("  [dim]http://localhost#id_token=...&state=...[/]")
    console.print()

    try:
        user_input = input("Paste URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None, None

    if not user_input:
        return None, None

    parsed = urlparse(user_input)
    if parsed.hostname not in ("localhost", "127.0.0.1"):
        console.print("[bold red]Error:[/] URL host doesn't match expected (localhost)")
        return None, None
    fragment = parsed.fragment
    if not fragment and "#" in user_input:
        fragment = user_input.split("#", 1)[1]

    if not fragment:
        return None, None

    params = parse_qs(fragment)
    return params.get("id_token", [None])[0], params.get("state", [None])[0]
