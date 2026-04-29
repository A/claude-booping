from booping.context.retro import Retro
from tests.helpers import get_fixture_path


def test_load_all_from_vault_full() -> None:
    vault = get_fixture_path("vault-full")
    retros = Retro.load_all(vault)
    assert len(retros) == 1

    retro = retros[0]
    assert retro.plan == "plans/20260401-add-user-auth.md"
    assert retro.goal == "success"
    assert "Auth shipped" in retro.body


def test_load_all_missing_dir() -> None:
    retros = Retro.load_all(get_fixture_path("vault-full") / "nonexistent")
    assert retros == []