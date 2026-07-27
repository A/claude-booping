from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_xdg_config_home(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Path]:
    """Isolate HOME and XDG_CONFIG_HOME so no test touches the developer's real machine.

    - XDG_CONFIG_HOME → per-test tmp dir, so the real global config
      (${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml) never leaks in. The yielded
      value is this xdg path (tests that write a global config use it directly).
    - HOME → per-test tmp dir, so vault resolution (`~/Claude/{project}` via
      `Path.expanduser()`) and the best-effort `.booping.log` writer land under tmp
      rather than the real `~/Claude` — even when a command resolves the repo's own
      `.booping` marker from pytest's cwd.

    autouse — every test gets isolation without opting in. A test that needs a global
    config writes it under `<xdg>/booping/config.yaml`; a test that needs its own HOME
    monkeypatches it again (last setenv wins).
    """
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    xdg = tmp_path_factory.mktemp("xdg-config")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg))
    yield xdg
