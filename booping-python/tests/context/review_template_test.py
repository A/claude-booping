from __future__ import annotations

from booping.context.review_template import ReviewTemplate
from tests.helpers import get_fixture_path


def test_core_only_mode() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-empty")
    templates = ReviewTemplate.load_all(plugin_root, vault)
    assert len(templates) == 2
    names = {t.name for t in templates}
    assert "sample" in names
    assert "python" in names
    for t in templates:
        assert t.source == "core"


def test_layer_parsed() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-empty")
    templates = ReviewTemplate.load_all(plugin_root, vault)
    by_name = {t.name: t for t in templates}
    assert by_name["python"].layer == "language"
    assert by_name["sample"].layer == "generic"


def test_project_override_replaces_same_name_preserving_position() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    core_only = ReviewTemplate.load_all(plugin_root, get_fixture_path("vault-empty"))
    core_sample_idx = next(i for i, t in enumerate(core_only) if t.name == "sample")

    templates = ReviewTemplate.load_all(plugin_root, vault)
    assert len(templates) == len(core_only)
    overridden = templates[core_sample_idx]
    assert overridden.name == "sample"
    assert overridden.source == "project"
    assert overridden.description == "Project-overridden sample"
