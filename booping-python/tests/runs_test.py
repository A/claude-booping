from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from booping import macros, runs
from booping.context import Context
from booping.context._yaml import parse_frontmatter_only
from booping.runs import effective_status

BOOPING = Path(__file__).resolve().parents[2] / "bin" / "booping"
DEADLINE = 30.0

RECORD = """---
id: {id}
playbook: develop
mode: supervised
target:
- plans/p1/index.md
plan: plans/p1/index.md
items: []
status: running
pid: {pid}
session_id: 00000000-0000-0000-0000-000000000000
log: runs/{id}.log
started_at: 2026-10-15 12:00
ended_at: null
exit_code: null
acked_at: null
---

# {id}
"""


def _project(root: Path, command: str) -> Path:
    (root / ".booping").write_text(
        "project_name: probe\nvault_path: ./vault\nlatest_migration: 9999\n"
    )
    vault = root / "vault"
    (vault / "plans" / "p1").mkdir(parents=True)
    (vault / "plans" / "p1" / "index.md").write_text("---\ntitle: P1\n---\n")
    (vault / "config.yaml").write_text(f"core:\n  run:\n    command: {command}\n")
    return vault


def _env(root: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_SESSION_ID"}
    env["HOME"] = str(root / "home")
    env["XDG_CONFIG_HOME"] = str(root / "xdg")
    return env


def _wait_for(predicate: Callable[[], object], what: str) -> None:
    end = time.monotonic() + DEADLINE
    while not predicate():
        if time.monotonic() > end:
            pytest.fail(f"timed out waiting for {what}")
        time.sleep(0.05)


def _gone(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def _impossible_pid() -> int:
    return int(Path("/proc/sys/kernel/pid_max").read_text()) + 1


def test_sigterm_to_the_wrapper_ends_the_child_and_records_143(tmp_path: Path) -> None:
    vault = _project(tmp_path, "[sh, -c, 'echo $$ > child.pid; exec sleep 60', fake]")
    wrapper = subprocess.Popen(
        [str(BOOPING), "run", "develop", "vault/plans/p1"],
        cwd=tmp_path,
        env=_env(tmp_path),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    child_pid_file = tmp_path / "child.pid"
    _wait_for(lambda: child_pid_file.is_file() and child_pid_file.read_text().strip(), "child")
    records = list((vault / "runs").glob("*.md"))
    assert len(records) == 1
    running = parse_frontmatter_only(records[0])
    assert running["status"] == "running"

    os.kill(running["pid"], signal.SIGTERM)
    wrapper.communicate(timeout=DEADLINE)

    assert wrapper.returncode == 143
    record = parse_frontmatter_only(records[0])
    assert record["status"] == "failed"
    assert record["exit_code"] == 143
    assert record["pid"] is None
    assert _gone(int(child_pid_file.read_text()))


def test_effective_status_running_with_a_live_pid_is_running() -> None:
    assert effective_status({"status": "running", "pid": os.getpid()}) == "running"


def test_effective_status_running_with_a_dead_pid_is_lost() -> None:
    assert effective_status({"status": "running", "pid": _impossible_pid()}) == "lost"


def test_effective_status_running_without_a_pid_is_lost() -> None:
    assert effective_status({"status": "running", "pid": None}) == "lost"


def test_effective_status_keeps_a_finished_status() -> None:
    assert effective_status({"status": "finished", "pid": None}) == "finished"


def test_ack_of_a_running_record_exits_1_and_writes_nothing(tmp_path: Path) -> None:
    vault = _project(tmp_path, "[true]")
    runs = vault / "runs"
    runs.mkdir()
    record = runs / "r1.md"
    text = RECORD.format(id="r1", pid=os.getpid())
    record.write_text(text)

    result = subprocess.run(
        [str(BOOPING), "run", "ack", "r1"],
        cwd=tmp_path,
        env=_env(tmp_path),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "error: run r1 is still running\n"
    assert record.read_text() == text


def test_now_is_fresh_on_every_call(monkeypatch: pytest.MonkeyPatch) -> None:
    macros.clear_cache()
    stamps = iter(["2026-10-15 12:00\n", "2026-10-15 12:07\n"])

    def ticking_run(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, next(stamps), "")

    monkeypatch.setattr(macros.subprocess, "run", ticking_run)
    ctx = Context(config={"core": {"macros": {"date": ["date"]}}})

    assert runs._now(ctx, runs.STAMP_DATE) == "2026-10-15 12:00"  # pyright: ignore[reportPrivateUsage]
    assert runs._now(ctx, runs.STAMP_DATE) == "2026-10-15 12:07"  # pyright: ignore[reportPrivateUsage]
