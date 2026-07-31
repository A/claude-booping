from __future__ import annotations

from pathlib import Path

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


def test_load_dir_filename_sorted(tmp_path: Path) -> None:
    (tmp_path / "0002_second.md").write_text("---\ntitle: Second\n---\nsecond\n")
    (tmp_path / "0001_first.md").write_text("---\ntitle: First\n---\nfirst\n")
    (tmp_path / "notes.txt").write_text("ignored\n")
    lessons = Lesson.load_dir(tmp_path)
    assert [lesson.id for lesson in lessons] == ["0001_first", "0002_second"]
    assert [lesson.title for lesson in lessons] == ["First", "Second"]


def test_load_dir_missing_dir(tmp_path: Path) -> None:
    assert Lesson.load_dir(tmp_path / "nope") == []


def test_load_dir_step_and_scope(tmp_path: Path) -> None:
    (tmp_path / "0001_scoped.md").write_text("---\nstep: research-web\n---\nbody\n")
    (tmp_path / "0002_plain.md").write_text("---\ntitle: Plain\n---\nbody\n")
    lessons = Lesson.load_dir(tmp_path, scope="playbook")
    assert [lesson.step for lesson in lessons] == ["research-web", None]
    assert {lesson.scope for lesson in lessons} == {"playbook"}


def test_load_dir_frontmatterless_falls_back_to_stem(tmp_path: Path) -> None:
    (tmp_path / "0001_bare.md").write_text("just a body\n")
    lessons = Lesson.load_dir(tmp_path)
    assert [(lesson.title, lesson.step, lesson.body) for lesson in lessons] == [
        ("0001_bare", None, "just a body\n")
    ]
