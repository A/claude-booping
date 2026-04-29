from booping.context.config import Config
from tests.helpers import get_fixture_path


def test_core_only() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    config = Config.load(plugin_root)
    assert config["sprint"]["default_threshold_sp"] == 35
    assert config["sprint"]["redecompose_threshold"] == 5


def test_project_override_deep_merge() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-with-config-override")
    config = Config.load(plugin_root, [vault / "config.yaml"])
    assert config["sprint"]["default_threshold_sp"] == 50
    assert config["sprint"]["redecompose_threshold"] == 5


def test_list_replacement() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-with-config-override")
    config = Config.load(plugin_root, [vault / "config.yaml"])
    # vault override has no tasks key, so core tasks remain
    assert len(config["tasks"]) == 2


def test_ordered_override_paths() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        override1 = Path(tmp) / "o1.yaml"
        override2 = Path(tmp) / "o2.yaml"
        override1.write_text("sprint:\n  default_threshold_sp: 20\n")
        override2.write_text("sprint:\n  default_threshold_sp: 99\n")
        config = Config.load(plugin_root, [override1, override2])
    assert config["sprint"]["default_threshold_sp"] == 99