from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml


class Lesson:
    """Lesson loaded from vault/lessons/*.md."""

    def __init__(
        self,
        id: str,
        path: Path,
        title: str,
        body: str,
        frontmatter: dict[str, Any],
    ):
        self.id = id
        self.path = path
        self.title = title
        self.body = body
        self.frontmatter = frontmatter

    @classmethod
    def load_all(cls, vault: Path) -> list[Lesson]:
        lessons_dir = vault / "lessons"
        if not lessons_dir.exists():
            return []
        lessons = []
        for md_file in sorted(lessons_dir.glob("*.md")):
            front, body = _read_frontmatter(md_file)
            lessons.append(cls(
                id=md_file.stem,
                path=md_file,
                title=front.get("title", md_file.stem),
                body=body,
                frontmatter=front,
            ))
        return lessons


class Retro:
    """Retrospective loaded from vault/retrospectives/*.md."""

    def __init__(
        self,
        path: Path,
        plan: str | None,
        goal: str | None,
        created: date | None,
        body: str,
        frontmatter: dict[str, Any],
    ):
        self.path = path
        self.plan = plan
        self.goal = goal
        self.created = created
        self.body = body
        self.frontmatter = frontmatter

    @classmethod
    def load_all(cls, vault: Path) -> list[Retro]:
        retros_dir = vault / "retrospectives"
        if not retros_dir.exists():
            return []
        retros = []
        for md_file in sorted(retros_dir.glob("*.md")):
            front, body = _read_frontmatter(md_file)
            retros.append(cls(
                path=md_file,
                plan=front.get("plan"),
                goal=front.get("goal"),
                created=cls._parse_date(front.get("created")),
                body=body,
                frontmatter=front,
            ))
        return retros

    @staticmethod
    def _parse_date(v: str | None) -> date | None:
        if not v:
            return None
        try:
            return date.fromisoformat(v)
        except ValueError:
            return None


def _read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            front = yaml.safe_load(text[4:end]) or {}
            body = text[end + 4:].lstrip("\n")
            return front, body
    return {}, text