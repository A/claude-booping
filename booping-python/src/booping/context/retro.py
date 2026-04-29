from datetime import date
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


class Retro(BaseModel):
    path: Path
    plan: str | None = None
    goal: str | None = None
    created: date | None = None
    body: str = ""
    frontmatter: dict[str, Any] = {}

    @classmethod
    def load_all(cls, vault: Path) -> list["Retro"]:
        retros_dir = vault / "retrospectives"
        if not retros_dir.is_dir():
            return []
        retros: list[Retro] = []
        for md_file in sorted(retros_dir.glob("*.md")):
            text = md_file.read_text()
            fm, body = _parse_frontmatter(text)
            retros.append(
                cls(
                    path=md_file,
                    plan=fm.get("plan"),
                    goal=fm.get("goal"),
                    created=fm.get("created"),
                    body=body,
                    frontmatter=fm,
                )
            )
        return retros