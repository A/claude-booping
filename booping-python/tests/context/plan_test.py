from __future__ import annotations

from datetime import date

from booping.context.plan import Plan
from tests.helpers import get_fixture_path


def test_load_all_count_and_fields() -> None:
    vault = get_fixture_path("vault-full")
    plans = Plan.load_all(vault)
    assert len(plans) == 2

    # First plan sorted by filename: 20260101-add-search-feature.md
    plan = plans[0]
    assert plan.title == "Add search feature"
    assert plan.type == "feature"
    assert plan.status == "in-progress"
    assert plan.sp == 5
    assert plan.created == date(2026, 1, 1)
    assert plan.goal == "Implement full-text search across the widget catalog."
    assert plan.business_goal == "Users can find widgets faster via keyword search."
    assert plan.split_from is None


def test_load_all_missing_plans_dir() -> None:
    vault = get_fixture_path("vault-empty")
    plans = Plan.load_all(vault)
    assert plans == []


def test_load_all_second_plan() -> None:
    vault = get_fixture_path("vault-full")
    plans = Plan.load_all(vault)
    plan = plans[1]
    assert plan.title == "Fix login timeout bug"
    assert plan.type == "bug"
    assert plan.status == "ready-for-dev"
    assert plan.sp == 2
