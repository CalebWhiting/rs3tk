"""Test auth/session.py — token storage, refresh, and session lifecycle."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rs3tk_core.auth import session as session_module
from rs3tk_core.auth.session import (
    _ensure_session,
    _store_tokens,
    ensure_valid_token,
    get_session,
    load_tokens,
    logout_account,
)
from rs3tk_core.jagex_api import Tokens, UserProfile


def _run(coro: object) -> object:
    return asyncio.run(coro)  # type: ignore[arg-type]


def _make_tokens(expiry_offset_seconds: int = 3600) -> Tokens:
    issued = datetime.now(UTC) - timedelta(seconds=0)
    return Tokens(
        access_token="access123",
        refresh_token="refresh123",
        id_token="id123",
        expires_in=expiry_offset_seconds,
        issued_at_str=issued.isoformat(),
    )


# ── _store_tokens / load_tokens ─────────────────────────────────────────────


class TestStoreAndLoad:
    @patch("rs3tk_core.auth.session.set_account_token")
    def test_stores_all_token_fields(self, mock_set: MagicMock) -> None:
        tokens = _make_tokens()

        _store_tokens("alice", tokens)

        assert mock_set.call_count == 4
        mock_set.assert_any_call("alice", "access_token", "access123")
        mock_set.assert_any_call("alice", "refresh_token", "refresh123")
        mock_set.assert_any_call("alice", "id_token", "id123")
        # token_issued_at is set to the current ISO timestamp; just verify the call
        called_keys = [c.args[1] for c in mock_set.call_args_list]
        assert "token_issued_at" in called_keys

    @patch("rs3tk_core.auth.session.get_account_token")
    def test_load_returns_none_without_access(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = lambda user, key: None if key == "access_token" else "refresh"

        assert load_tokens("alice") is None

    @patch("rs3tk_core.auth.session.get_account_token")
    def test_load_returns_none_without_refresh(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = lambda user, key: "access" if key == "access_token" else None

        assert load_tokens("alice") is None

    @patch("rs3tk_core.auth.session.get_account_token")
    def test_load_returns_tokens(self, mock_get: MagicMock) -> None:
        values = {
            "access_token": "a",
            "refresh_token": "r",
            "id_token": "i",
            "token_issued_at": "2024-01-01T00:00:00+00:00",
        }
        mock_get.side_effect = lambda user, key: values.get(key)

        tokens = load_tokens("alice")

        assert tokens is not None
        assert tokens.access_token == "a"
        assert tokens.refresh_token == "r"
        assert tokens.id_token == "i"


# ── logout_account ──────────────────────────────────────────────────────────


class TestLogoutAccount:
    @patch("rs3tk_core.auth.session.clear_account")
    def test_calls_clear_account(self, mock_clear: MagicMock) -> None:
        logout_account("alice")
        mock_clear.assert_called_once_with("alice")


# ── ensure_valid_token ──────────────────────────────────────────────────────


class TestEnsureValidToken:
    @patch("rs3tk_core.auth.session.load_tokens")
    def test_raises_when_no_tokens(self, mock_load: MagicMock) -> None:
        mock_load.return_value = None

        with pytest.raises(RuntimeError, match="Not logged in"):
            _run(ensure_valid_token("alice"))

    @patch("rs3tk_core.auth.session.load_tokens")
    def test_returns_cached_tokens_as_is(self, mock_load: MagicMock) -> None:
        # Fresh tokens — returned directly
        tokens = _make_tokens()
        mock_load.return_value = tokens

        result = _run(ensure_valid_token("alice"))

        assert result is tokens

    @patch("rs3tk_core.auth.session.load_tokens")
    def test_returns_cached_tokens_even_if_access_token_expired(self, mock_load: MagicMock) -> None:
        # access_token is 'expired' (24h ago, 1s expiry) but we never refresh
        # — the access_token is only used to bootstrap login; session_id is
        # what authenticates API calls.
        issued = datetime.now(UTC) - timedelta(hours=24)
        tokens = Tokens(
            access_token="old_a",
            refresh_token="old_r",
            id_token="old_i",
            expires_in=1,
            issued_at_str=issued.isoformat(),
        )
        mock_load.return_value = tokens

        result = _run(ensure_valid_token("alice"))

        assert result is tokens

    @patch("rs3tk_core.auth.session._store_tokens")
    @patch("rs3tk_core.auth.session.load_tokens")
    def test_never_refreshes_or_stores(self, mock_load: MagicMock, mock_store: MagicMock) -> None:
        # Even with an expired access_token, ensure_valid_token must not
        # trigger any side effects — no _store_tokens call.
        issued = datetime.now(UTC) - timedelta(hours=24)
        tokens = Tokens(
            access_token="old_a",
            refresh_token="old_r",
            id_token="old_i",
            expires_in=1,
            issued_at_str=issued.isoformat(),
        )
        mock_load.return_value = tokens

        _run(ensure_valid_token("alice"))

        mock_store.assert_not_called()


# ── _ensure_session ─────────────────────────────────────────────────────────


class TestEnsureSession:
    @patch("rs3tk_core.auth.session.get_account_token")
    @patch("rs3tk_core.auth.session.ensure_valid_token", new_callable=AsyncMock)
    def test_returns_cached_session(self, mock_ensure: AsyncMock, mock_get: MagicMock) -> None:
        mock_ensure.return_value = _make_tokens()
        mock_get.return_value = "cached-session"

        result = _run(_ensure_session("alice"))

        assert result == "cached-session"

    @patch("rs3tk_core.auth.session.create_session", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.set_account_token")
    @patch("rs3tk_core.auth.session.get_account_token")
    @patch("rs3tk_core.auth.session.ensure_valid_token", new_callable=AsyncMock)
    def test_creates_session_when_missing(
        self,
        mock_ensure: AsyncMock,
        mock_get: MagicMock,
        mock_set: MagicMock,
        mock_create: AsyncMock,
    ) -> None:
        mock_ensure.return_value = _make_tokens()
        # First call: get_account_token for "session_id" -> None
        # Second call: get_account_token for "consent_id_token" -> "consent-xyz"
        mock_get.side_effect = lambda user, key: None if key == "session_id" else "consent-xyz"
        mock_create.return_value = "new-session"

        result = _run(_ensure_session("alice"))

        assert result == "new-session"
        mock_create.assert_called_once_with("consent-xyz")
        mock_set.assert_called_once_with("alice", "session_id", "new-session")

    @patch("rs3tk_core.auth.session.get_account_token")
    @patch("rs3tk_core.auth.session.ensure_valid_token", new_callable=AsyncMock)
    def test_raises_when_no_consent_token(self, mock_ensure: AsyncMock, mock_get: MagicMock) -> None:
        mock_ensure.return_value = _make_tokens()
        mock_get.side_effect = lambda user, key: None  # both None

        with pytest.raises(RuntimeError, match="No consent token"):
            _run(_ensure_session("alice"))


# ── get_session ─────────────────────────────────────────────────────────────


class TestGetSession:
    @patch("rs3tk_core.auth.session.get_profile", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session._ensure_session", new_callable=AsyncMock)
    def test_returns_session_and_profile(self, mock_ensure: AsyncMock, mock_profile: AsyncMock) -> None:
        mock_ensure.return_value = "sid"
        profile = UserProfile(uuid="u", username="u", display_name="u", characters=[])
        mock_profile.return_value = profile

        sid, prof = _run(get_session("alice"))

        assert sid == "sid"
        assert prof is profile
        mock_profile.assert_called_once_with("sid")

    @patch("rs3tk_core.auth.session.get_profile", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.create_session", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.set_account_token")
    @patch("rs3tk_core.auth.session.get_account_token")
    @patch("rs3tk_core.auth.session._ensure_session", new_callable=AsyncMock)
    def test_retries_with_new_session_on_profile_failure(
        self,
        mock_ensure: AsyncMock,
        mock_get: MagicMock,
        mock_set: MagicMock,
        mock_create: AsyncMock,
        mock_profile: AsyncMock,
    ) -> None:
        mock_ensure.return_value = "sid-old"
        mock_get.return_value = "consent-xyz"
        mock_create.return_value = "sid-new"
        profile = UserProfile(uuid="u", username="u", display_name="u", characters=[])
        # First call to get_profile fails, second succeeds
        mock_profile.side_effect = [Exception("profile gone"), profile]

        sid, prof = _run(get_session("alice"))

        assert sid == "sid-new"
        assert prof is profile
        assert mock_profile.call_count == 2
        mock_create.assert_called_once_with("consent-xyz")
        mock_set.assert_called_once_with("alice", "session_id", "sid-new")

    @patch("rs3tk_core.auth.session.get_profile", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.get_account_token")
    @patch("rs3tk_core.auth.session._ensure_session", new_callable=AsyncMock)
    def test_raises_on_retry_when_no_consent(
        self, mock_ensure: AsyncMock, mock_get: MagicMock, mock_profile: AsyncMock
    ) -> None:
        mock_ensure.return_value = "sid"
        mock_get.return_value = None
        mock_profile.side_effect = Exception("profile gone")

        with pytest.raises(RuntimeError, match="No consent token"):
            _run(get_session("alice"))


# ── smoke import for coverage ───────────────────────────────────────────────


def test_module_imports() -> None:
    assert hasattr(session_module, "login")


# ── login (full OAuth flow) ──────────────────────────────────────────────────


def _make_jwt(sub: str = "alice", nonce: str | None = None) -> str:
    """Build a minimal unsigned JWT (header.payload.signature) with the given claims."""
    import base64
    import json

    def b64(obj: dict[str, object]) -> str:
        raw = json.dumps(obj).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    header = b64({"alg": "none", "typ": "JWT"})
    payload: dict[str, object] = {"sub": sub}
    if nonce is not None:
        payload["nonce"] = nonce
    return f"{header}.{b64(payload)}.sig"


class TestLogin:
    @patch("rs3tk_core.auth.session.create_session", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.set_account_token")
    @patch("rs3tk_core.auth.session.decode_jwt_payload")
    @patch("rs3tk_core.auth.session.exchange_code", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.browser.open_login_browser")
    @patch("rs3tk_core.auth.browser.open_consent_browser")
    @patch("rs3tk_core.auth.session.generate_state")
    @patch("rs3tk_core.auth.session.generate_pkce_pair")
    def test_happy_path(
        self,
        mock_pkce: MagicMock,
        mock_state: MagicMock,
        mock_consent_browser: MagicMock,
        mock_login_browser: MagicMock,
        mock_exchange: AsyncMock,
        mock_decode: MagicMock,
        mock_set: MagicMock,
        mock_create: AsyncMock,
    ) -> None:
        # Three values needed: state1 (login), state2 (consent), nonce (consent)
        mock_pkce.return_value = ("verifier", "challenge")
        mock_state.side_effect = ["state-login", "state-consent", "state-nonce"]
        mock_login_browser.return_value = ("auth-code", "state-login")
        tokens = Tokens(access_token="a", refresh_token="r", id_token=_make_jwt(sub="alice"))
        mock_exchange.return_value = tokens
        mock_consent_browser.return_value = (
            _make_jwt(nonce="state-nonce"),
            "state-consent",
        )
        # First call decodes login id_token (just sub), second decodes consent (nonce check)
        mock_decode.side_effect = [{"sub": "alice"}, {"nonce": "state-nonce"}]
        mock_create.return_value = "new-session"

        tokens_returned, username = _run(session_module.login())

        assert username == "alice"
        assert tokens_returned is tokens
        mock_create.assert_called_once()
        mock_set.assert_any_call("alice", "consent_id_token", _make_jwt(nonce="state-nonce"))
        mock_set.assert_any_call("alice", "session_id", "new-session")

    @patch("rs3tk_core.auth.browser.open_login_browser")
    def test_no_code_raises(self, mock_login: MagicMock) -> None:
        mock_login.return_value = (None, None)

        with pytest.raises(RuntimeError, match="no authorization code"):
            _run(session_module.login())

    @patch("rs3tk_core.auth.browser.open_login_browser")
    def test_state_mismatch_raises(self, mock_login: MagicMock) -> None:
        mock_login.return_value = ("auth-code", "wrong-state")

        with pytest.raises(RuntimeError, match="CSRF state mismatch"):
            _run(session_module.login())

    @patch("rs3tk_core.auth.session.exchange_code", new_callable=AsyncMock)
    @patch("rs3tk_core.auth.session.generate_state")
    @patch("rs3tk_core.auth.browser.open_login_browser")
    def test_no_id_token_raises(self, mock_login: MagicMock, mock_state: MagicMock, mock_exchange: AsyncMock) -> None:
        mock_state.return_value = "state-login"
        mock_login.return_value = ("auth-code", "state-login")
        mock_exchange.return_value = Tokens(access_token="a", refresh_token="r", id_token="")

        with pytest.raises(RuntimeError, match="no ID token"):
            _run(session_module.login())
