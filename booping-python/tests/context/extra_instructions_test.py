from booping.context.extra_instructions import ExtraInstructions
from tests.helpers import get_fixture_path


def test_load_from_vault_full() -> None:
    vault = get_fixture_path("vault-full")
    result = ExtraInstructions.load(vault)
    assert "skill_groom" in result
    assert "grooming rules" in result["skill_groom"]
    assert "agent_booping-developer" in result
    assert "test suite" in result["agent_booping-developer"]


def test_absent_vault_yields_empty() -> None:
    result = ExtraInstructions.load(None)
    assert result == {}


def test_missing_dir_yields_empty() -> None:
    result = ExtraInstructions.load(get_fixture_path("vault-empty"))
    assert result == {}