from __future__ import annotations

from pathlib import Path

import yaml

from booping.context import Context
from tests.helpers import get_fixture_path


def _write_global(xdg: Path, data: dict[str, object]) -> None:
    path = xdg / "booping" / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data))


def test_vault_override_skips_global_config_tier(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """`--project` pins the config tiers: the machine-global one is machine-local."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    _write_global(isolated_xdg_config_home, {"machine_only": "leaked"})
    vault = tmp_path / "pinned"
    vault.mkdir()
    (vault / "config.yaml").write_text(yaml.dump({"from_vault": "kept"}))

    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root, vault_override=vault)
    assert "machine_only" not in ctx.config
    assert ctx.config["from_vault"] == "kept"


def test_without_vault_override_global_tier_still_merges(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault_base = tmp_path / "vaults"
    _write_global(
        isolated_xdg_config_home, {"home_dir": str(vault_base), "machine_only": "leaked"}
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".booping").write_text("project_name: proj\n")
    vault = vault_base / "proj"
    vault.mkdir(parents=True)
    (vault / "config.yaml").write_text(yaml.dump({"from_vault": "kept"}))

    ctx = Context.assemble(start=repo, plugin_root=plugin_root)
    assert ctx.config["machine_only"] == "leaked"
    assert ctx.config["from_vault"] == "kept"
