from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter


class Lesson(BaseModel):
    id: str
    path: Path
    title: str
    body: str
    frontmatter: dict[str, Any]

    @classmethod
    def load_all(cls, vault: Path) -> list[Lesson]:
        lessons_dir = vault / "lessons"
        if not lessons_dir.is_dir():
            return []
        lessons: list[Lesson] = []
        for p in sorted(lessons_dir.glob("*.md")):
            fm, body = parse_frontmatter(p)
            stem = p.stem
            title = str(fm.get("title", stem))
            lessons.append(cls(id=stem, path=p, title=title, body=body, frontmatter=fm))
        return lessons
