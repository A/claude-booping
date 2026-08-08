from __future__ import annotations

from pathlib import Path

import pytest

from booping.context.lesson import Lesson, LessonTarget, TargetRejection, parse_target
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


def test_load_dir_scope_comes_from_caller(tmp_path: Path) -> None:
    (tmp_path / "0001_scoped.md").write_text("---\nstep: research-web\n---\nbody\n")
    (tmp_path / "0002_plain.md").write_text("---\ntitle: Plain\n---\nbody\n")
    lessons = Lesson.load_dir(tmp_path, scope="project")
    assert {lesson.scope for lesson in lessons} == {"project"}
    assert not any(hasattr(lesson, "step") for lesson in lessons)


def test_load_dir_frontmatterless_falls_back_to_stem(tmp_path: Path) -> None:
    (tmp_path / "0001_bare.md").write_text("just a body\n")
    lessons = Lesson.load_dir(tmp_path)
    assert [(lesson.title, lesson.body) for lesson in lessons] == [
        ("0001_bare", "just a body\n")
    ]
    assert lessons[0].targets == []
    assert lessons[0].parsed_targets == []
    assert lessons[0].target_rejections == []


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("groom", LessonTarget(kind="playbook", playbook="groom")),
        (
            "groom/draft-plan",
            LessonTarget(kind="step", playbook="groom", step="draft-plan"),
        ),
        (
            "agent:booping-developer",
            LessonTarget(kind="agent", agent="booping-developer"),
        ),
        (
            "agent:booping:booping-researcher",
            LessonTarget(kind="agent", agent="booping:booping-researcher"),
        ),
        ("skill:playbook", LessonTarget(kind="skill", skill="playbook")),
        ("skill:code-review", LessonTarget(kind="skill", skill="code-review")),
    ],
)
def test_parse_target_legal_forms(entry: str, expected: LessonTarget) -> None:
    assert parse_target(entry) == expected


@pytest.mark.parametrize(
    "entry",
    [
        "",
        "  ",
        " groom",
        "groom*",
        "!groom",
        "groom/*",
        "groom/draft-plan/extra",
        "/groom",
        "groom/",
        "agent:",
        "agent:*",
        "skill:",
        "skill:*",
        "some playbook",
        42,
        {"playbook": "groom"},
        None,
    ],
)
def test_parse_target_rejections(entry: object) -> None:
    assert isinstance(parse_target(entry), TargetRejection)


def test_load_dir_targets_scalar_normalizes_to_list(tmp_path: Path) -> None:
    (tmp_path / "0001_scalar.md").write_text("---\ntargets: groom\n---\nbody\n")
    lesson = Lesson.load_dir(tmp_path)[0]
    assert lesson.targets == ["groom"]
    assert lesson.parsed_targets == [LessonTarget(kind="playbook", playbook="groom")]


def test_load_dir_targets_list_mixed_valid_and_malformed(tmp_path: Path) -> None:
    (tmp_path / "0001_mixed.md").write_text(
        "---\ntargets:\n  - groom/draft-plan\n  - 'groom/*'\n---\nbody\n"
    )
    lesson = Lesson.load_dir(tmp_path)[0]
    assert lesson.targets == ["groom/draft-plan", "groom/*"]
    assert lesson.parsed_targets == [
        LessonTarget(kind="step", playbook="groom", step="draft-plan")
    ]
    assert [r.entry for r in lesson.target_rejections] == ["groom/*"]


def test_load_dir_malformed_targets_lesson_is_not_dropped(tmp_path: Path) -> None:
    (tmp_path / "0001_bad.md").write_text("---\ntargets:\n  - '!groom'\n---\nbody\n")
    lessons = Lesson.load_dir(tmp_path)
    assert [lesson.id for lesson in lessons] == ["0001_bad"]
    assert lessons[0].parsed_targets == []
    assert [r.entry for r in lessons[0].target_rejections] == ["!groom"]


def _write_lesson(root: Path, name: str, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(f"---\ntargets:\n  - groom\n---\n{body}\n")


def test_load_targeted_union_and_shadowing(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    vault = tmp_path / "vault"
    _write_lesson(home_dir / "_lessons", "0001_shared.md", "global copy")
    _write_lesson(home_dir / "_lessons", "0003_global_only.md", "global only")
    _write_lesson(vault / "_lessons", "0001_shared.md", "project copy")
    _write_lesson(vault / "_lessons", "0002_project_only.md", "project only")

    lessons = Lesson.load_targeted(home_dir, vault)
    assert [lesson.path.name for lesson in lessons] == [
        "0001_shared.md",
        "0002_project_only.md",
        "0003_global_only.md",
    ]
    assert [lesson.scope for lesson in lessons] == ["project", "project", "global"]
    assert lessons[0].body.strip() == "project copy"


def test_load_targeted_global_only_without_vault(tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    _write_lesson(home_dir / "_lessons", "0001_g.md", "global")
    lessons = Lesson.load_targeted(home_dir, None)
    assert [lesson.id for lesson in lessons] == ["0001_g"]


def test_load_targeted_missing_dirs(tmp_path: Path) -> None:
    assert Lesson.load_targeted(tmp_path / "home", tmp_path / "vault") == []
    assert Lesson.load_targeted(None, None) == []
