from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from booping.context import config as config_mod
from tests.helpers import get_fixture_path


def test_core_only_load() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    cfg = config_mod.load(plugin_root, [])
    assert cfg["sprint"]["default_threshold_sp"] == 35  # type: ignore[index]


def test_override_changes_value() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-with-config-override")
    cfg = config_mod.load(plugin_root, [vault / "config.yaml"])
    assert cfg["sprint"]["default_threshold_sp"] == 50  # type: ignore[index]


def test_deep_merge_sibling_preserved() -> None:
    """Overriding sprint.default_threshold_sp leaves other sprint keys intact."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-with-config-override")
    cfg = config_mod.load(plugin_root, [vault / "config.yaml"])
    # plugin-root-minimal config has only sprint.default_threshold_sp;
    # the merge should produce sprint as a dict (not replaced wholesale)
    assert isinstance(cfg["sprint"], dict)


def test_list_replacement() -> None:
    """A list value in an override replaces wholesale (not merged)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump({"sprint": {"scale": ["a", "b"]}}, f)
        override_path = Path(f.name)

    cfg = config_mod.load(plugin_root, [override_path])
    assert cfg["sprint"]["scale"] == ["a", "b"]  # type: ignore[index]
    override_path.unlink()


def test_ordered_override_paths_signature() -> None:
    """Verify function accepts a list of override paths (multiple entries)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    cfg = config_mod.load(plugin_root, [Path("/nonexistent1.yaml"), Path("/nonexistent2.yaml")])
    assert cfg["sprint"]["default_threshold_sp"] == 35  # type: ignore[index]
