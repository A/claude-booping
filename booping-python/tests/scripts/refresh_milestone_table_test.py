"""Tests for the `develop` playbook's milestone-table hook script.

The script shells back into `booping`, so it is exercised as a subprocess the way
`booping playbook-transition` runs it — the plan directory as argv, inside a project
whose vault config can redirect the milestone glob and columns.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "playbooks"
    / "develop"
    / "_scripts"
    / "refresh-milestone-table"
)

INDEX = """---
title: Demo
sp: 99
status: in-progress
---

# Demo

## Context

Prose that must survive | pipes and all.

## Milestones

| id | title |
| --- | --- |
| 01 | stale row |

## Final Verification

`just ci` green.
"""

MILESTONES = {
    "M01-first-thing": ('"01"', "First thing", 3, "pending"),
    "M02-second": ('"02"', "Second", 2, "done"),
}


def _project(tmp_path: Path, *, config: str = "", milestone_dir: str = "milestones") -> Path:
    repo = tmp_path / "repo"
    (repo / "vault").mkdir(parents=True)
    (repo / ".booping").write_text("project_name: demo\nvault_path: vault\n")
    if config:
        (repo / "vault" / "config.yaml").write_text(config)

    plan = repo / "vault" / "plans" / "demo"
    (plan / milestone_dir).mkdir(parents=True)
    (plan / "index.md").write_text(INDEX)
    for name, (ident, title, sp, status) in MILESTONES.items():
        milestone = plan / milestone_dir / name
        milestone.mkdir()
        (milestone / f"{name}.md").write_text(
            f"---\nid: {ident}\ntitle: {title}\nsp: {sp}\nstatus: {status}\n"
            f"plan: plans/demo/index.md\n---\n\n# {title}\n"
        )
        (milestone / "feedback.md").write_text("---\nsp: 100\n---\n\nsidecar\n")
    return plan


def _run(plan: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, XDG_CONFIG_HOME=str(tmp_path / "xdg"))
    return subprocess.run(
        [str(SCRIPT), str(plan)], env=env, capture_output=True, text=True, check=False
    )


def _section(text: str, heading: str) -> str:
    body = text.split(f"\n{heading}\n", 1)[1]
    return body.split("\n## ", 1)[0].strip()


def test_renders_one_row_per_milestone_file(tmp_path: Path) -> None:
    plan = _project(tmp_path)
    result = _run(plan, tmp_path)

    assert result.returncode == 0, result.stderr
    assert _section((plan / "index.md").read_text(), "## Milestones") == (
        "| id | title | sp | status |\n"
        "| --- | --- | --- | --- |\n"
        "| 01 | [First thing](milestones/M01-first-thing/M01-first-thing.md) | 3 | pending |\n"
        "| 02 | [Second](milestones/M02-second/M02-second.md) | 2 | done |"
    )


def test_leaves_the_surrounding_sections_untouched(tmp_path: Path) -> None:
    plan = _project(tmp_path)
    _run(plan, tmp_path)

    text = (plan / "index.md").read_text()
    assert _section(text, "## Context") == "Prose that must survive | pipes and all."
    assert _section(text, "## Final Verification") == "`just ci` green."
    assert text.startswith("---\ntitle: Demo\n")


def test_stamps_sp_with_the_sum_of_the_milestone_files(tmp_path: Path) -> None:
    plan = _project(tmp_path)
    _run(plan, tmp_path)

    assert "\nsp: 5\n" in (plan / "index.md").read_text()


def test_writes_the_table_into_a_section_that_has_none(tmp_path: Path) -> None:
    plan = _project(tmp_path)
    (plan / "index.md").write_text(
        INDEX.replace("| id | title |\n| --- | --- |\n| 01 | stale row |\n\n", "")
    )
    result = _run(plan, tmp_path)

    assert result.returncode == 0, result.stderr
    row = "| 01 | [First thing](milestones/M01-first-thing/M01-first-thing.md) | 3 | pending |"
    assert row in _section((plan / "index.md").read_text(), "## Milestones")


def test_second_run_changes_nothing(tmp_path: Path) -> None:
    plan = _project(tmp_path)
    _run(plan, tmp_path)
    once = (plan / "index.md").read_text()
    _run(plan, tmp_path)

    assert (plan / "index.md").read_text() == once


def test_follows_the_glob_and_columns_the_config_declares(tmp_path: Path) -> None:
    plan = _project(
        tmp_path,
        milestone_dir="stages",
        config="core:\n  plans:\n    milestones:\n"
        "      glob: stages/*/M*.md\n      table_columns: [title, status]\n",
    )
    result = _run(plan, tmp_path)

    assert result.returncode == 0, result.stderr
    assert _section((plan / "index.md").read_text(), "## Milestones") == (
        "| title | status |\n"
        "| --- | --- |\n"
        "| [First thing](stages/M01-first-thing/M01-first-thing.md) | pending |\n"
        "| [Second](stages/M02-second/M02-second.md) | done |"
    )


@pytest.mark.parametrize("removed", ["milestones", "index.md"])
def test_reports_the_plan_dir_and_writes_nothing_when_a_piece_is_missing(
    tmp_path: Path, removed: str
) -> None:
    plan = _project(tmp_path)
    before = (plan / "index.md").read_text()
    for path in sorted((plan / removed).rglob("*"), reverse=True) + [plan / removed]:
        path.rmdir() if path.is_dir() else path.unlink()

    result = _run(plan, tmp_path)

    assert result.returncode != 0
    assert str(plan) in result.stderr
    if removed != "index.md":
        assert (plan / "index.md").read_text() == before
