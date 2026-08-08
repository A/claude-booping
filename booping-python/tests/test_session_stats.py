from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from booping.commands import session_stats as cmd
from booping.context._yaml import parse_frontmatter_only
from booping.session_stats import (
    SessionStats,
    Tokens,
    build_report,
    locate_transcript,
    parse_transcript,
    summarize,
)

FIXTURES = Path(__file__).parent / "fixtures" / "session_stats"
PROJECTS = FIXTURES / "projects"
PROJ_A = PROJECTS / "-home-anton-proj-a"
PROJ_B = PROJECTS / "-home-anton-proj-b"
VAULT = FIXTURES / "vault"

run = cmd._run  # type: ignore[reportPrivateUsage]


def _summary(path: Path) -> SessionStats:
    events, _ = parse_transcript(path)
    return summarize(path.stem, events)


def _ns(path: Path, **overrides: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "path": path,
        "mask": "index.md",
        "force": False,
        "dry_run": False,
        "projects_root": PROJECTS,
    }
    return argparse.Namespace(**{**defaults, **overrides})  # type: ignore[arg-type]


def _document(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    return json.loads(capsys.readouterr().out)


def _vault_copy(tmp_path: Path) -> Path:
    dest = tmp_path / "vault"
    shutil.copytree(VAULT, dest)
    return dest


# --- locator -----------------------------------------------------------------


def test_locate_transcript_finds_file_under_project_slug() -> None:
    assert locate_transcript("sess-alpha", PROJECTS) == PROJ_A / "sess-alpha.jsonl"


def test_locate_transcript_returns_none_when_absent() -> None:
    assert locate_transcript("sess-nope", PROJECTS) is None


def test_locate_transcript_tolerates_missing_root(tmp_path: Path) -> None:
    assert locate_transcript("sess-alpha", tmp_path / "absent") is None


def test_missing_transcript_warns_and_skips_session() -> None:
    report = build_report(["sess-alpha", "sess-gone"], PROJECTS)
    assert [s.session_id for s in report.sessions] == ["sess-alpha"]
    assert any("sess-gone" in w for w in report.warnings)


# --- classifier --------------------------------------------------------------


def test_parser_counts_malformed_lines_and_skips_them() -> None:
    events, malformed = parse_transcript(PROJ_A / "sess-alpha.jsonl")
    assert malformed == 1
    assert events


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


def test_human_origin_with_list_content_is_a_real_prompt() -> None:
    events, _ = parse_transcript(PROJ_A / "sess-alpha.jsonl")
    interruption = next(e for e in events if e.timestamp.minute == 30)
    assert interruption.is_prompt is True


def test_task_notification_origin_is_not_a_real_prompt() -> None:
    events, _ = parse_transcript(PROJ_A / "sess-alpha.jsonl")
    notification = next(e for e in events if e.timestamp.minute == 31)
    assert notification.is_prompt is False


def test_meta_and_sidechain_lines_are_not_real_prompts() -> None:
    events, _ = parse_transcript(PROJ_A / "sess-alpha.jsonl")
    assert [(e.is_meta, e.is_sidechain, e.is_prompt) for e in events if e.is_meta or e.is_sidechain]
    assert all(not e.is_prompt for e in events if e.is_meta or e.is_sidechain)


def test_parser_classifies_turn_starts() -> None:
    events, _ = parse_transcript(PROJ_A / "sess-alpha.jsonl")
    assert [e.is_prompt for e in events] == [
        False,
        True,
        False,
        False,
        False,
        False,
        True,
        False,
        False,
    ]


def test_parser_yields_tool_use_name_id_and_denial_kind() -> None:
    events, _ = parse_transcript(PROJ_A / "sess-rejected.jsonl")
    assert [(u.tool_use_id, u.name) for e in events for u in e.tool_uses] == [
        ("toolu_edit", "Edit")
    ]
    denials = [(e.tool_result_ids, e.denial_kind) for e in events if e.denial_kind]
    assert denials == [(("toolu_edit",), "user-rejected")]


def test_parser_sets_model_only_on_assistant_events() -> None:
    events, _ = parse_transcript(PROJ_B / "sess-beta.jsonl")
    assert [e.model for e in events] == [None, "claude-opus-4-8", None, "claude-opus-4-8"]


# --- active time -------------------------------------------------------------


def test_idle_gap_between_turns_is_not_counted() -> None:
    summary = _summary(PROJ_A / "sess-alpha.jsonl")
    assert summary.seconds == 120 + 240
    assert summary.minutes == 6


def test_session_ending_on_assistant_event_counts_final_turn() -> None:
    summary = _summary(PROJ_B / "sess-beta.jsonl")
    assert summary.seconds == 90 + 150
    assert summary.minutes == 4


@pytest.mark.parametrize("name", ["sess-empty", "sess-header-only"])
def test_empty_and_header_only_transcripts_yield_zero(name: str) -> None:
    events, malformed = parse_transcript(PROJ_B / f"{name}.jsonl")
    summary = summarize(name, events)
    assert (summary.seconds, summary.models, summary.tokens, malformed) == (
        0.0,
        [],
        Tokens(),
        0,
    )


def test_ask_user_question_span_is_excluded_from_active_time() -> None:
    summary = _summary(PROJ_A / "sess-ask.jsonl")
    assert summary.minutes == 6


def test_tool_result_is_matched_by_tool_use_id_not_position() -> None:
    summary = _summary(PROJ_A / "sess-concurrent.jsonl")
    assert summary.minutes == 4


def test_user_rejected_span_is_subtracted() -> None:
    assert _summary(PROJ_A / "sess-rejected.jsonl").minutes == 3


def test_automode_blocked_span_is_not_subtracted() -> None:
    assert _summary(PROJ_A / "sess-automode.jsonl").minutes == 23


def test_regression_session_reports_well_under_unadjusted_span() -> None:
    summary = _summary(PROJ_A / "sess-19353202.jsonl")
    assert summary.minutes == 34


def test_total_is_rounded_integer_minutes() -> None:
    report = build_report(["sess-alpha", "sess-beta"], PROJECTS)
    assert report.total_minutes == 10


# --- tokens and models -------------------------------------------------------


def test_tokens_sum_only_top_level_usage_fields() -> None:
    assert _summary(PROJ_B / "sess-tokens-plain.jsonl").tokens == Tokens(
        input=300, output=30, cache_creation=3000, cache_read=11000
    )


def test_iterations_array_is_never_summed() -> None:
    plain = _summary(PROJ_B / "sess-tokens-plain.jsonl")
    iterated = _summary(PROJ_B / "sess-tokens-iterations.jsonl")
    assert plain.tokens == iterated.tokens


def test_cache_creation_and_cache_read_stay_separate() -> None:
    tokens = _summary(PROJ_B / "sess-tokens-plain.jsonl").tokens
    assert (tokens.cache_creation, tokens.cache_read) == (3000, 11000)


def test_sidechain_lines_contribute_neither_tokens_nor_models() -> None:
    summary = _summary(PROJ_B / "sess-tokens-plain.jsonl")
    assert summary.models == ["claude-fable-5"]
    assert summary.tokens.input == 300


def test_models_are_sorted_deduped_across_sessions() -> None:
    report = build_report(["sess-beta", "sess-alpha"], PROJECTS)
    assert report.models == ["claude-fable-5", "claude-opus-4-8"]


def test_report_tokens_sum_across_sessions() -> None:
    report = build_report(["sess-alpha", "sess-beta"], PROJECTS)
    assert report.tokens == Tokens(input=44, output=21, cache_creation=82, cache_read=116)


# --- addressing --------------------------------------------------------------


def test_directory_walks_by_mask_in_sorted_path_order(capsys: pytest.CaptureFixture[str]) -> None:
    run(_ns(VAULT, dry_run=True))
    document = _document(capsys)
    assert [a["path"] for a in document["artifacts"]] == ["plan-a/index.md", "plan-b/index.md"]


def test_file_path_yields_one_entry_and_ignores_mask(capsys: pytest.CaptureFixture[str]) -> None:
    plan = VAULT / "plan-a" / "index.md"
    run(_ns(plan, mask="nothing-matches.md", dry_run=True))
    document = _document(capsys)
    assert [a["path"] for a in document["artifacts"]] == [str(plan)]


def test_artifact_without_sessions_key_is_skipped_with_a_stderr_note(
    capsys: pytest.CaptureFixture[str],
) -> None:
    run(_ns(VAULT / "plan-no-sessions" / "index.md", dry_run=True))
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"artifacts": []}
    assert "no sessions:" in captured.err


