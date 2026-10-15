from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter
from booping.specs.targets import Target, TargetRejection, parse_target


class Lesson(BaseModel):
    id: str
    path: Path
    title: str
    body: str
    frontmatter: dict[str, Any]
    scope: str | None = None
    targets: list[str] = []
    parsed_targets: list[Target] = []
    target_rejections: list[TargetRejection] = []

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
            raw = fm.get("targets")
            entries: list[Any] = []
            if isinstance(raw, str):
                entries = [raw]
            elif isinstance(raw, list):
                entries = list(raw)  # pyright: ignore[reportUnknownArgumentType]
            results = [parse_target(entry) for entry in entries]
            lessons.append(
                cls(
                    id=stem,
                    path=p,
                    title=title,
                    body=body,
                    frontmatter=fm,
                    scope=scope,
                    targets=[str(entry) for entry in entries],
                    parsed_targets=[r for r in results if isinstance(r, Target)],
                    target_rejections=[r for r in results if isinstance(r, TargetRejection)],
                )
            )
        return lessons

    @classmethod
    def load_all(cls, vault: Path) -> list[Lesson]:
        return cls.load_dir(vault / "lessons")
