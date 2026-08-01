from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from booping.context.plan import Plan
from tests.helpers import get_fixture_path


def _write_plan(path: Path, title: str, status: str = "in-spec") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntype: feature\nstatus: {status}\n---\n\n# Body\n"
    )


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
    assert plan.summary == "Users can find widgets faster via keyword search."
    assert plan.split_from is None
    assert plan.commit == "0123456789abcdef0123456789abcdef01234567"


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
    assert plan.commit is None


def test_load_all_mixed_flat_and_directory_plans(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    _write_plan(plans / "20260101-flat.md", "Flat")
    _write_plan(plans / "20260102-stub.md", "Stub", status="backlog")
    _write_plan(plans / "20260103-dir" / "plan.md", "Directory")
    (plans / "20260103-dir" / "notes.md").write_text("scratch\n")

    loaded = Plan.load_all(tmp_path)

    assert [p.slug for p in loaded] == [
        "20260101-flat",
        "20260102-stub",
        "20260103-dir",
    ]
    assert [p.title for p in loaded] == ["Flat", "Stub", "Directory"]
    assert [p.rel_link for p in loaded] == [
        "plans/20260101-flat.md",
        "plans/20260102-stub.md",
        "plans/20260103-dir/plan.md",
    ]


def test_load_all_directory_plan_wins_collision(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plans = tmp_path / "plans"
    _write_plan(plans / "20260101-foo.md", "Flat foo")
    _write_plan(plans / "20260101-foo" / "plan.md", "Directory foo")

    loaded = Plan.load_all(tmp_path)

    assert len(loaded) == 1
    assert loaded[0].title == "Directory foo"
    assert loaded[0].rel_link == "plans/20260101-foo/plan.md"

    err = capsys.readouterr().err
    assert "20260101-foo.md" in err
    assert "20260101-foo/plan.md" in err
