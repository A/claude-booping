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
    step: str | None = None
    scope: str | None = None

    @classmethod
    def load_dir(cls, path: Path, scope: str | None = None) -> list[Lesson]:
        """Load every `*.md` in `path`, filename-sorted. Missing dir → empty list."""
        if not path.is_dir():
            return []
        lessons: list[Lesson] = []
        for p in sorted(path.glob("*.md")):
            fm, body = parse_frontmatter(p)
            stem = p.stem
            title = str(fm.get("title", stem))
            step = fm.get("step")
            lessons.append(
                cls(
                    id=stem,
                    path=p,
                    title=title,
                    body=body,
                    frontmatter=fm,
                    step=str(step) if step is not None else None,
                    scope=scope,
                )
            )
        return lessons

    @classmethod
    def load_all(cls, vault: Path) -> list[Lesson]:
        return cls.load_dir(vault / "lessons")
