from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from booping.context import config as config_mod
from booping.context.config import AgentConfig, SkillConfig
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


def test_agent_config_native_validates() -> None:
    cfg = AgentConfig.model_validate({"internal": True, "good_for": ["x"]})
    assert cfg.type == "agent"
    assert cfg.command is None
    assert cfg.internal is True


def test_agent_config_cli_without_command_errors() -> None:
    with pytest.raises(Exception):
        AgentConfig.model_validate({"type": "cli"})


def test_agent_config_cli_with_command_validates() -> None:
    cfg = AgentConfig.model_validate({"type": "cli", "command": "pi --print"})
    assert cfg.type == "cli"
    assert cfg.command == "pi --print"


def test_agent_config_rejects_unknown_field() -> None:
    with pytest.raises(Exception):
        AgentConfig.model_validate({"tipe": "cli"})


def test_skill_config_disable_internal_agents_default() -> None:
    cfg = SkillConfig.model_validate({"agents": {"a": {"internal": True}}})
    assert cfg.disable_internal_agents is False


def test_validate_skills_raises_on_cli_without_command() -> None:
    bad = {"skills": {"develop": {"agents": {"x": {"type": "cli"}}}}}
    with pytest.raises(ValueError):
        config_mod.validate_skills(bad)


def test_validate_skills_passes_on_valid_config() -> None:
    good = {
        "skills": {
            "develop": {
                "agents": {
                    "booping-developer": {"internal": True, "good_for": ["coding"]},
                    "pi-mesh": {"type": "cli", "command": "pi --print"},
                },
                "disable_internal_agents": True,
            }
        }
    }
    config_mod.validate_skills(good)


def test_loader_does_not_filter_internal_when_disable_flag_set(tmp_path: Path) -> None:
    plugin_root = Path(__file__).resolve().parents[3]
    override_path = tmp_path / "config.yaml"
    override_path.write_text(
        yaml.dump({"skills": {"develop": {"disable_internal_agents": True}}})
    )
    cfg = config_mod.load(plugin_root, [override_path])
    agents = cfg["skills"]["develop"]["agents"]  # type: ignore[index]
    assert "booping-developer" in agents
    assert "booping-researcher" in agents


def test_ordered_override_paths_signature() -> None:
    """Verify function accepts a list of override paths (multiple entries)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    cfg = config_mod.load(plugin_root, [Path("/nonexistent1.yaml"), Path("/nonexistent2.yaml")])
    assert cfg["sprint"]["default_threshold_sp"] == 35  # type: ignore[index]
