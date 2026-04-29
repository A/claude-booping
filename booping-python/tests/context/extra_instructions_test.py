from __future__ import annotations

from booping.context import extra_instructions as ei_mod
from tests.helpers import get_fixture_path


def test_load_from_vault_full() -> None:
    vault = get_fixture_path("vault-full")
    ei = ei_mod.load(vault)
    assert "skill_groom" in ei
    assert "Always link new plans" in ei["skill_groom"]


def test_absent_key_not_in_dict() -> None:
    vault = get_fixture_path("vault-full")
    ei = ei_mod.load(vault)
    assert "skill_chat" not in ei


def test_empty_vault_returns_empty_dict() -> None:
    vault = get_fixture_path("vault-empty")
    ei = ei_mod.load(vault)
    assert ei == {}
