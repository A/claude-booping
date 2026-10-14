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

    @classmethod
    def load_targeted(cls, home_dir: Path | None, vault: Path | None) -> list[Lesson]:
        """Lessons from the two `_lessons/` roots — global `{home_dir}/_lessons/` then
        project `{vault}/_lessons/`, project shadowing global by filename."""
        dirs: list[tuple[str, Path]] = []
        if home_dir is not None:
            dirs.append(("global", home_dir / "_lessons"))
        if vault is not None:
            dirs.append(("project", vault / "_lessons"))
        merged = _merge_by_filename([(scope, cls.load_dir(p, scope)) for scope, p in dirs])
        return sorted(merged, key=lambda lesson: lesson.path.name)


def _merge_by_filename(loaded: list[tuple[str, list[Lesson]]]) -> list[Lesson]:
    """Roots ordered least → most specific; a filename carried by several roots keeps
    only its most specific copy."""
    winner: dict[str, int] = {}
    for index, (_, lessons) in enumerate(loaded):
        for lesson in lessons:
            winner[lesson.path.name] = index
    merged: list[Lesson] = []
    for index, (_, lessons) in enumerate(loaded):
        merged.extend(lesson for lesson in lessons if winner[lesson.path.name] == index)
    return merged
