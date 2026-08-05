from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from booping.context import config as config_mod
from booping.query import QuerySpec, build_spec, resolve_spec
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


def test_unknown_keys_load_without_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No key is schema-checked: an invented playbook block loads verbatim."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    override_path = tmp_path / "config.yaml"
    override_path.write_text(
        yaml.dump(
            {
                "core": {
                    "my_playbook": {
                        "whatever": {"agents": {"x": {"bogus": "field"}}},
                    }
                }
            }
        )
    )
    cfg = config_mod.load(plugin_root, [override_path])
    assert cfg["core"]["my_playbook"]["whatever"]["agents"]["x"] == {"bogus": "field"}  # type: ignore[index]
    assert capsys.readouterr().err == ""


def test_loader_does_not_filter_internal_when_disable_flag_set(tmp_path: Path) -> None:
    plugin_root = Path(__file__).resolve().parents[3]
    override_path = tmp_path / "config.yaml"
    override_path.write_text(
        yaml.dump({"core": {"develop_playbook": {"disable_internal_agents": True}}})
    )
    cfg = config_mod.load(plugin_root, [override_path])
    agents = cfg["core"]["develop_playbook"]["agents"]  # type: ignore[index]
    assert "booping-developer" in agents
    assert "booping-researcher" in agents


def test_agent_entry_replaces_wholesale(tmp_path: Path) -> None:
    """Project override of `core.<name>_playbook.agents.<id>` replaces the entry, not deep-merges.

    The core entry's `internal: true` must NOT leak into the override.
    """
    plugin_root = Path(__file__).resolve().parents[3]
    override_path = tmp_path / "config.yaml"
    override_path.write_text(
        yaml.dump(
            {
                "core": {
                    "develop_playbook": {
                        "agents": {
                            "booping-developer": {
                                "good_for": ["overridden"],
                                "bad_for": ["nothing"],
                            }
                        }
                    }
                }
            }
        )
    )
    cfg = config_mod.load(plugin_root, [override_path])
    entry = cfg["core"]["develop_playbook"]["agents"]["booping-developer"]  # type: ignore[index]
    assert entry == {
        "good_for": ["overridden"],
        "bad_for": ["nothing"],
    }
    # Sibling agent stays untouched.
    assert cfg["core"]["develop_playbook"]["agents"]["booping-researcher"]["internal"] is True  # type: ignore[index]


