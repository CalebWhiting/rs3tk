"""Jagex API client and data models."""

from __future__ import annotations

import base64
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import TypeAlias
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, ConfigDict


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# A JWT is three base64url-encoded segments separated by dots: header.payload.signature.
# We only need the payload (index 1) to read claims like "nonce".
# Base64url uses "-" and "_" instead of "+" and "/", and omits padding.
# The standard base64 decoder expects padding, so we re-add "=" as needed.
def decode_jwt_payload(token: str) -> dict[str, object]:
    try:
        payload = token.split(".")[1]
        padding = (4 - len(payload) % 4) % 4
        payload += "=" * padding
        result: dict[str, object] = json.loads(base64.urlsafe_b64decode(payload))
        return result
    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid JWT: {e}") from e


class _BaseApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_snake_to_camel)


class Tokens(_BaseApiModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    issued_at_str: str = ""

    @property
    def expiry(self) -> datetime:
        if self.issued_at_str:
            try:
                issued = datetime.fromisoformat(self.issued_at_str)
                return issued + timedelta(seconds=self.expires_in)
            except ValueError:
                pass
        return datetime.now(UTC) + timedelta(seconds=self.expires_in)


class Membership(_BaseApiModel):
    game_group: str
    active_subscription: bool
    expiration_date: str = ""
    membership_expire: str = ""

    @property
    def expires_at(self) -> str:
        return self.expiration_date or self.membership_expire


class Character(_BaseApiModel):
    account_id: str
    display_name: str
    user_hash: str = ""
    membership: list[Membership] = []

    @property
    def is_member(self) -> bool:
        now = datetime.now()
        for m in self.membership:
            if m.active_subscription:
                return True
            expire = m.expires_at
            if expire:
                try:
                    exp = datetime.fromisoformat(expire)
                    if exp.tzinfo is not None:
                        exp = exp.replace(tzinfo=None)
                    if now < exp:
                        return True
                except (ValueError, TypeError):
                    pass
        return False


GameSession: TypeAlias = str


class UserProfile(_BaseApiModel):
    uuid: str
    username: str
    email: str | None = None
    display_name: str | None = None
    characters: list[Character] = []


_BASE_URL = "https://account.jagex.com"
_AUTH_URL = f"{_BASE_URL}/oauth2/auth"
_TOKEN_URL = f"{_BASE_URL}/oauth2/token"
_AUTH_API = "https://auth.jagex.com"
_SESSIONS_URL = f"{_AUTH_API}/game-session/v1/sessions"
_ACCOUNTS_URL = f"{_AUTH_API}/game-session/v1/accounts"

CLIENT_ID = "com_jagex_auth_desktop_launcher"
REDIRECT_URI = "https://secure.runescape.com/m=weblogin/launcher-redirect"
CONSENT_REDIRECT_URI = "http://localhost"
SCOPES = (
    "openid offline gamesso.token.create user.profile.read"
    " user.entitlement.read user.game.read"
    " user.sku.read user.voucher.redeem"
)
CONSENT_CLIENT_ID = "1fddee4e-b100-4f4e-b2b0-097f9088f9d2"


# A Bearer token is a credential that grants the holder access to a
# protected resource.  It is sent in the HTTP Authorization header as
# "Authorization: Bearer <token>".  The server validates the token and
# uses its embedded claims (e.g. account ID, scopes) to authorize the
# request.  Unlike session cookies, bearer tokens are stateless and
# suitable for API-to-API calls.
def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}", "Accept": "application/json"}


@asynccontextmanager
async def _client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as c:
        yield c


def build_auth_url(code_challenge: str, state: str) -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "login",
        "flow": "launcher",
    }
    return f"{_AUTH_URL}?{urlencode(params)}"


def build_consent_url(id_token: str, state: str, nonce: str) -> str:
    params = {
        "prompt": "consent",
        "redirect_uri": CONSENT_REDIRECT_URI,
        "response_type": "id_token code",
        "client_id": CONSENT_CLIENT_ID,
        "scope": "openid offline",
        "id_token_hint": id_token,
        "state": state,
        "nonce": nonce,
    }
    return f"{_AUTH_URL}?{urlencode(params)}"


async def exchange_code(code: str, code_verifier: str) -> Tokens:
    async with _client() as c:
        r = await c.post(
            _TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
            },
        )
        r.raise_for_status()
        return Tokens.model_validate(r.json())


async def refresh_tokens(refresh_token: str) -> Tokens:
    async with _client() as c:
        r = await c.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": refresh_token,
            },
        )
        r.raise_for_status()
        return Tokens.model_validate(r.json())


def _extract_session(r: httpx.Response) -> str | None:
    try:
        data = r.json()
        sid = data.get("sessionId")
        return str(sid) if sid else None
    except (ValueError, KeyError):
        return None


async def create_session(id_token: str) -> str:
    async with _client() as c:
        r = await c.post(
            _SESSIONS_URL,
            json={"idToken": id_token},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if r.status_code == 409:
            sid = _extract_session(r)
            if sid:
                return sid
            r2 = await c.get(_SESSIONS_URL, headers=_bearer(id_token))
            if r2.status_code == 200:
                data = r2.json()
                raw = None
                if isinstance(data, list) and data:
                    raw = data[0].get("sessionId")
                elif isinstance(data, dict):
                    raw = data.get("sessionId")
                if raw:
                    return str(raw)
            raise RuntimeError("Session exists but could not be retrieved. Re-login required.")
        r.raise_for_status()
        raw = r.json().get("sessionId")
        if not raw:
            raise RuntimeError("No session ID in response.")
        return str(raw)


async def get_profile(session_id: str) -> UserProfile:
    async with _client() as c:
        r = await c.get(
            f"{_ACCOUNTS_URL}?fetchMembership=true",
            headers=_bearer(session_id),
        )
        r.raise_for_status()
        data = r.json()

        if isinstance(data, list):
            return UserProfile(
                uuid="",
                username="",
                characters=[Character.model_validate(x) for x in data],
            )
        return UserProfile.model_validate(data)
