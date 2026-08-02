from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter

# Directory-plan filenames, preference order. Legacy dual-file dirs pair a full
# `plan.md` with a bare `index.md` run artifact, so `plan.md` wins when both
# exist; new-style dirs (groom playbook) carry only `index.md`.
DIR_PLAN_NAMES = ("plan.md", "index.md")


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
    summary: str = ""
    commit: str | None = None
    body: str = ""

    @property
    def slug(self) -> str:
        if self.path.name in DIR_PLAN_NAMES:
            return self.path.parent.name
        return self.path.stem

    @property
    def rel_link(self) -> str:
        if self.path.name in DIR_PLAN_NAMES:
            return f"plans/{self.path.parent.name}/{self.path.name}"
        return f"plans/{self.path.name}"

    @classmethod
    def load_all(cls, vault: Path) -> list[Plan]:
        plans_dir = vault / "plans"
        if not plans_dir.is_dir():
            return []

        by_slug: dict[str, Path] = {}
        for name in DIR_PLAN_NAMES:
            for p in plans_dir.glob(f"*/{name}"):
                if p.parent.name in by_slug:
                    print(
                        f"warning: skipping {p} — shadowed by {by_slug[p.parent.name]}",
                        file=sys.stderr,
                    )
                    continue
                by_slug[p.parent.name] = p
        for p in plans_dir.glob("*.md"):
            if p.stem in by_slug:
                print(
                    f"warning: skipping {p} — shadowed by {by_slug[p.stem]}",
                    file=sys.stderr,
                )
                continue
            by_slug[p.stem] = p

        plans: list[Plan] = []
        for _, path in sorted(by_slug.items()):
            try:
                plans.append(_from_fm(path, *parse_frontmatter(path)))
            except Exception as exc:
                print(
                    f"warning: skipping {path} — not a loadable plan ({exc})",
                    file=sys.stderr,
                )
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
        summary=str(fm.get("summary", "")),
        commit=str(fm["commit"]) if fm.get("commit") is not None else None,
        body=body,
    )
