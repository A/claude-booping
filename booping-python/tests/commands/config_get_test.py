from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BOOPING_BIN), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_scalar_string_prints_raw_single_line(tmp_path: Path) -> None:
    # Runs outside any project (tmp cwd has no `.booping`) — core+global only.
    result = _run("config-get", "home_dir", cwd=tmp_path)
    assert result.returncode == 0
    # Raw value from config, unexpanded, no quoting, trailing newline only.
    assert result.stdout == "~/Claude/\n"
    assert result.stderr == ""


def test_scalar_int_dotted_path(tmp_path: Path) -> None:
    result = _run("config-get", "sprint.default_threshold_sp", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == "35"
    assert result.stdout.endswith("\n")


def test_mapping_prints_yaml(tmp_path: Path) -> None:
    result = _run("config-get", "plan.statuses", cwd=tmp_path)
    assert result.returncode == 0
    parsed = yaml.safe_load(result.stdout)
    assert isinstance(parsed, dict)
    assert "backlog" in parsed


def test_missing_key_exits_1_nothing_on_stdout(tmp_path: Path) -> None:
    result = _run("config-get", "no.such.key", cwd=tmp_path)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "no.such.key" in result.stderr


def test_missing_top_level_key(tmp_path: Path) -> None:
    result = _run("config-get", "nope", cwd=tmp_path)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "key not found" in result.stderr


def test_global_tier_merges(tmp_path: Path, isolated_xdg_config_home: Path) -> None:
    # The autouse fixture points XDG_CONFIG_HOME at isolated_xdg_config_home, which
    # the subprocess inherits. A global config value there overrides core.
    booping_cfg = isolated_xdg_config_home / "booping"
    booping_cfg.mkdir(parents=True, exist_ok=True)
    (booping_cfg / "config.yaml").write_text("home_dir: ~/Vaults/\n")
    result = _run("config-get", "home_dir", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout == "~/Vaults/\n"


def test_help_lists_subcommand(tmp_path: Path) -> None:
    result = _run("--help", cwd=tmp_path)
    assert result.returncode == 0
    assert "config-get" in result.stdout
