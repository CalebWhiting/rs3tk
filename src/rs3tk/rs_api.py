"""RuneScape website APIs — player details, RuneMetrics, player count, avatars."""

from __future__ import annotations

import re
from typing import TypeAlias

from pydantic import BaseModel

from rs3tk.jagex_api import _client

# ── playerDetails.ws ──────────────────────────────────────────────────────────


class PlayerDetail(BaseModel):
    name: str
    is_suffix: bool = False
    recruiting: bool = False
    title: str = ""
    clan: str = ""


# The endpoint wraps the JSON array in a jQuery callback: callback([...]);
# We strip the callback wrapper before parsing.
_JQUERY_RE = re.compile(r"^[^([]*\((.*)\)\s*;?\s*$", re.DOTALL)


def _parse_jsonp(text: str) -> str:
    m = _JQUERY_RE.match(text)
    return m.group(1) if m else text


async def get_player_details(names: list[str]) -> list[PlayerDetail]:
    import json

    params = {
        "names": json.dumps(names),
        "callback": "jQuery000000000000000_0000000000",
        "_": "0",
    }
    async with _client() as c:
        r = await c.get(
            "https://secure.runescape.com/m=website-data/playerDetails.ws",
            params=params,
        )
        r.raise_for_status()
        raw = _parse_jsonp(r.text)
        return [PlayerDetail.model_validate(x) for x in json.loads(raw)]


# ── RuneMetrics ───────────────────────────────────────────────────────────────


class Activity(BaseModel):
    date: str = ""
    details: str = ""
    text: str = ""


class SkillValue(BaseModel):
    id: int
    level: int
    xp: int
    rank: int = 0


class RuneMetricsProfile(BaseModel):
    name: str = ""
    rank: str = ""
    combat_level: int = 0
    total_skill: int = 0
    total_xp: int = 0
    quests_complete: int = 0
    quests_started: int = 0
    quests_not_started: int = 0
    magic: int = 0
    ranged: int = 0
    melee: int = 0
    logged_in: bool = False
    activities: list[Activity] = []
    skill_values: list[SkillValue] = []

    model_config = {"populate_by_name": True}

    def __init__(self, **data: object) -> None:
        raw = dict(data)
        raw["combat_level"] = raw.pop("combatlevel", 0)
        raw["total_skill"] = raw.pop("totalskill", 0)
        raw["total_xp"] = raw.pop("totalxp", 0)
        raw["quests_complete"] = raw.pop("questscomplete", 0)
        raw["quests_started"] = raw.pop("questsstarted", 0)
        raw["quests_not_started"] = raw.pop("questsnotstarted", 0)
        raw["logged_in"] = str(raw.pop("loggedIn", "false")).lower() == "true"
        raw["skill_values"] = raw.pop("skillvalues", [])
        super().__init__(**raw)


async def get_rune_metrics(name: str, activities: int = 5) -> RuneMetricsProfile:
    async with _client() as c:
        r = await c.get(
            "https://apps.runescape.com/runemetrics/profile/profile",
            params={"user": name, "activities": str(activities)},
        )
        r.raise_for_status()
        return RuneMetricsProfile.model_validate(r.json())


# ── Player Count ──────────────────────────────────────────────────────────────


async def get_player_count() -> int:
    params = {
        "varname": "iPlayerCount",
        "callback": "jQuery000000000000000_0000000000",
        "_": "0",
    }
    async with _client() as c:
        r = await c.get("https://www.runescape.com/player_count.js", params=params)
        r.raise_for_status()
        raw = _parse_jsonp(r.text)
        return int(raw.strip())


# ── Player Avatar ─────────────────────────────────────────────────────────────

AvatarUrl: TypeAlias = str


async def get_player_avatar(name: str, size: str = "chat") -> AvatarUrl:
    """Return the final avatar URL after following redirects."""
    url = f"https://secure.runescape.com/m=avatar-rs/{name}/{size}.png"
    async with _client() as c:
        r = await c.get(url, follow_redirects=True)
        return str(r.url)
