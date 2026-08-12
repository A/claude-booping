"""The hook a consumer implements to configure the txtar runner."""

from __future__ import annotations

import pytest

from pytest_txtar.case import TxtarSpec


@pytest.hookspec(firstresult=True)
def pytest_txtar_spec(config: pytest.Config) -> TxtarSpec | None:
    """Return the TxtarSpec for this test session."""
