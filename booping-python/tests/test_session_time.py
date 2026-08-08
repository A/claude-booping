from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from booping.commands import session_time as cmd
from booping.context._yaml import parse_frontmatter_only
from booping.session_time import (
    build_report,
    locate_transcript,
    parse_transcript,
    summarize,
)

FIXTURES = Path(__file__).parent / "fixtures" / "session_time"
PROJECTS = FIXTURES / "projects"
PLAN = FIXTURES / "plan" / "index.md"


def _ns(**kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)  # type: ignore[arg-type]


run = cmd._run  # type: ignore[reportPrivateUsage]


# --- locator -----------------------------------------------------------------


def test_locate_transcript_finds_file_under_project_slug() -> None:
    found = locate_transcript("sess-alpha", PROJECTS)
    assert found == PROJECTS / "-home-anton-proj-a" / "sess-alpha.jsonl"


def test_locate_transcript_returns_none_when_absent() -> None:
    assert locate_transcript("sess-nope", PROJECTS) is None


def test_locate_transcript_tolerates_missing_root(tmp_path: Path) -> None:
    assert locate_transcript("sess-alpha", tmp_path / "absent") is None


# --- parser ------------------------------------------------------------------


def test_parser_counts_malformed_lines_and_skips_them() -> None:
    events, malformed = parse_transcript(PROJECTS / "-home-anton-proj-a" / "sess-alpha.jsonl")
    assert malformed == 1
    assert events


def test_parser_classifies_only_real_prompts_as_turn_starts() -> None:
    events, _ = parse_transcript(PROJECTS / "-home-anton-proj-a" / "sess-alpha.jsonl")
    assert [e.is_prompt for e in events] == [False, True, False, False, False, True, False]


def test_parser_drops_sidechain_lines() -> None:
    events, _ = parse_transcript(PROJECTS / "-home-anton-proj-a" / "sess-alpha.jsonl")
    assert all(e.model != "claude-sidechain-9" for e in events)


def test_parser_skips_unknown_types_without_raising(tmp_path: Path) -> None:
    path = tmp_path / "s.jsonl"
    path.write_text(
        '{"type":"future-thing","timestamp":"2026-08-08T10:00:00.000Z"}\n'
        '{"type":"user","timestamp":"2026-08-08T10:00:00.000Z",'
        '"message":{"content":"hi"}}\n'
    )
    events, malformed = parse_transcript(path)
    assert malformed == 0
    assert len(events) == 1


def test_parser_counts_bad_timestamps_as_malformed(tmp_path: Path) -> None:
    path = tmp_path / "s.jsonl"
    path.write_text('{"type":"user","timestamp":"not-a-date","message":{"content":"hi"}}\n')
    events, malformed = parse_transcript(path)
    assert (events, malformed) == ([], 1)


def test_parser_sets_model_only_on_assistant_events() -> None:
    events, _ = parse_transcript(PROJECTS / "-home-anton-proj-b" / "sess-beta.jsonl")
    assert [e.model for e in events] == [
        None,
        "claude-opus-4-8",
        None,
        "claude-opus-4-8",
    ]


# --- summation ---------------------------------------------------------------


def test_idle_gap_between_turns_is_not_counted() -> None:
    events, _ = parse_transcript(PROJECTS / "-home-anton-proj-a" / "sess-alpha.jsonl")
    summary = summarize("sess-alpha", events)
    assert summary.seconds == 120 + 240
    assert summary.minutes == 6


def test_session_ending_on_assistant_event_counts_final_turn() -> None:
    events, _ = parse_transcript(PROJECTS / "-home-anton-proj-b" / "sess-beta.jsonl")
    summary = summarize("sess-beta", events)
    assert summary.seconds == 90 + 150
    assert summary.minutes == 4


@pytest.mark.parametrize("name", ["sess-empty", "sess-header-only"])
def test_empty_and_header_only_transcripts_yield_zero(name: str) -> None:
    events, malformed = parse_transcript(PROJECTS / "-home-anton-proj-b" / f"{name}.jsonl")
    summary = summarize(name, events)
    assert (summary.seconds, summary.models, malformed) == (0.0, [], 0)


def test_models_are_sorted_deduped_and_exclude_sidechain() -> None:
    report = build_report(["sess-alpha", "sess-beta"], PROJECTS)
    assert report.models == ["claude-fable-5", "claude-opus-4-8"]


def test_total_is_rounded_integer_minutes() -> None:
    report = build_report(["sess-alpha", "sess-beta"], PROJECTS)
    assert report.total_minutes == 10


def test_missing_transcript_warns_and_skips_session() -> None:
    report = build_report(["sess-alpha", "sess-gone"], PROJECTS)
    assert [s.session_id for s in report.sessions] == ["sess-alpha"]
    assert any("sess-gone" in w for w in report.warnings)


# --- subcommand --------------------------------------------------------------


def test_run_prints_rows_total_and_models(capsys: pytest.CaptureFixture[str]) -> None:
    run(_ns(plan=PLAN, write=False, projects_root=PROJECTS))
    out = capsys.readouterr().out
    assert out == (
        "sess-alpha  6m  claude-fable-5\n"
        "sess-beta  4m  claude-opus-4-8\n"
        "total  10m\n"
        "models  claude-fable-5,claude-opus-4-8\n"
    )


def test_run_without_write_leaves_plan_untouched(capsys: pytest.CaptureFixture[str]) -> None:
    before = PLAN.read_text()
    run(_ns(plan=PLAN, write=False, projects_root=PROJECTS))
    capsys.readouterr()
    assert PLAN.read_text() == before


def test_write_stamps_active_minutes_and_models(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = tmp_path / "index.md"
    plan.write_text(PLAN.read_text())
    run(_ns(plan=plan, write=True, projects_root=PROJECTS))
    capsys.readouterr()
    frontmatter = parse_frontmatter_only(plan)
    assert frontmatter["active_minutes"] == 10
    assert list(frontmatter["models"]) == ["claude-fable-5", "claude-opus-4-8"]


def test_missing_plan_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        run(_ns(plan=tmp_path / "nope.md", write=False, projects_root=PROJECTS))
    assert exc.value.code == 1
    assert "plan not found" in capsys.readouterr().err


def test_plan_without_sessions_key_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = tmp_path / "index.md"
    plan.write_text("---\ntitle: No sessions\n---\n\n# Body\n")
    with pytest.raises(SystemExit) as exc:
        run(_ns(plan=plan, write=False, projects_root=PROJECTS))
    assert exc.value.code == 1
    assert "no sessions:" in capsys.readouterr().err


def test_null_sessions_reports_zero_at_exit_0(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = tmp_path / "index.md"
    plan.write_text("---\ntitle: Empty\nsessions: null\n---\n\n# Body\n")
    run(_ns(plan=plan, write=False, projects_root=PROJECTS))
    assert capsys.readouterr().out == "total  0m\nmodels  \n"


def test_parser_registers_session_time_subcommand() -> None:
    from booping.cli import build_parser

    args = build_parser().parse_args(["session-time", str(PLAN)])
    assert args.plan == PLAN
    assert args.write is False
    assert args.projects_root is None
