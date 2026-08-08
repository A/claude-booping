from __future__ import annotations

import re
from pathlib import Path

import pytest

from booping.context.project import Project
from tests.helpers import get_fixture_path


def test_load_cwd_from_vault_root() -> None:
    vault = get_fixture_path("vault-full")
    project = Project.load_cwd(start=vault)
    assert project is not None
    assert project.name == "vault-full"
    assert project.directory == Path.home() / "Claude" / "vault-full"
    assert project.repo_directory == vault


def test_load_cwd_relative_vault_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: relvault\nvault_path: ./booping\n")
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.directory == (repo / "booping").resolve()


def test_load_cwd_absolute_vault_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    abs_vault = tmp_path / "elsewhere" / "vault"
    (repo / ".booping").write_text(
        f"project_name: absvault\nvault_path: {abs_vault}\n"
    )
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.directory == abs_vault


def test_load_cwd_tilde_vault_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: tildevault\nvault_path: ~/some-vault\n")
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.directory == Path.home() / "some-vault"


def test_home_dir_base_used_when_no_vault_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: hd\n")
    project = Project.load_cwd(start=repo, home_dir="/tmp/x")
    assert project is not None
    assert project.directory == Path("/tmp/x") / "hd"


def test_vault_path_wins_over_home_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: vp\nvault_path: ./booping\n")
    project = Project.load_cwd(start=repo, home_dir="/tmp/x")
    assert project is not None
    assert project.directory == (repo / "booping").resolve()


def test_default_home_dir_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: dh\n")
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.directory == Path.home() / "Claude" / "dh"


def test_home_dir_tilde_expands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: te\n")
    project = Project.load_cwd(start=repo, home_dir="~/somewhere")
    assert project is not None
    assert project.directory == Path.home() / "somewhere" / "te"


def test_is_local_vault_false_for_home_dir_vault(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: hv\n")
    project = Project.load_cwd(start=repo, home_dir="/tmp/x")
    assert project is not None
    assert project.is_local_vault is False


def test_is_local_vault_true_for_vault_under_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: localvault\nvault_path: ./booping\n")
    project = Project.load_cwd(start=repo)
    assert project is not None
    assert project.is_local_vault is True


def test_is_local_vault_false_for_claude_vault() -> None:
    vault = get_fixture_path("vault-full")
    project = Project.load_cwd(start=vault)
    assert project is not None
    assert project.is_local_vault is False


def test_latest_migration_defaults_to_minus_one(tmp_path: Path) -> None:
    (tmp_path / ".booping").write_text("project_name: nomig\n")
    project = Project.load_cwd(start=tmp_path)
    assert project is not None
    assert project.latest_migration == -1


def test_latest_migration_read_from_marker(tmp_path: Path) -> None:
    (tmp_path / ".booping").write_text("project_name: mig\nlatest_migration: 7\n")
    project = Project.load_cwd(start=tmp_path)
    assert project is not None
    assert project.latest_migration == 7


def test_unknown_marker_keys_are_ignored(tmp_path: Path) -> None:
    (tmp_path / ".booping").write_text(
        "project_name: future\nlatest_migration: 2\nsome_future_key: {a: [1, 2]}\n"
    )
    project = Project.load_cwd(start=tmp_path)
    assert project is not None
    assert project.latest_migration == 2


def test_non_integer_latest_migration_is_a_user_error_naming_the_file(
    tmp_path: Path,
) -> None:
    marker = tmp_path / ".booping"
    marker.write_text("project_name: bad\nlatest_migration: nope\n")
    with pytest.raises(ValueError, match=re.escape(str(marker))):
        Project.load_cwd(start=tmp_path)


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


def test_containment_resolves_vault_workdir(tmp_path: Path) -> None:
    vault = tmp_path / "myproj"
    workdir = vault / "docs"
    workdir.mkdir(parents=True)
    project = Project.load_cwd(start=workdir, home_dir=str(tmp_path))
    assert project is not None
    assert project.name == "myproj"
    assert project.directory == vault
    assert project.repo_directory is None
    assert project.is_local_vault is False


def test_containment_resolves_vault_root_itself(tmp_path: Path) -> None:
    vault = tmp_path / "myproj"
    vault.mkdir()
    project = Project.load_cwd(start=vault, home_dir=str(tmp_path))
    assert project is not None
    assert project.name == "myproj"
    assert project.directory == vault


def test_containment_skips_home_dir_itself(tmp_path: Path) -> None:
    assert Project.load_cwd(start=tmp_path, home_dir=str(tmp_path)) is None


def test_containment_skips_underscore_roots(tmp_path: Path) -> None:
    playbook_dir = tmp_path / "_playbooks" / "docs"
    playbook_dir.mkdir(parents=True)
    assert Project.load_cwd(start=playbook_dir, home_dir=str(tmp_path)) is None


def test_containment_skips_hidden_dirs(tmp_path: Path) -> None:
    hidden = tmp_path / ".trash" / "old"
    hidden.mkdir(parents=True)
    assert Project.load_cwd(start=hidden, home_dir=str(tmp_path)) is None


def test_marker_wins_over_containment(tmp_path: Path) -> None:
    # A repo-local vault nested under home_dir: the marker walk hits first.
    repo = tmp_path / "myproj"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: marked\nvault_path: ./booping\n")
    inner = repo / "booping" / "plans"
    inner.mkdir(parents=True)
    project = Project.load_cwd(start=inner, home_dir=str(tmp_path))
    assert project is not None
    assert project.name == "marked"
    assert project.repo_directory == repo


def test_load_cwd_without_git_still_resolves(tmp_path: Path) -> None:
    # tmp_path has no .git — the repo directory is the marker's dir regardless.
    (tmp_path / ".booping").write_text("project_name: nogit\n")
    project = Project.load_cwd(start=tmp_path)
    assert project is not None
    assert project.repo_directory == tmp_path.resolve()
