from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from booping.logging import log_invocation


def test_log_invocation_noop_when_vault_is_none() -> None:
    log_invocation(vault=None, subcommand="render", detail="foo.j2")
    # No assertion needed; the call must not raise.


def test_log_invocation_appends_one_line(tmp_path: Path) -> None:
    log_invocation(vault=tmp_path, subcommand="render", detail="foo.j2")
    log_file = tmp_path / "_booping" / ".booping.log"
    assert log_file.exists()
    content = log_file.read_text()
    lines = content.strip().splitlines()
    assert len(lines) == 1
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[render\] foo\.j2$", lines[0])


def test_log_invocation_appends_not_overwrites(tmp_path: Path) -> None:
    log_invocation(vault=tmp_path, subcommand="render", detail="first.j2")
    log_invocation(vault=tmp_path, subcommand="render-sprints", detail="→ sprints.md")
    log_file = tmp_path / "_booping" / ".booping.log"
    content = log_file.read_text()
    lines = content.strip().splitlines()
    assert len(lines) == 2
    assert "[render] first.j2" in lines[0]
    assert "[render-sprints] → sprints.md" in lines[1]


def test_log_invocation_empty_detail_no_trailing_space(tmp_path: Path) -> None:
    log_invocation(vault=tmp_path, subcommand="render", detail="")
    log_file = tmp_path / "_booping" / ".booping.log"
    content = log_file.read_text()
    lines = content.strip().splitlines()
    assert len(lines) == 1
    assert lines[0].endswith("]")
    # Ensure there is no trailing space before the closing bracket
    assert "] " not in lines[0]


def test_log_invocation_creates_parent_directory(tmp_path: Path) -> None:
    # Do NOT pre-create _booping/
    log_invocation(vault=tmp_path, subcommand="render", detail="foo.j2")
    log_file = tmp_path / "_booping" / ".booping.log"
    assert log_file.exists()


def test_render_subprocess_integration_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invoking bin/booping render via subprocess writes one [render] line to the log."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".booping").touch()

    # Point HOME at tmp_path so Project.load_cwd() resolves vault under tmp_path/Claude/
    monkeypatch.setenv("HOME", str(tmp_path))

    plugin_root = Path(__file__).resolve().parents[2]
    booping_bin = plugin_root / "bin" / "booping"

    result = subprocess.run(
        [str(booping_bin), "render", "src/templates/skills/chat.md.j2"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0

    log_file = tmp_path / "Claude" / "repo" / "_booping" / ".booping.log"
    assert log_file.is_file()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    assert re.match(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[render\] .+$",
        lines[0],
    ), f"unexpected log line: {lines[0]!r}"
