from __future__ import annotations

from datetime import date

from booping.context.retro import Retro
from tests.helpers import get_fixture_path


def test_load_all_count_and_fields() -> None:
    vault = get_fixture_path("vault-full")
    retros = Retro.load_all(vault)
    assert len(retros) == 1

    retro = retros[0]
    assert retro.plan == "20260101-add-search-feature"
    assert retro.goal == "Delivered search MVP on time with good test coverage."
    assert retro.created == date(2026, 1, 31)
    assert "What went well" in retro.body


def test_load_all_missing_retros_dir() -> None:
    vault = get_fixture_path("vault-empty")
    retros = Retro.load_all(vault)
    assert retros == []
