"""RuneScape website APIs — RuneMetrics profile lookup."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from rs3tk.jagex_api import _client


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

    @model_validator(mode="before")
    @classmethod
    def _remap_camel_case(cls, data: dict[str, object]) -> dict[str, object]:
        raw = dict(data)
        raw["combat_level"] = raw.pop("combatlevel", 0)
        raw["total_skill"] = raw.pop("totalskill", 0)
        raw["total_xp"] = raw.pop("totalxp", 0)
        raw["quests_complete"] = raw.pop("questscomplete", 0)
        raw["quests_started"] = raw.pop("questsstarted", 0)
        raw["quests_not_started"] = raw.pop("questsnotstarted", 0)
        raw["logged_in"] = str(raw.pop("loggedIn", "false")).lower() == "true"
        raw["skill_values"] = raw.pop("skillvalues", [])
        return raw


async def get_rune_metrics(name: str, activities: int = 5) -> RuneMetricsProfile:
    async with _client() as c:
        r = await c.get(
            "https://apps.runescape.com/runemetrics/profile/profile",
            params={"user": name, "activities": str(activities)},
        )
        r.raise_for_status()
        return RuneMetricsProfile.model_validate(r.json())
