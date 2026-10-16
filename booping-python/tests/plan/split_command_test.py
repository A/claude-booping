from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from booping.cli import build_parser

FIXTURES = Path(__file__).parent / "__fixtures__"
REPO_ROOT = Path(__file__).resolve().parents[3]
REFRESH = REPO_ROOT / "playbooks" / "develop" / "_scripts" / "refresh-milestone-table"

INDEX = """\
---
title: "Demo"
status: drafting
sp: null
summary: null
---

# Demo
"""

M01 = """\
---
id: "01"
title: "Parser core"
sp: 3
status: pending
plan: "plans/demo/index.md"
---

# M01: Parser core

## Tasks

| Task | Description |
|------|-------------|
| 1.1 | Write `src/a.py` |

## Definition of Done

- [ ] parser exists

## References

- `src/b.py`

## Verify

```
pytest tests/a_test.py
```
"""

M02 = """\
---
id: "02"
title: "CLI wiring"
sp: 2
status: pending
plan: "plans/demo/index.md"
---

# M02: CLI wiring

## Tasks

- wire `src/cli.py`

## Definition of Done

- [ ] cli runs

## References

## Verify

`booping --help`
"""

SPLIT_INDEX = """\
---
title: "Demo"
status: drafting
sp: 5
summary: null
---

# Demo plan

## Context

Some context.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Parser core](milestones/M01-parser-core/M01-parser-core.md) | 3 | pending |
| 02 | [CLI wiring](milestones/M02-cli-wiring/M02-cli-wiring.md) | 2 | pending |

## Groups

| group | milestones | sp |
| --- | --- | --- |
| G1 | M01, M02 | 5 |

## Final Verification

- [ ] all green
"""

NO_SP_DRAFT = """\
# Plan

## Milestones

### M01 — Only step

#### Tasks

- do `a.py`
"""


def _booping(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    return 0


def _plan_dir(root: Path, draft: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    plan = root / "plans" / "demo"
    plan.mkdir(parents=True)
    (plan / "draft.md").write_text(draft, encoding="utf-8")
    monkeypatch.chdir(root)
    return plan


def _tree(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


def test_split_writes_milestones_and_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _plan_dir(tmp_path, (FIXTURES / "fixed.md").read_text(encoding="utf-8"), monkeypatch)
    (plan / "index.md").write_text(INDEX, encoding="utf-8")

    code = _booping(["plan", "split", "plans/demo/draft.md"])

    out = capsys.readouterr()
    assert code == 0
    assert out.out == (
        "M01-parser-core sp=3 sections=tasks:4,dod:2,references:2,verify:4\n"
        "M02-cli-wiring sp=2 sections=tasks:2,dod:2,references:0,verify:1\n"
        "group G1: M01, M02 (5 SP)\n"
    )
    assert out.err == ""
    m01 = plan / "milestones" / "M01-parser-core" / "M01-parser-core.md"
    m02 = plan / "milestones" / "M02-cli-wiring" / "M02-cli-wiring.md"
    assert m01.read_text(encoding="utf-8") == M01
    assert m02.read_text(encoding="utf-8") == M02
    assert (plan / "index.md").read_text(encoding="utf-8") == SPLIT_INDEX


def test_milestone_head_matches_the_scaffold_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _plan_dir(tmp_path, (FIXTURES / "fixed.md").read_text(encoding="utf-8"), monkeypatch)
    assert _booping(["plan", "split", "plans/demo/draft.md"]) == 0
    sets = ["id=01", "slug=parser-core", "title=Parser core", "sp=3", "plan=plans/demo/index.md"]
    argv = ["scaffold", "core.groom_playbook.milestone_scaffold", "ref"]
    assert _booping([*argv, *(x for s in sets for x in ("--set", s))]) == 0
    capsys.readouterr()

    scaffolded = (tmp_path / "ref" / "M01-parser-core" / "M01-parser-core.md").read_text()
    written = (plan / "milestones" / "M01-parser-core" / "M01-parser-core.md").read_text()
    head = scaffolded[: scaffolded.index("# M01: Parser core\n") + len("# M01: Parser core\n")]
    assert written.startswith(head)


def test_refresh_milestone_table_is_a_no_op_after_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = _plan_dir(tmp_path, (FIXTURES / "fixed.md").read_text(encoding="utf-8"), monkeypatch)
    (plan / "index.md").write_text(INDEX, encoding="utf-8")
    assert _booping(["plan", "split", "plans/demo/draft.md"]) == 0
    before = (plan / "index.md").read_text(encoding="utf-8")

    subprocess.run([str(REFRESH), str(plan)], check=True, capture_output=True)

    assert (plan / "index.md").read_text(encoding="utf-8") == before


def test_headingless_draft_exits_3_and_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _plan_dir(tmp_path, "# Plan\n\nNo milestones here.\n", monkeypatch)

    code = _booping(["plan", "split", "plans/demo/draft.md"])

    assert code == 3
    assert capsys.readouterr().err == "error: no milestone heading found in plans/demo/draft.md\n"
    assert _tree(plan) == ["draft.md"]


def test_missing_sp_exits_4_with_null_sp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _plan_dir(tmp_path, NO_SP_DRAFT, monkeypatch)

    code = _booping(["plan", "split", "plans/demo/draft.md"])

    out = capsys.readouterr()
    assert code == 4
    assert out.err == "flag: M01: sp not stated anywhere; left null\n"
    assert out.out == (
        "M01-only-step sp=null sections=tasks:1,dod:0,references:0,verify:0\ngroup G1: M01 (0 SP)\n"
    )
    written = (plan / "milestones" / "M01-only-step" / "M01-only-step.md").read_text()
    assert "\nsp: null\n" in written
    assert "| 01 | [Only step](milestones/M01-only-step/M01-only-step.md) |  | pending |" in (
        (plan / "index.md").read_text()
    )


def test_existing_milestones_refused_without_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _plan_dir(tmp_path, (FIXTURES / "fixed.md").read_text(encoding="utf-8"), monkeypatch)
    old = plan / "milestones" / "M01-old" / "M01-old.md"
    old.parent.mkdir(parents=True)
    old.write_text('---\nid: "01"\n---\n')

    code = _booping(["plan", "split", "plans/demo/draft.md"])

    assert code == 2
    assert capsys.readouterr().err.startswith("error: 1 milestone file(s) already exist")
    assert _tree(plan) == [
        "draft.md",
        "milestones",
        "milestones/M01-old",
        "milestones/M01-old/M01-old.md",
    ]


def test_replace_removes_old_milestone_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = _plan_dir(tmp_path, (FIXTURES / "fixed.md").read_text(encoding="utf-8"), monkeypatch)
    old = plan / "milestones" / "M01-old" / "M01-old.md"
    old.parent.mkdir(parents=True)
    old.write_text('---\nid: "01"\n---\n')
    stray = plan / "milestones" / "notes"
    stray.mkdir()

    code = _booping(["plan", "split", "plans/demo/draft.md", "--replace"])

    assert code == 0
    assert not old.parent.exists()
    assert stray.is_dir()
    assert (plan / "milestones" / "M01-parser-core" / "M01-parser-core.md").is_file()
