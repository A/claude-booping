from __future__ import annotations

from booping.context.lesson import Lesson
from tests.helpers import get_fixture_path


def test_load_all_count_and_fields() -> None:
    vault = get_fixture_path("vault-full")
    lessons = Lesson.load_all(vault)
    assert len(lessons) == 1

    lesson = lessons[0]
    assert lesson.id == "2026-01-20-prefer-explicit-over-implicit"
    # fallback to id (no title in frontmatter)
    assert lesson.title == "2026-01-20-prefer-explicit-over-implicit"
    assert "explicit return types" in lesson.body
    assert lesson.frontmatter["date"].year == 2026


def test_load_all_missing_lessons_dir() -> None:
    vault = get_fixture_path("vault-empty")
    lessons = Lesson.load_all(vault)
    assert lessons == []
