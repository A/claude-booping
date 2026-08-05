from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from booping.logger import log


def test_log_noop_when_vault_is_none() -> None:
    log(vault=None, subcommand="render", message="foo.j2")


def test_log_appends_one_line(tmp_path: Path) -> None:
    message = "foo.j2"
    log(vault=tmp_path, subcommand="render", message=message)
    log_file = tmp_path / "_booping" / ".booping.log"
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    assert "[render]" in lines[0]
    assert message in lines[0]


def test_log_appends_not_overwrites(tmp_path: Path) -> None:
    log(vault=tmp_path, subcommand="render", message="first.j2")
    log(vault=tmp_path, subcommand="query", message="→ 3 rows")
    log_file = tmp_path / "_booping" / ".booping.log"
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 2
    assert "[render]" in lines[0] and "first.j2" in lines[0]
    assert "[query]" in lines[1] and "→ 3 rows" in lines[1]


def test_log_empty_message_no_trailing_space(tmp_path: Path) -> None:
    log(vault=tmp_path, subcommand="render", message="")
    log_file = tmp_path / "_booping" / ".booping.log"
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    assert lines[0].endswith("]")
    assert "] " not in lines[0]


def test_log_creates_parent_directory(tmp_path: Path) -> None:
    log(vault=tmp_path, subcommand="render", message="foo.j2")
    assert (tmp_path / "_booping" / ".booping.log").exists()


def test_render_subprocess_integration_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".booping").touch()

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
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[render\] .+$", lines[0])
