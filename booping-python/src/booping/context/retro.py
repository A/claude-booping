from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter


class Retro(BaseModel):
    path: Path
    plan: str | None = None
    goal: str | None = None
    created: date | None = None
    body: str = ""
    frontmatter: dict[str, Any]

    @classmethod
    def load_all(cls, vault: Path) -> list[Retro]:
        retros_dir = vault / "retrospectives"
        if not retros_dir.is_dir():
            return []
        retros: list[Retro] = []
        for p in sorted(retros_dir.glob("*.md")):
            fm, body = parse_frontmatter(p)
            plan_val = fm.get("plan")
            goal_val = fm.get("goal")
            created_val = fm.get("created")
            retros.append(
                cls(
                    path=p,
                    plan=str(plan_val) if plan_val is not None else None,
                    goal=str(goal_val) if goal_val is not None else None,
                    created=created_val if isinstance(created_val, date) else None,
                    body=body,
                    frontmatter=fm,
                )
            )
        return retros
