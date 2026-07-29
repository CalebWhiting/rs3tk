from __future__ import annotations

from rs3tk_core.rs_api import RuneMetricsProfile


def test_rune_metrics_from_camel_case() -> None:
    data = {
        "name": "Test",
        "combatlevel": 100,
        "totalskill": 2000,
        "totalxp": 100000,
        "questscomplete": 50,
        "questsstarted": 5,
        "questsnotstarted": 10,
        "logged_in": True,
        "activities": [],
        "skillvalues": [],
    }
    p = RuneMetricsProfile.model_validate(data)
    assert p.combat_level == 100
    assert p.total_skill == 2000
    assert p.total_xp == 100000
    assert p.quests_complete == 50
    assert p.skill_values == []


def test_rune_metrics_defaults() -> None:
    p = RuneMetricsProfile()
    assert p.name == ""
    assert p.combat_level == 0
    assert p.activities == []
