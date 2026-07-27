from __future__ import annotations

from datetime import UTC, datetime, timedelta

from rs3tk.jagex_api import Character, Membership, Tokens, UserProfile


def test_tokens_from_dict() -> None:
    t = Tokens(access_token="a", refresh_token="r", id_token="i")
    assert t.access_token == "a"


def test_character_is_member_true() -> None:
    m = Membership(game_group="osrs", active_subscription=True, expiration_date="2030-01-01")
    c = Character(account_id="1", display_name="Test", user_hash="h", membership=[m])
    assert c.is_member is True


def test_character_is_member_false() -> None:
    m = Membership(game_group="osrs", active_subscription=False, expiration_date="2020-01-01")
    c = Character(account_id="1", display_name="Test", user_hash="h", membership=[m])
    assert c.is_member is False


def test_character_is_member_active_false_but_not_yet_expired() -> None:
    future = (datetime.now(UTC) + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    m = Membership(game_group="osrs", active_subscription=False, expiration_date=future)
    c = Character(account_id="1", display_name="Test", user_hash="h", membership=[m])
    assert c.is_member is True


def test_character_is_member_via_membership_expire_alias() -> None:
    future = (datetime.now(UTC) + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    m = Membership(game_group="osrs", active_subscription=False, membership_expire=future)
    c = Character(account_id="1", display_name="Test", user_hash="h", membership=[m])
    assert c.is_member is True


def test_user_profile_from_dict() -> None:
    data = {"uuid": "u", "username": "test", "displayName": "Test", "characters": []}
    p = UserProfile.model_validate(data)
    assert p.username == "test"
    assert p.display_name == "Test"