def test_stdout_is_json_only_while_warnings_go_to_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    run(_ns(VAULT, dry_run=True))
    captured = capsys.readouterr()
    assert json.loads(captured.out)["artifacts"]
    assert "warning:" in captured.err
    assert "warning:" not in captured.out


def test_missing_path_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        run(_ns(tmp_path / "absent"))
    assert exc.value.code == 1
    assert "path not found" in capsys.readouterr().err


def test_mask_matching_nothing_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        run(_ns(VAULT, mask="nothing-matches.md"))
    assert exc.value.code == 1
    assert "no artifact matching" in capsys.readouterr().err


def test_cli_registers_session_stats_with_contract_defaults() -> None:
    from booping.cli import build_parser

    args = build_parser().parse_args(["session-stats", str(VAULT)])
    assert (args.path, args.mask) == (VAULT, "index.md")
    assert (args.force, args.dry_run, args.projects_root) == (False, False, None)


# --- write path --------------------------------------------------------------


def test_fresh_artifact_gets_all_six_keys_and_reports_written(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _vault_copy(tmp_path)
    run(_ns(vault))
    entry = _document(capsys)["artifacts"][0]
    assert entry["written"] is True
    frontmatter = parse_frontmatter_only(vault / "plan-a" / "index.md")
    assert {key: frontmatter.get(key) for key in cmd.METRIC_KEYS} == {
        "metrics_active_minutes": 10,
        "metrics_models": ["claude-fable-5", "claude-opus-4-8"],
        "metrics_tokens_input": 44,
        "metrics_tokens_output": 21,
        "metrics_tokens_cache_creation": 82,
        "metrics_tokens_cache_read": 116,
    }


def test_rerun_without_force_is_a_byte_identical_skip(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _vault_copy(tmp_path)
    run(_ns(vault))
    capsys.readouterr()
    stamped = (vault / "plan-a" / "index.md").read_bytes()

    run(_ns(vault))
    entry = _document(capsys)["artifacts"][0]
    assert entry["written"] is False
    assert entry["skipped"] == cmd.ALREADY_STAMPED
    assert (entry["sessions"], entry["totals"]) == ([], {})
    assert (vault / "plan-a" / "index.md").read_bytes() == stamped


def test_force_overwrites_existing_values(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _vault_copy(tmp_path)
    plan = vault / "plan-a" / "index.md"
    plan.write_text(plan.read_text().replace("sp: 3", "sp: 3\nmetrics_active_minutes: 999"))

    run(_ns(vault, force=True))
    capsys.readouterr()
    assert parse_frontmatter_only(plan)["metrics_active_minutes"] == 10


def test_dry_run_matches_a_real_run_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _vault_copy(tmp_path)
    before = {p: p.read_bytes() for p in sorted(vault.rglob("*.md"))}

    run(_ns(vault, dry_run=True))
    dry = _document(capsys)["artifacts"]
    assert {p: p.read_bytes() for p in sorted(vault.rglob("*.md"))} == before

    run(_ns(vault))
    wet = _document(capsys)["artifacts"]
    assert [a["totals"] for a in dry] == [a["totals"] for a in wet]
    assert [a["written"] for a in dry] == [False, False]


def test_session_objects_use_the_frontmatter_key_names_verbatim(
    capsys: pytest.CaptureFixture[str],
) -> None:
    run(_ns(VAULT, dry_run=True))
    entry = _document(capsys)["artifacts"][0]
    assert set(entry["totals"]) == set(cmd.METRIC_KEYS)
    assert set(entry["sessions"][0]) == {"session", *cmd.METRIC_KEYS}
