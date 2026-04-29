from booping.context.lesson import Lesson
from tests.helpers import get_fixture_path


def test_load_all_from_vault_full() -> None:
    vault = get_fixture_path("vault-full")
    lessons = Lesson.load_all(vault)
    assert len(lessons) == 1

    lesson = lessons[0]
    assert lesson.id == "test-lesson"
    assert lesson.title == "test-lesson"
    assert "explicit return" in lesson.body


def test_load_all_missing_dir() -> None:
    lessons = Lesson.load_all(get_fixture_path("vault-full") / "nonexistent")
    assert lessons == []