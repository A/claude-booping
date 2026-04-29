from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end]
    body = text[end + 3 :]
    if body.startswith("\n"):
        body = body[1:]
    return yaml.safe_load(fm_text) or {}, body


class Plan(BaseModel):
    path: Path
    title: str = ""
    type: str = ""
    status: str = ""
    sp: int | None = None
    split_from: str | None = None
    created: str | None = None
    planned: str | None = None
    started: str | None = None
    completed: str | None = None
    retro: str | None = None
    goal: str | None = None
    business_goal: str = ""
    body: str = ""

    @classmethod
    def load_all(cls, vault: Path) -> list["Plan"]:
        plans_dir = vault / "plans"
        if not plans_dir.is_dir():
            return []
        plans: list[Plan] = []
        for md_file in sorted(plans_dir.glob("*.md")):
            text = md_file.read_text()
            fm, body = _parse_frontmatter(text)
            plans.append(
                cls(
                    path=md_file,
                    title=fm.get("title", ""),
                    type=fm.get("type", ""),
                    status=fm.get("status", ""),
                    sp=fm.get("sp"),
                    split_from=fm.get("split_from"),
                    created=fm.get("created"),
                    planned=fm.get("planned"),
                    started=fm.get("started"),
                    completed=fm.get("completed"),
                    retro=fm.get("retro"),
                    goal=fm.get("goal"),
                    business_goal=fm.get("business_goal", ""),
                    body=body,
                )
            )
        return plans