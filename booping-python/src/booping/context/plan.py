from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml


def _read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            front = yaml.safe_load(text[4:end]) or {}
            body = text[end + 4:].lstrip("\n")
            return front, body
    return {}, text


class Plan:
    """Plan loaded from vault/plans/*.md."""

    def __init__(
        self,
        path: Path,
        title: str,
        type: str = "feature",
        status: str = "backlog",
        sp: int | None = None,
        split_from: str | None = None,
        created: date | None = None,
        planned: str | None = None,
        started: str | None = None,
        completed: str | None = None,
        retro: str | None = None,
        goal: str | None = None,
        business_goal: str = "",
        body: str = "",
    ):
        self.path = path
        self.title = title
        self.type = type
        self.status = status
        self.sp = sp
        self.split_from = split_from
        self.created = created
        self.planned = planned
        self.started = started
        self.completed = completed
        self.retro = retro
        self.goal = goal
        self.business_goal = business_goal
        self.body = body

    @classmethod
    def load_all(cls, vault: Path) -> list[Plan]:
        plans_dir = vault / "plans"
        if not plans_dir.exists():
            return []
        plans = []
        for md_file in sorted(plans_dir.glob("*.md")):
            front, body = _read_frontmatter(md_file)
            plans.append(cls(
                path=md_file,
                title=front.get("title", md_file.stem),
                type=front.get("type", "feature"),
                status=front.get("status", "backlog"),
                sp=front.get("sp"),
                split_from=front.get("split_from"),
                created=cls._parse_date(front.get("created")),
                planned=front.get("planned"),
                started=front.get("started"),
                completed=front.get("completed"),
                retro=front.get("retro"),
                goal=front.get("goal"),
                business_goal=front.get("business_goal", ""),
                body=body,
            ))
        return plans

    @staticmethod
    def _parse_date(v: str | None) -> date | None:
        if not v:
            return None
        for fmt in ("%Y-%m-%d",):
            try:
                return date.fromisoformat(v)
            except ValueError:
                continue
        return None