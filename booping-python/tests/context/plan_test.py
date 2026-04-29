from booping.context.plan import Plan
from tests.helpers import get_fixture_path


def test_load_all_from_vault_full() -> None:
    vault = get_fixture_path("vault-full")
    plans = Plan.load_all(vault)
    assert len(plans) == 2

    assert plans[0].title == "Add user authentication"
    assert plans[0].type == "feature"
    assert plans[0].status == "in-progress"
    assert plans[0].sp == 5
    assert "OAuth2 login flow" in plans[0].body

    assert plans[1].title == "Fix login redirect bug"
    assert plans[1].type == "bug"
    assert plans[1].status == "backlog"
    assert plans[1].sp == 2
    assert "redirect after login" in plans[1].body


def test_load_all_missing_dir() -> None:
    plans = Plan.load_all(get_fixture_path("vault-full") / "nonexistent")
    assert plans == []