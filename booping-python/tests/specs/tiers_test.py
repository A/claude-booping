from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from booping.rendering import get_plugin_root
from booping.specs.tiers import project_root, resolve_tiers, types


def _config(**tiers: dict[str, Any]) -> dict[str, Any]:
    base: dict[str, Any] = {
        "core": {"namespace": "booping", "path": "vault/specs"},
        "global": {"namespace": None, "path": "_specs"},
        "project": {"path": None},
    }
    base.update(tiers)
    return {"core": {"specs": {"format": "src/specs", "tiers": base}}}


def test_project_root_vault_inside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    vault = repo / "vault"
    vault.mkdir(parents=True)
    assert project_root(None, repo, vault) == vault / "specs"


def test_project_root_vault_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    vault = tmp_path / "Claude" / "repo"
    repo.mkdir()
    vault.mkdir(parents=True)
    assert project_root(None, repo, vault) == repo / "specs"


def test_project_root_no_vault(tmp_path: Path) -> None:
    assert project_root(None, tmp_path, None) == tmp_path / "specs"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/specs", "REPO/docs/specs"),
        ("/srv/specs", "/srv/specs"),
        ("~/specs", "HOME/specs"),
    ],
)
def test_project_root_explicit_path(tmp_path: Path, path: str, expected: str) -> None:
    repo = tmp_path / "repo"
    vault = repo / "vault"
    vault.mkdir(parents=True)
    want = expected.replace("REPO", str(repo)).replace("HOME", str(Path.home()))
    assert project_root(path, repo, vault) == Path(want)


def test_resolve_tiers_all_three(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USER", "alice")
    plugin, home, repo = tmp_path / "plugin", tmp_path / "home", tmp_path / "repo"
    tiers = resolve_tiers(
        _config(), plugin_root=plugin, home_dir=home, repo=repo, vault=repo / "vault"
    )
    assert [(t.name, t.namespace, t.root, t.anchor) for t in tiers] == [
        ("core", "booping", plugin / "vault/specs", plugin),
        ("global", "alice", home / "_specs", home),
        ("project", None, repo / "vault/specs", repo),
    ]


def test_resolve_tiers_explicit_global_namespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("USER", "alice")
    tiers = resolve_tiers(
        _config(**{"global": {"namespace": "team", "path": "/abs/specs"}}),
        plugin_root=tmp_path,
        home_dir=tmp_path / "home",
        repo=None,
        vault=None,
    )
    assert [(t.name, t.namespace, t.root) for t in tiers] == [
        ("core", "booping", tmp_path / "vault/specs"),
        ("global", "team", Path("/abs/specs")),
    ]


def test_resolve_tiers_vault_override_drops_global(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tiers = resolve_tiers(
        _config(),
        plugin_root=tmp_path,
        home_dir=tmp_path / "home",
        repo=repo,
        vault=tmp_path / "fixture-vault",
        vault_override=True,
    )
    assert [t.name for t in tiers] == ["core", "project"]
    assert tiers[1].root == repo / "specs"


def test_types_lists_shipped_schemas() -> None:
    assert types(get_plugin_root() / "src/specs") == [
        "adr",
        "conflict",
        "idea",
        "reference",
        "rule",
        "runbook",
        "story",
        "value",
    ]
