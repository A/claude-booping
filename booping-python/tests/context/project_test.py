from __future__ import annotations

from pathlib import Path

from booping.context.project import Project
from tests.helpers import get_fixture_path


def test_load_cwd_from_vault_root() -> None:
    vault = get_fixture_path("vault-full")
    project = Project.load_cwd(start=vault)
    assert project is not None
    assert project.name == "vault-full"
    assert project.directory == Path.home() / "Claude" / "vault-full"


def test_load_cwd_from_subdirectory_walks_up(tmp_path: Path) -> None:
    booping = tmp_path / ".booping"
    booping.write_text("project_name: test-project\n")
    subdir = tmp_path / "src" / "templates"
    subdir.mkdir(parents=True)
    project = Project.load_cwd(start=subdir)
    assert project is not None
    assert project.name == "test-project"


def test_load_cwd_missing_booping_returns_none(tmp_path: Path) -> None:
    # tmp_path is outside any repo so no .booping will be found walking up
    project = Project.load_cwd(start=tmp_path)
    assert project is None
