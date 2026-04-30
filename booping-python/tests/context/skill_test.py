from __future__ import annotations

from booping.context.skill import Skill
from tests.helpers import get_fixture_path


def test_load_all_count() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    skills = Skill.load_all(plugin_root)
    assert len(skills) == 2


def test_load_all_fields() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    skills = Skill.load_all(plugin_root)
    skill = skills["sample-skill"]
    assert skill.name == "sample-skill"
    assert skill.description == "A sample skill for testing"
    assert skill.effort == "low"
    assert skill.model == "claude-opus-4-5"
    assert skill.allowed_tools == ["Bash(git:*)"]
    assert skill.user_invocable is True
    assert skill.debug_enabled is False


def test_debug_enabled_flag() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    skills = Skill.load_all(plugin_root)
    assert skills["debug-skill"].debug_enabled is True
    assert skills["sample-skill"].debug_enabled is False
