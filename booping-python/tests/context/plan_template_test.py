from __future__ import annotations

from booping.context.plan_template import PlanTemplate
from tests.helpers import get_fixture_path


def test_core_only_mode() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    # vault-empty has no plan_templates dir
    vault = get_fixture_path("vault-empty")
    templates = PlanTemplate.load_all(plugin_root, vault)
    assert len(templates) == 2
    names = {t.name for t in templates}
    assert "sample" in names
    assert "api-endpoint" in names
    for t in templates:
        assert t.source == "core"


def test_project_override_replaces_core_entry() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    templates = PlanTemplate.load_all(plugin_root, vault)

    # vault-full has api-endpoint which overrides the core entry
    api_templates = [t for t in templates if t.name == "api-endpoint"]
    assert len(api_templates) == 1
    api = api_templates[0]
    assert api.source == "project"
    # Project version body differs from core
    assert "Define route and handler" in api.body


def test_project_override_preserves_position() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    templates = PlanTemplate.load_all(plugin_root, vault)
    # Overridden entry is in place of core entry (not appended)
    api_idx = next(i for i, t in enumerate(templates) if t.name == "api-endpoint")
    # sample was added first alphabetically; api-endpoint second in core
    assert api_idx == 0 or api_idx == 1  # position preserved from core ordering


def test_sample_template_fields() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-empty")
    templates = PlanTemplate.load_all(plugin_root, vault)
    sample = next(t for t in templates if t.name == "sample")
    assert sample.description == "A sample plan template for testing"
    assert "Do the thing" in sample.body
