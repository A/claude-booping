from pathlib import Path

from pytest import MonkeyPatch

from booping.context.project import Project
from tests.helpers import get_fixture_path


def test_load_from_fixture_root() -> None:
    expected_dir = Path.home() / "Claude" / "full-test"
    project = Project(name="full-test", directory=expected_dir)
    assert project.name == "full-test"
    assert project.directory == expected_dir


def test_load_cwd_walkup(monkeypatch: MonkeyPatch) -> None:
    walkup_dir = get_fixture_path("project-walkup") / "nested" / "sub"

    def _fake_cwd() -> Path:
        return walkup_dir

    monkeypatch.setattr("booping.context.project.Path.cwd", _fake_cwd)
    project = Project.load_cwd()
    assert project is not None
    assert project.name == "walkup-test"
    assert project.directory == Path.home() / "Claude" / "walkup-test"


def test_load_cwd_absent_returns_none(monkeypatch: MonkeyPatch) -> None:
    def _fake_cwd() -> Path:
        return Path("/tmp")

    monkeypatch.setattr("booping.context.project.Path.cwd", _fake_cwd)
    project = Project.load_cwd()
    assert project is None