"""Booping's configuration for the pytest-txtar runner — see README.md."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_txtar.case import TxtarSpec

REPO_ROOT = Path(__file__).resolve().parents[2]


def pytest_txtar_spec(config: pytest.Config) -> TxtarSpec:
    return TxtarSpec(
        commands={"booping": REPO_ROOT / "bin" / "booping"},
        roots=("home", "xdg", "cwd"),
        cwd_root="cwd",
        env={"HOME": "home", "XDG_CONFIG_HOME": "xdg"},
    )
