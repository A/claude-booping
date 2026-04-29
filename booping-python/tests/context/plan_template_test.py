from booping.context.plan_template import PlanTemplate
from tests.helpers import get_fixture_path


def test_core_only() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    templates = PlanTemplate.load_all(plugin_root, vault=None)
    assert len(templates) == 2
    names = [t.name for t in templates]
    assert "backend" in names
    assert "frontend" in names
    assert all(t.source == "core" for t in templates)


def test_project_override() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    templates = PlanTemplate.load_all(plugin_root, vault)

    custom = [t for t in templates if t.name == "custom-template"]
    assert len(custom) == 1
    assert custom[0].source == "project"
    assert "Custom template body" in custom[0].body

    core_names = [t.name for t in templates if t.source == "core"]
    assert "backend" in core_names
    assert "frontend" in core_names


def test_project_replaces_core_same_name() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    templates = PlanTemplate.load_all(plugin_root, vault)
    names = [t.name for t in templates]
    assert len(names) == len(set(names))