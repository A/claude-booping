from __future__ import annotations

from pathlib import Path

import yaml

from booping.context import Context
from tests.helpers import get_fixture_path


def _write_global(xdg: Path, data: dict[str, object]) -> Path:
    path = xdg / "booping" / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data))
    return path


def test_assemble_smoke() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)

    assert ctx.project is not None
    assert ctx.project.name == "vault-full"

    assert ctx.vault == vault
    assert len(ctx.lessons) > 0
    assert len(ctx.plan_templates) > 0
    assert len(ctx.skills) > 0
    assert len(ctx.agents) > 0
    assert ctx.config != {}


def test_assemble_no_project(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    # tmp_path is outside the repo so no .booping walk-up will find one
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)

    assert ctx.project is None
    assert ctx.vault is None
    assert ctx.lessons == []
    # Plan templates still load from plugin root even with no project
    assert len(ctx.plan_templates) > 0
    assert len(ctx.skills) > 0
    assert len(ctx.agents) > 0
    assert ctx.config != {}


def test_assemble_no_project_merges_global(tmp_path: Path, isolated_xdg_config_home: Path) -> None:
    """No-project branch (outside any .booping) still merges the global tier."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    _write_global(isolated_xdg_config_home, {"sprint": {"default_threshold_sp": 77}})
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    assert ctx.project is None
    assert ctx.config["sprint"]["default_threshold_sp"] == 77


def test_assemble_home_dir_drives_vault(tmp_path: Path, isolated_xdg_config_home: Path) -> None:
    """Global `home_dir` + no `vault_path:` → Project.directory == <home_dir>/<name>."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    _write_global(isolated_xdg_config_home, {"home_dir": str(vault_base)})
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: myproj\n")
    ctx = Context.assemble(start=repo, plugin_root=plugin_root)
    assert ctx.project is not None
    assert ctx.project.directory == vault_base / "myproj"


def test_assemble_vault_path_wins_over_global_home_dir(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """`.booping` `vault_path:` set → global `home_dir` ignored."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    _write_global(isolated_xdg_config_home, {"home_dir": str(tmp_path / "vaults")})
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: vp\nvault_path: ./booping\n")
    ctx = Context.assemble(start=repo, plugin_root=plugin_root)
    assert ctx.project is not None
    assert ctx.project.directory == (repo / "booping").resolve()


def test_assemble_default_vault_without_global(tmp_path: Path) -> None:
    """No global config → default ~/Claude/<name> resolution unchanged (regression)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: dproj\n")
    ctx = Context.assemble(start=repo, plugin_root=plugin_root)
    assert ctx.project is not None
    assert ctx.project.directory == Path.home() / "Claude" / "dproj"


def _write_playbook(root: Path, name: str) -> None:
    step = root / "_playbooks" / name / "s1"
    step.mkdir(parents=True)
    (root / "_playbooks" / name / "playbook.md").write_text(
        f"---\nname: {name}\ntitle: {name}\ngraph:\n  s1: []\n---\nbody\n"
    )
    (step / "prompt.md").write_text("---\nsummary: s1\n---\nstep body\n")


def test_assemble_vault_override_pins_playbook_discovery(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    vault_base.mkdir()
    _write_global(isolated_xdg_config_home, {"home_dir": str(vault_base)})
    _write_playbook(vault_base, "global-only")
    vault = tmp_path / "pinned"
    vault.mkdir()
    _write_playbook(vault, "local-only")

    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root, vault_override=vault)
    assert [pb.name for pb in ctx.playbooks] == ["local-only"]


def test_assemble_vault_workdir_resolves_by_containment(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """A start inside `home_dir/{project}/` resolves that vault — local playbooks
    included — even though no `.booping` marker is reachable from it."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    _write_global(isolated_xdg_config_home, {"home_dir": str(vault_base)})
    vault = vault_base / "myproj"
    _write_playbook(vault, "local-docs")
    workdir = vault / "docs"
    workdir.mkdir()

    ctx = Context.assemble(start=workdir, plugin_root=plugin_root)
    assert ctx.project is not None
    assert ctx.project.name == "myproj"
    assert ctx.project.repo_directory is None
    assert ctx.vault == vault
    assert "local-docs" in [pb.name for pb in ctx.playbooks]


def test_assemble_without_override_keeps_global_playbooks(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    vault_base.mkdir()
    _write_global(isolated_xdg_config_home, {"home_dir": str(vault_base)})
    _write_playbook(vault_base, "global-only")

    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    assert [pb.name for pb in ctx.playbooks] == ["global-only"]


def test_assemble_project_tier_home_dir_has_no_effect(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """`home_dir` set in the project tier is merged into config but does NOT move the
    vault — the vault is already resolved from core+global by then (documented
    non-behavior)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    _write_global(isolated_xdg_config_home, {"home_dir": str(vault_base)})
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: proj\n")
    vault = vault_base / "proj"
    vault.mkdir(parents=True)
    (vault / "config.yaml").write_text(yaml.dump({"home_dir": "/tmp/should-be-ignored"}))
    ctx = Context.assemble(start=repo, plugin_root=plugin_root)
    assert ctx.project is not None
    # Vault resolved from the global tier, not the project-tier home_dir.
    assert ctx.project.directory == vault
    # The project-tier value is still merged into config — just inert for resolution.
    assert ctx.config["home_dir"] == "/tmp/should-be-ignored"


def test_booping_initialized_false_without_global_config(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    assert ctx.booping_initialized is False


def test_booping_initialized_true_with_global_config(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    _write_global(isolated_xdg_config_home, {"home_dir": str(tmp_path / "vaults")})
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    assert ctx.booping_initialized is True


def _write_rule(specs: Path, name: str) -> None:
    path = specs / "rule" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntitle: R\nstatus: accepted\ntargets: [groom]\nbrief: B.\n---\n")


def test_assemble_vault_override_drops_global_tier_rules(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    core_specs = tmp_path / "core-specs"
    tiers = {
        "core": {"namespace": "booping", "path": str(core_specs)},
        "global": {"namespace": "me", "path": "_specs"},
    }
    _write_global(
        isolated_xdg_config_home,
        {"home_dir": str(vault_base), "core": {"specs": {"tiers": tiers}}},
    )
    _write_rule(core_specs, "0001-core.md")
    _write_rule(vault_base / "_specs", "0002-global.md")
    vault = tmp_path / "pinned"
    vault.mkdir()
    (vault / "config.yaml").write_text(yaml.dump({"core": {"specs": {"tiers": tiers}}}))

    pinned = Context.assemble(start=tmp_path, plugin_root=plugin_root, vault_override=vault)
    assert [rule.ref for rule in pinned.targeted_rules] == ["booping:rule/0001"]

    unpinned = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    assert unpinned.project is None
    assert [rule.ref for rule in unpinned.targeted_rules] == [
        "booping:rule/0001",
        "me:rule/0002",
    ]
    assert unpinned.rule_skips == []
