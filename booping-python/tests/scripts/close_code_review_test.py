"""Tests for the `code-review` playbook's exit hook script.

The script is plugin-shipped and stdlib-only, so it is exercised as a subprocess the
way `booping playbook-transition` runs it: cwd and `BOOPING_WORKDIR` at the vault root,
`BOOPING_ARTIFACT` at the resolved review.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "playbooks"
    / "code-review"
    / "_scripts"
    / "close-code-review"
)

REVIEW_REL = "codereviews/20260809_plan/202608091453.md"
PLAN_REL = "plans/20260809_plan/index.md"


def _vault(tmp_path: Path, plan_frontmatter: str) -> Path:
    vault = tmp_path / "vault"
    review = vault / REVIEW_REL
    review.parent.mkdir(parents=True)
    review.write_text(f"---\nplan: {PLAN_REL}\nstatus: human-review\n---\n\n# Review\n")

    plan = vault / PLAN_REL
    plan.parent.mkdir(parents=True)
    plan.write_text(f"---\ntitle: Foo\n{plan_frontmatter}\nstatus: done\n---\n\n# Foo\n")
    return vault


def _run(vault: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=vault,
        env={
            "PATH": "/usr/bin:/bin",
            "BOOPING_WORKDIR": str(vault),
            "BOOPING_ARTIFACT": str(vault / REVIEW_REL),
        },
        capture_output=True,
        text=True,
    )


def _code_reviews(plan: Path) -> list[str]:
    lines = plan.read_text().partition("\n---\n")[0].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("code_reviews:"))
    end = start + 1
    while end < len(lines) and lines[end].lstrip().startswith("- "):
        end += 1
    return [line.lstrip()[2:].strip() for line in lines[start + 1 : end]]


class Case(NamedTuple):
    frontmatter: str
    expected: list[str]


CASES = {
    # the regression: an empty inline list is empty, not an element named "[]"
    "empty-inline-list": Case("code_reviews: []", [REVIEW_REL]),
    "null-scalar": Case("code_reviews: null", [REVIEW_REL]),
    "tilde-scalar": Case("code_reviews: ~", [REVIEW_REL]),
    "key-absent": Case("sp: 4", [REVIEW_REL]),
    "populated-block-list": Case(
        "code_reviews:\n  - codereviews/20260809_plan/202608081200.md",
        ["codereviews/20260809_plan/202608081200.md", REVIEW_REL],
    ),
    "populated-inline-list": Case(
        "code_reviews: [codereviews/20260809_plan/202608081200.md]",
        ["codereviews/20260809_plan/202608081200.md", REVIEW_REL],
    ),
}


@pytest.mark.parametrize("case", CASES.values(), ids=list(CASES))
def test_review_is_appended_as_its_own_element(tmp_path: Path, case: Case) -> None:
    vault = _vault(tmp_path, case.frontmatter)

    result = _run(vault)

    assert result.returncode == 0, result.stderr
    assert _code_reviews(vault / PLAN_REL) == case.expected


def test_an_already_linked_review_is_not_duplicated(tmp_path: Path) -> None:
    vault = _vault(tmp_path, f"code_reviews:\n  - {REVIEW_REL}")

    result = _run(vault)

    assert result.returncode == 0, result.stderr
    assert _code_reviews(vault / PLAN_REL) == [REVIEW_REL]
    assert "already linked to" in result.stdout


def test_the_body_and_the_other_keys_survive(tmp_path: Path) -> None:
    vault = _vault(tmp_path, "code_reviews: []")

    assert _run(vault).returncode == 0

    text = (vault / PLAN_REL).read_text()
    assert text.startswith("---\ntitle: Foo\n")
    assert "\nstatus: done\n" in text
    assert text.endswith("---\n\n# Foo\n")


def test_a_missing_plan_aborts_the_transition(tmp_path: Path) -> None:
    vault = _vault(tmp_path, "code_reviews: []")
    (vault / PLAN_REL).unlink()

    result = _run(vault)

    assert result.returncode != 0
    assert "plan referenced by `plan:` not found" in result.stderr
