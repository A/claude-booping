from __future__ import annotations

import os
import subprocess
from pathlib import Path

from booping.context.project import Project
from tests.helpers import get_fixture_path


def test_load_cwd_from_vault_root() -> None:
    vault = get_fixture_path("vault-full")
    project = Project.load_cwd(start=vault)
    assert project is not None
    assert project.name == "vault-full"
    assert project.directory == Path.home() / "Claude" / "vault-full"
    assert project.repo_directory == vault


def test_load_cwd_from_subdirectory_walks_up(tmp_path: Path) -> None:
    booping = tmp_path / ".booping"
    booping.write_text("project_name: test-project\n")
    subdir = tmp_path / "src" / "templates"
    subdir.mkdir(parents=True)
    project = Project.load_cwd(start=subdir)
    assert project is not None
    assert project.name == "test-project"
    assert project.repo_directory == tmp_path.resolve()


def test_load_cwd_missing_booping_returns_none(tmp_path: Path) -> None:
    # tmp_path is outside any repo so no .booping will be found walking up
    project = Project.load_cwd(start=tmp_path)
    assert project is None


def test_load_cwd_captures_git_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: gittest\n")
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
        env=env,
    )
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.git_commit is not None
    assert len(project.git_commit) == 40
    assert all(c in "0123456789abcdef" for c in project.git_commit)


def test_load_cwd_no_git_returns_none_commit(tmp_path: Path) -> None:
    # tmp_path has no .git, so git rev-parse fails — git_commit must be None
    (tmp_path / ".booping").write_text("project_name: nogit\n")
    project = Project.load_cwd(start=tmp_path)
    assert project is not None
    assert project.git_commit is None
    assert project.repo_directory == tmp_path.resolve()
