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


class Lesson(BaseModel):
    id: str
    path: Path
    title: str
    body: str
    frontmatter: dict[str, Any]

    @classmethod
    def load_all(cls, vault: Path) -> list["Lesson"]:
        lessons_dir = vault / "lessons"
        if not lessons_dir.is_dir():
            return []
        lessons: list[Lesson] = []
        for md_file in sorted(lessons_dir.glob("*.md")):
            text = md_file.read_text()
            fm, body = _parse_frontmatter(text)
            lessons.append(
                cls(
                    id=md_file.stem,
                    path=md_file,
                    title=fm.get("title", md_file.stem),
                    body=body,
                    frontmatter=fm,
                )
            )
        return lessons