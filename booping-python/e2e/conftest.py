"""Booping's configuration for the pytest-txtar runner — see README.md."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from pytest_txtar.case import TxtarSpec

REPO_ROOT = Path(__file__).resolve().parents[2]

# Cases inherit this process's environment. A run inside a Claude Code session
# carries its session id, which `correction add` would follow into a transcript,
# so it is dropped; a case that needs one sets it on its own `cmd` line via
# `env CLAUDE_CODE_SESSION_ID=… booping …`, which is why `bin/` leads PATH.
os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
os.environ["PATH"] = f"{REPO_ROOT / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"


def pytest_txtar_spec(config: pytest.Config) -> TxtarSpec:
    return TxtarSpec(
        commands={"booping": REPO_ROOT / "bin" / "booping"},
        roots=("home", "xdg", "cwd"),
        cwd_root="cwd",
        env={"HOME": "home", "XDG_CONFIG_HOME": "xdg"},
    )
