from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from booping.rendering import get_plugin_root
from booping.specs.tiers import project_root, resolve_tiers, schemas, status_enum, types


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
    assert project_root(None, repo, vault) == tmp_path / "repo" / "vault"


def test_project_root_vault_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    vault = tmp_path / "Claude" / "repo"
    repo.mkdir()
    vault.mkdir(parents=True)
    assert project_root(None, repo, vault) == tmp_path / "Claude" / "repo"


def test_project_root_no_vault(tmp_path: Path) -> None:
    assert project_root(None, tmp_path, None) == tmp_path / "specs"


def test_project_root_specs_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    assert project_root("specs", repo, repo / "vault") == tmp_path / "repo" / "specs"


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
        ("project", None, repo / "vault", repo),
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
    assert tiers[1].root == tmp_path / "fixture-vault"


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


def test_schemas_without_tier_dir_is_the_shipped_set(tmp_path: Path) -> None:
    fmt = tmp_path / "format"
    (fmt / "schemas").mkdir(parents=True)
    (fmt / "schemas" / "rule.yaml").write_text("doc: rule\n")
    (fmt / "schemas" / "adr.yaml").write_text("doc: adr\n")
    assert schemas(fmt, tmp_path / "tier") == {
        "adr": fmt / "schemas" / "adr.yaml",
        "rule": fmt / "schemas" / "rule.yaml",
    }


def test_schemas_tier_overrides_a_stem_and_adds_one(tmp_path: Path) -> None:
    fmt, root = tmp_path / "format", tmp_path / "tier"
    (fmt / "schemas").mkdir(parents=True)
    (root / "_schemas").mkdir(parents=True)
    for stem in ("rule", "adr"):
        (fmt / "schemas" / f"{stem}.yaml").write_text(f"doc: {stem}\n")
    for stem in ("rule", "mechanic"):
        (root / "_schemas" / f"{stem}.yaml").write_text(f"doc: {stem}\n")
    assert schemas(fmt, root) == {
        "adr": fmt / "schemas" / "adr.yaml",
        "mechanic": root / "_schemas" / "mechanic.yaml",
        "rule": root / "_schemas" / "rule.yaml",
    }


def test_resolve_tiers_gives_each_tier_its_own_overlay(tmp_path: Path) -> None:
    plugin, home, repo = tmp_path / "plugin", tmp_path / "home", tmp_path / "repo"
    (plugin / "src/specs/schemas").mkdir(parents=True)
    (plugin / "src/specs/schemas/rule.yaml").write_text("doc: rule\n")
    (home / "_specs/_schemas").mkdir(parents=True)
    (home / "_specs/_schemas/rule.yaml").write_text("doc: rule\n")
    (home / "_specs/_schemas/mechanic.yaml").write_text("doc: mechanic\n")
    tiers = resolve_tiers(
        _config(), plugin_root=plugin, home_dir=home, repo=repo, vault=repo / "vault"
    )
    assert {t.name: (t.types, t.schemas["rule"]) for t in tiers} == {
        "core": (["rule"], plugin / "src/specs/schemas/rule.yaml"),
        "global": (["mechanic", "rule"], home / "_specs/_schemas/rule.yaml"),
        "project": (["rule"], plugin / "src/specs/schemas/rule.yaml"),
    }


def test_status_enum_reads_the_frontmatter_rule_in_written_order() -> None:
    idea = get_plugin_root() / "src" / "specs" / "schemas" / "idea.yaml"
    assert status_enum(idea) == ["open", "validating", "accepted", "rejected"]


def test_status_enum_is_empty_without_a_status_enum(tmp_path: Path) -> None:
    schema = tmp_path / "x.yaml"
    schema.write_text("doc: x\nrules:\n  - select: FRONTMATTER\n    has:\n      type: x\n")
    assert status_enum(schema) == []
