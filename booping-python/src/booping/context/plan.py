from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter


class Plan(BaseModel):
    path: Path
    title: str
    type: Literal["feature", "bug", "refactoring"]
    status: str
    sp: int | None = None
    split_from: str | None = None
    created: date | None = None
    planned: str | None = None
    started: str | None = None
    completed: str | None = None
    retro: str | None = None
    goal: str | None = None
    business_goal: str = ""
    body: str = ""

    @classmethod
    def load_all(cls, vault: Path) -> list[Plan]:
        plans_dir = vault / "plans"
        if not plans_dir.is_dir():
            return []
        plans: list[Plan] = []
        for p in sorted(plans_dir.glob("*.md")):
            fm, body = parse_frontmatter(p)
            plans.append(_from_fm(p, fm, body))
        return plans


def _from_fm(path: Path, fm: dict[str, Any], body: str) -> Plan:
    planned_raw = fm.get("planned")
    started_raw = fm.get("started")
    completed_raw = fm.get("completed")
    created_raw = fm.get("created")
    return Plan(
        path=path,
        title=str(fm.get("title", path.stem)),
        type=fm["type"],  # type: ignore[arg-type]
        status=str(fm.get("status", "")),
        sp=int(fm["sp"]) if fm.get("sp") is not None else None,
        split_from=str(fm["split_from"]) if fm.get("split_from") is not None else None,
        created=created_raw if isinstance(created_raw, date) else None,
        planned=str(planned_raw) if planned_raw is not None else None,
        started=str(started_raw) if started_raw is not None else None,
        completed=str(completed_raw) if completed_raw is not None else None,
        retro=str(fm["retro"]) if fm.get("retro") is not None else None,
        goal=str(fm["goal"]) if fm.get("goal") is not None else None,
        business_goal=str(fm.get("business_goal", "")),
        body=body,
    )
