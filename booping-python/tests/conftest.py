from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_xdg_config_home(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Path]:
    """Point XDG_CONFIG_HOME at a per-test tmp dir so the dev machine's real global
    config (${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml) never leaks into tests.

    autouse — every test gets isolation without opting in. A test that needs a global
    config writes it under `<xdg>/booping/config.yaml`.
    """
    xdg = tmp_path_factory.mktemp("xdg-config")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    yield xdg