def test_ordered_override_paths_signature() -> None:
    """Verify function accepts a list of override paths (multiple entries)."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    cfg = config_mod.load(plugin_root, [Path("/nonexistent1.yaml"), Path("/nonexistent2.yaml")])
    assert cfg["sprint"]["default_threshold_sp"] == 35  # type: ignore[index]


def test_global_config_path_isolated_by_autouse_conftest() -> None:
    """Canary: the autouse conftest fixture redirects XDG_CONFIG_HOME to a tmp dir,
    so global_config_path() reflects it *without any explicit fixture request* here."""
    xdg = os.environ["XDG_CONFIG_HOME"]
    assert config_mod.global_config_path() == Path(xdg) / "booping" / "config.yaml"
    # And it is NOT the developer's real ~/.config location.
    assert config_mod.global_config_path() != Path.home() / ".config" / "booping" / "config.yaml"


def test_global_config_path_falls_back_to_dot_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert config_mod.global_config_path() == Path.home() / ".config" / "booping" / "config.yaml"


def _write_global(xdg: Path, data: dict[str, object]) -> Path:
    path = xdg / "booping" / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data))
    return path


def test_merge_order_core_global_project(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """core (35) → global (99) → project (50): each tier overrides the previous."""
    plugin_root = get_fixture_path("plugin-root-minimal")
    global_path = _write_global(
        isolated_xdg_config_home, {"sprint": {"default_threshold_sp": 99}}
    )
    # global overrides core
    cfg = config_mod.load(plugin_root, [global_path])
    assert cfg["sprint"]["default_threshold_sp"] == 99  # type: ignore[index]
    # project overrides global
    project_path = tmp_path / "config.yaml"
    project_path.write_text(yaml.dump({"sprint": {"default_threshold_sp": 50}}))
    cfg = config_mod.load(plugin_root, [global_path, project_path])
    assert cfg["sprint"]["default_threshold_sp"] == 50  # type: ignore[index]


def test_agents_shallow_merge_across_three_tiers(
    tmp_path: Path, isolated_xdg_config_home: Path
) -> None:
    """`agents` blocks shallow-merge across core, global, and project tiers."""
    plugin_root = Path(__file__).resolve().parents[3]
    global_path = _write_global(
        isolated_xdg_config_home,
        {"core": {"develop_playbook": {"agents": {"g-agent": {"good_for": ["g"]}}}}},
    )
    project_path = tmp_path / "config.yaml"
    project_path.write_text(
        yaml.dump(
            {"core": {"develop_playbook": {"agents": {"p-agent": {"good_for": ["p"]}}}}}
        )
    )
    cfg = config_mod.load(plugin_root, [global_path, project_path])
    agents = cfg["core"]["develop_playbook"]["agents"]  # type: ignore[index]
    assert "booping-developer" in agents  # core preserved
    assert "g-agent" in agents  # global tier added
    assert "p-agent" in agents  # project tier added


def test_project_tier_macros_merge_like_any_other_key(
    tmp_path: Path, isolated_xdg_config_home: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    global_path = _write_global(
        isolated_xdg_config_home, {"core": {"macros": {"now": ["echo", "global"]}}}
    )
    project_path = tmp_path / "config.yaml"
    project_path.write_text(
        yaml.dump(
            {
                "core": {"macros": {"now": ["echo", "project"], "extra": ["echo", "x"]}},
                "sprint": {"default_threshold_sp": 50},
            }
        )
    )

    cfg = config_mod.load(plugin_root, [global_path, project_path])

    assert cfg["core"]["macros"] == {  # type: ignore[index]
        "now": ["echo", "project"],
        "extra": ["echo", "x"],
    }
    assert cfg["sprint"]["default_threshold_sp"] == 50  # type: ignore[index]
    assert capsys.readouterr().err == ""


def test_missing_global_file_silently_skipped(isolated_xdg_config_home: Path) -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    missing = isolated_xdg_config_home / "booping" / "config.yaml"
    assert not missing.exists()
    cfg = config_mod.load(plugin_root, [missing])
    assert cfg["sprint"]["default_threshold_sp"] == 35  # type: ignore[index]


CORE_QUERY_PATHS = [
    "core.code_review_playbook.queries.review_candidates",
    "core.code_review_playbook.queries.scope_candidates",
    "core.retro_playbook.queries.candidates",
    "core.learn_playbook.queries.candidates",
    "core.groom_playbook.queries.latest_plans",
]


def _core_config() -> dict[str, object]:
    return config_mod.load(Path(__file__).resolve().parents[3], [])


def test_plans_glob_is_the_single_directory_shape() -> None:
    assert _core_config()["core"]["plans"]["glob"] == ["plans/*/index.md"]  # type: ignore[index]


@pytest.mark.parametrize("dotted", CORE_QUERY_PATHS)
def test_each_consumer_spec_resolves_to_a_spec_mapping(dotted: str) -> None:
    spec = resolve_spec(_core_config(), dotted)
    assert isinstance(spec, dict)
    assert set(spec) <= {"glob", "where", "sort", "columns"}
    assert QuerySpec(**spec) is not None


@pytest.mark.parametrize("dotted", CORE_QUERY_PATHS)
def test_a_spec_omitting_glob_falls_back_to_core_plans_glob(dotted: str) -> None:
    cfg = _core_config()
    spec = build_spec(cfg, resolve_spec(cfg, dotted))
    assert spec.glob == cfg["core"]["plans"]["glob"]  # type: ignore[index]


def test_a_spec_declaring_glob_keeps_it() -> None:
    cfg = _core_config()
    spec = build_spec(cfg, {"glob": ["notes/*.md"]})
    assert spec.glob == ["notes/*.md"]
