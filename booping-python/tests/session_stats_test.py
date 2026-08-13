from __future__ import annotations

from pathlib import Path

import pytest

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


def _summary(path: Path) -> SessionStats:
    events, _ = parse_transcript(path)
    return summarize(path.stem, events)


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
