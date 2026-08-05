from __future__ import annotations

import re
import subprocess
from pathlib import Path


def test_render_resolves_relative_path_against_plugin_root_not_cwd(
    tmp_path: Path,
) -> None:
    """Skill-load shells invoke `booping render src/templates/...` with cwd anywhere
    (typically the user's project repo or vault). The relative path must resolve
    against the plugin root, never the caller's cwd.
    """
    plugin_root = Path(__file__).resolve().parents[3]
    booping_bin = plugin_root / "bin" / "booping"

    result = subprocess.run(
        [str(booping_bin), "render", "src/templates/skills/playbook.md.j2"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "# booping — /playbook" in result.stdout


def _render(tmp_path: Path, body: str, *args: str) -> subprocess.CompletedProcess[str]:
    plugin_root = Path(__file__).resolve().parents[3]
    template = tmp_path / "probe.md.j2"
    template.write_text(body)
    return subprocess.run(
        [str(plugin_root / "bin" / "booping"), "render", str(template), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_render_set_override_wins_over_core_value(tmp_path: Path) -> None:
    result = _render(
        tmp_path,
        "{{ config.core.sprint.default_threshold_sp }}\n",
        "--set",
        "core.sprint.default_threshold_sp=7",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "7"


def test_render_set_override_repeated_pairs_later_wins(tmp_path: Path) -> None:
    result = _render(
        tmp_path,
        "{{ config.core.sprint.default_threshold_sp }}\n",
        "--set",
        "core.sprint.default_threshold_sp=7",
        "--set",
        "core.sprint.default_threshold_sp=9",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "9"


def test_render_set_deep_merges_leaving_siblings(tmp_path: Path) -> None:
    result = _render(
        tmp_path,
        "{{ config.core.sprint.default_threshold_sp }}"
        "|{{ config.core.sprint.scale | length > 0 }}\n",
        "--set",
        "core.sprint.default_threshold_sp=7",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "7|True"


def test_render_macro_runs_a_core_declared_macro(tmp_path: Path) -> None:
    result = _render(tmp_path, "{{ macro('core.macros.date', '+%Y%m%d-%H-%M') }}\n")
    assert result.returncode == 0
    assert re.fullmatch(r"\d{8}-\d{2}-\d{2}", result.stdout.strip())


def test_render_stub_macro_returns_the_literal(tmp_path: Path) -> None:
    result = _render(
        tmp_path,
        "{{ macro('core.macros.date') }}\n",
        "--stub-macro",
        "core.macros.date=19700101-00-00",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "19700101-00-00"


def test_render_stub_macro_key_may_carry_the_call_arguments(tmp_path: Path) -> None:
    result = _render(
        tmp_path,
        "{{ macro('core.macros.date', '+%Y%m%d%H%M') }}\n",
        "--stub-macro",
        "core.macros.date +%Y%m%d%H%M=197001010000",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "197001010000"


def test_render_stub_macro_malformed_pair_exits_1(tmp_path: Path) -> None:
    result = _render(tmp_path, "x\n", "--stub-macro", "nope")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "malformed --stub-macro pair" in result.stderr


def test_render_set_malformed_pair_exits_1(tmp_path: Path) -> None:
    result = _render(tmp_path, "x\n", "--set", "nope")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "malformed --set pair" in result.stderr


_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
_STOP = "**STOP — tell the user:** this project is behind on booping migrations"


def _behind_repo(tmp_path: Path) -> Path:
    """A repo whose marker carries no `latest_migration` — watermark -1, so behind."""
    (tmp_path / ".booping").write_text("project_name: probe\n")
    return tmp_path


def _render_playbook(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(_PLUGIN_ROOT / "bin" / "booping"), "render-playbook", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_render_gates_a_behind_vault(tmp_path: Path) -> None:
    result = _render(_behind_repo(tmp_path), "rendered body\n")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith(_STOP)
    assert "rendered body" not in result.stdout


def test_render_playbook_gates_a_behind_vault(tmp_path: Path) -> None:
    result = _render_playbook(_behind_repo(tmp_path), "groom")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith(_STOP)
    assert "## Playbook Steps" not in result.stdout


def test_render_playbook_migrate_is_exempt_from_the_gate(tmp_path: Path) -> None:
    result = _render_playbook(_behind_repo(tmp_path), "migrate")
    assert result.returncode == 0
    assert _STOP not in result.stdout
    assert "## Playbook Steps" in result.stdout


def test_render_playbook_migrate_step_is_exempt_from_the_gate(tmp_path: Path) -> None:
    """The step fetch is a separate process issued by a spawned sub-agent."""
    result = _render_playbook(_behind_repo(tmp_path), "migrate", "--step", "survey")
    assert result.returncode == 0
    assert _STOP not in result.stdout
    assert result.stdout.strip() != ""


def test_render_playbook_project_pins_the_marker_to_that_root(tmp_path: Path) -> None:
    """The fixture vault carries a current marker, so a pinned render is not gated
    even though the cwd's own repo is behind."""
    result = _render_playbook(
        _behind_repo(tmp_path),
        "retro",
        "--project",
        str(_PLUGIN_ROOT / "playbooks" / "_fixtures" / "vault"),
    )
    assert result.returncode == 0
    assert _STOP not in result.stdout
    assert "## Playbook Steps" in result.stdout
