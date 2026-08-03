"""Session management — token storage, refresh, and lifecycle."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from rs3tk_core.auth.oauth import generate_pkce_pair, generate_state
from rs3tk_core.config import (
    clear_account,
    get_account_token,
    set_account_token,
)
from rs3tk_core.jagex_api import (
    Tokens,
    UserProfile,
    build_auth_url,
    build_consent_url,
    create_session,
    decode_jwt_payload,
    exchange_code,
    get_profile,
)

logger = logging.getLogger(__name__)


def _store_tokens(username: str, tokens: Tokens) -> None:
    set_account_token(username, "access_token", tokens.access_token)
    set_account_token(username, "refresh_token", tokens.refresh_token)
    set_account_token(username, "id_token", tokens.id_token)
    set_account_token(username, "token_issued_at", datetime.now(UTC).isoformat())


def load_tokens(username: str) -> Tokens | None:
    access = get_account_token(username, "access_token")
    refresh = get_account_token(username, "refresh_token")
    if not access or not refresh:
        return None
    return Tokens(
        access_token=access,
        refresh_token=refresh,
        id_token=get_account_token(username, "id_token") or "",
        issued_at_str=get_account_token(username, "token_issued_at") or "",
    )


def logout_account(username: str) -> None:
    clear_account(username)


async def login(system_browser: bool = False) -> tuple[Tokens, str]:
    from rs3tk_core.auth.browser import (
        find_electron_login_script,
        find_electron_runtime,
        open_consent_browser,
        open_login_browser,
    )
    from rs3tk_core.auth.system_browser import open_consent_system, open_login_system

    verifier, challenge = generate_pkce_pair()
    state1 = generate_state()
    auth_url = build_auth_url(challenge, state1)

    if system_browser:
        code, returned_state = open_login_system(auth_url)
    else:
        runtime = find_electron_runtime()
        script = find_electron_login_script() if runtime else None
        if runtime is not None and script is not None:
            print("A browser window has opened. Log in to your Jagex Account.")
            code, returned_state = open_login_browser(runtime, script, auth_url)
        else:
            code, returned_state = open_login_system(auth_url)

    if not code:
        raise RuntimeError("Login failed — no authorization code received.")
    if returned_state != state1:
        raise RuntimeError("Login failed — CSRF state mismatch.")

    tokens = await exchange_code(code, verifier)

    if not tokens.id_token:
        raise RuntimeError("Login failed — no ID token received.")

    token_body = decode_jwt_payload(tokens.id_token)
    username = str(token_body.get("sub", ""))

    _store_tokens(username, tokens)

    state2, nonce = generate_state(), generate_state()
    consent_url = build_consent_url(tokens.id_token, state2, nonce)

    if system_browser:
        id_token, consent_state = open_consent_system(consent_url)
    else:
        runtime = find_electron_runtime()
        script = find_electron_login_script() if runtime else None
        if runtime is not None and script is not None:
            print("A browser window has opened for consent.")
            id_token, consent_state = open_consent_browser(runtime, script, consent_url)
        else:
            id_token, consent_state = open_consent_system(consent_url)

    if not id_token:
        raise RuntimeError("Consent failed — no ID token received.")
    if consent_state != state2:
        raise RuntimeError("Consent failed — CSRF state mismatch.")

    try:
        token_body = decode_jwt_payload(id_token)
        if token_body.get("nonce") != nonce:
            raise RuntimeError("Consent failed — nonce mismatch.")
    except (ValueError, RuntimeError) as e:
        raise RuntimeError("Consent failed — could not validate token.") from e

    set_account_token(username, "consent_id_token", id_token)
    set_account_token(username, "session_id", await create_session(id_token))
    return tokens, username


async def ensure_valid_token(username: str) -> Tokens:
    """Return the cached tokens for the given user.

    Tokens are never auto-refreshed and never considered "expired" by this
    layer. The access_token is only used to bootstrap the login flow; once
    a session_id and consent_id_token have been stored, the actual API
    calls authenticate with the session_id (a long-lived Bearer token
    re-created on demand from the consent_id_token if it stops working).

    If you need to force a re-login, run `rs3tk auth login` again.
    """
    tokens = load_tokens(username)
    if tokens is None:
        raise RuntimeError(f"Not logged in as {username}. Run `rs3tk login` first.")
    return tokens


async def _ensure_session(username: str) -> str:
    await ensure_valid_token(username)

    session_id = get_account_token(username, "session_id")
    if session_id:
        return session_id

    consent_id = get_account_token(username, "consent_id_token")
    if not consent_id:
        raise RuntimeError(f"No consent token for {username}. Run `rs3tk login` again.")

    session_id = await create_session(consent_id)
    set_account_token(username, "session_id", session_id)
    return session_id


async def get_session(username: str) -> tuple[str, UserProfile]:
    session_id = await _ensure_session(username)
    try:
        profile = await get_profile(session_id)
        return session_id, profile
    except Exception:
        logger.debug("Profile fetch failed for %s, retrying with new session", username, exc_info=True)
        consent_id = get_account_token(username, "consent_id_token")
        if not consent_id:
            raise RuntimeError(f"No consent token for {username}. Run `rs3tk login` again.") from None
        session_id = await create_session(consent_id)
        set_account_token(username, "session_id", session_id)
        profile = await get_profile(session_id)
        return session_id, profile
