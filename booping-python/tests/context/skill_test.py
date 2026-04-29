from booping.context.skill import Skill
from tests.helpers import get_fixture_path


def test_load_all() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    skills = Skill.load_all(plugin_root)
    assert len(skills) == 2
    assert "help" in skills
    assert "groom" in skills

    help_skill = skills["help"]
    assert help_skill.description == "Show what booping is"
    assert help_skill.effort == "low"
    assert "Read" in help_skill.allowed_tools
    assert help_skill.user_invocable is True
    assert help_skill.debug_enabled is False

    groom_skill = skills["groom"]
    assert groom_skill.effort == "high"


def test_debug_enabled_marker() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    debug_marker = plugin_root / "skills" / "help" / ".debug_enabled"
    debug_marker.touch()
    try:
        skills = Skill.load_all(plugin_root)
        assert skills["help"].debug_enabled is True
    finally:
        debug_marker.unlink()