from __future__ import annotations

from pathlib import Path

from booping.context.review_template import ReviewTemplate
from tests.helpers import get_fixture_path


def _write_global(home_dir: Path, name: str, description: str) -> Path:
    directory = home_dir / "review_templates"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.md"
    _ = path.write_text(
        f"---\nname: {name}\ndescription: {description}\nlayer: generic\n---\n\nglobal body\n"
    )
    return path


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


def test_global_tier_overrides_core(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    _ = _write_global(tmp_path, "sample", "Global-overridden sample")

    templates = ReviewTemplate.load_all(
        plugin_root, get_fixture_path("vault-empty"), tmp_path
    )
    by_name = {t.name: t for t in templates}
    assert by_name["sample"].source == "global"
    assert by_name["sample"].description == "Global-overridden sample"
    assert by_name["python"].source == "core"


def test_project_tier_overrides_global(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    _ = _write_global(tmp_path, "sample", "Global-overridden sample")

    templates = ReviewTemplate.load_all(
        plugin_root, get_fixture_path("vault-full"), tmp_path
    )
    core_only = ReviewTemplate.load_all(plugin_root, get_fixture_path("vault-empty"))
    assert len(templates) == len(core_only)
    by_name = {t.name: t for t in templates}
    assert by_name["sample"].source == "project"
    assert by_name["sample"].description == "Project-overridden sample"


def test_global_only_template_appends(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    path = _write_global(tmp_path, "house-style", "Global house style")

    templates = ReviewTemplate.load_all(
        plugin_root, get_fixture_path("vault-empty"), tmp_path
    )
    by_name = {t.name: t for t in templates}
    assert by_name["house-style"].source == "global"
    assert by_name["house-style"].path == path


def test_no_home_dir_skips_global_tier(tmp_path: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    _ = _write_global(tmp_path, "house-style", "Global house style")

    templates = ReviewTemplate.load_all(plugin_root, get_fixture_path("vault-empty"))
    assert all(t.source == "core" for t in templates)
    assert "house-style" not in {t.name for t in templates}
