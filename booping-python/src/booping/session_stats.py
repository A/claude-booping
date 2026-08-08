"""Mine active working time, token usage and model ids from Claude Code transcripts.

A turn starts at a real user prompt and ends at the last conversational event
before the next one; idle time between turns never enters the sum.  Inside a
turn, every stretch the session spent blocked on a human — an `AskUserQuestion`
call until its `tool_result`, or a tool call the user rejected — is subtracted,
because it is wall clock the machine spent waiting rather than working.

The jsonl schema is internal to Claude Code and shifts between versions, so
every line is parsed defensively: unknown types are skipped, broken lines are
counted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import cast

# Only conversational lines carry turn boundaries.  Bookkeeping types
# (`mode`, `queue-operation`, `last-prompt`, …) are emitted while the user is
# idle, so counting them would fill the very gaps the algorithm drops.
_CONVERSATIONAL_TYPES = frozenset({"user", "assistant"})

# Waiting on this tool is waiting on a human, by definition of the tool.
_BLOCKING_TOOLS = frozenset({"AskUserQuestion"})

# The other denial kinds (`permission-rule`, `automode-blocked`,
# `automode-unavailable`) are system decisions taken without a human present.
_BLOCKING_DENIAL_KINDS = frozenset({"user-rejected"})


@dataclass(frozen=True)
class Tokens:
    input: int = 0
    output: int = 0
    cache_creation: int = 0
    cache_read: int = 0

    def __add__(self, other: Tokens) -> Tokens:
        return Tokens(
            input=self.input + other.input,
            output=self.output + other.output,
            cache_creation=self.cache_creation + other.cache_creation,
            cache_read=self.cache_read + other.cache_read,
        )


@dataclass(frozen=True)
class ToolUse:
    tool_use_id: str
    name: str


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    kind: str
    is_prompt: bool = False
    is_sidechain: bool = False
    is_meta: bool = False
    model: str | None = None
    denial_kind: str | None = None
    tool_uses: tuple[ToolUse, ...] = ()
    tool_result_ids: tuple[str, ...] = ()
    tokens: Tokens = field(default_factory=Tokens)


@dataclass(frozen=True)
class SessionStats:
    session_id: str
    seconds: float
    models: list[str]
    tokens: Tokens

    @property
    def minutes(self) -> int:
        return round(self.seconds / 60)


@dataclass(frozen=True)
class Report:
    sessions: list[SessionStats]
    warnings: list[str]

    @property
    def total_minutes(self) -> int:
        return round(sum(s.seconds for s in self.sessions) / 60)

    @property
    def models(self) -> list[str]:
        return sorted({m for s in self.sessions for m in s.models})

    @property
    def tokens(self) -> Tokens:
        total = Tokens()
        for session in self.sessions:
            total = total + session.tokens
        return total


def default_projects_root() -> Path:
    return Path.home() / ".claude" / "projects"


def locate_transcript(session_id: str, projects_root: Path) -> Path | None:
    """Find `{projects_root}/{any-project-slug}/{session_id}.jsonl`."""
    matches = sorted(projects_root.glob(f"*/{session_id}.jsonl"))
    return matches[0] if matches else None


def _parse_timestamp(raw: object) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _mapping(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict):
        return {}
    items = cast(dict[object, object], raw)
    return {str(key): value for key, value in items.items()}


def _int_at(mapping: dict[str, object], key: str) -> int:
    value = mapping.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _str_at(mapping: dict[str, object], key: str) -> str | None:
    value = mapping.get(key)
    return value if isinstance(value, str) and value else None


def _blocks(message: dict[str, object]) -> list[dict[str, object]]:
    content = message.get("content")
    if not isinstance(content, list):
        return []
    return [_mapping(block) for block in cast(list[object], content)]


def _model_of(message: dict[str, object]) -> str | None:
    return _str_at(message, "model")


def _tokens_of(message: dict[str, object]) -> Tokens:
    """Top-level `usage` only — `iterations` mirrors it and would double-count."""
    usage = _mapping(message.get("usage"))
    return Tokens(
        input=_int_at(usage, "input_tokens"),
        output=_int_at(usage, "output_tokens"),
        cache_creation=_int_at(usage, "cache_creation_input_tokens"),
        cache_read=_int_at(usage, "cache_read_input_tokens"),
    )


def _is_real_prompt(record: dict[str, object], message: dict[str, object]) -> bool:
    """A user line typed by the human.

    `origin.kind` is authoritative where present; older transcripts lack it and
    fall back to the shape heuristic — tool results and injected context arrive
    as `user` lines too, but their content is a list of blocks.
    """
    if record.get("isMeta") or record.get("isSidechain"):
        return False
    kind = _str_at(_mapping(record.get("origin")), "kind")
    if kind is not None:
        return kind == "human"
    return isinstance(message.get("content"), str)


def _event_of(record: dict[str, object]) -> Event | None:
    kind = record.get("type")
    if kind not in _CONVERSATIONAL_TYPES or not isinstance(kind, str):
        return None
    timestamp = _parse_timestamp(record.get("timestamp"))
    if timestamp is None:
        return None
    message = _mapping(record.get("message"))
    tool_uses: list[ToolUse] = []
    tool_result_ids: list[str] = []
    for block in _blocks(message):
        block_type = block.get("type")
        if block_type == "tool_use":
            tool_use_id, name = _str_at(block, "id"), _str_at(block, "name")
            if tool_use_id and name:
                tool_uses.append(ToolUse(tool_use_id=tool_use_id, name=name))
        elif block_type == "tool_result":
            tool_use_id = _str_at(block, "tool_use_id")
            if tool_use_id:
                tool_result_ids.append(tool_use_id)
    return Event(
        timestamp=timestamp,
        kind=kind,
        is_prompt=kind == "user" and _is_real_prompt(record, message),
        is_sidechain=bool(record.get("isSidechain")),
        is_meta=bool(record.get("isMeta")),
        model=_model_of(message) if kind == "assistant" else None,
        denial_kind=_str_at(record, "toolDenialKind"),
        tool_uses=tuple(tool_uses),
        tool_result_ids=tuple(tool_result_ids),
        tokens=_tokens_of(message) if kind == "assistant" else Tokens(),
    )


def parse_transcript(path: Path) -> tuple[list[Event], int]:
    """Stream a transcript into conversational events plus a malformed-line count."""
    events: list[Event] = []
    malformed = 0
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                record: object = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            typed = _mapping(record)
            if not isinstance(record, dict):
                malformed += 1
                continue
            if typed.get("type") not in _CONVERSATIONAL_TYPES:
                continue
            event = _event_of(typed)
            if event is None:
                malformed += 1
                continue
            events.append(event)
    return events, malformed


def _turn_spans(events: list[Event]) -> list[tuple[datetime, datetime]]:
    spans: list[tuple[datetime, datetime]] = []
    start: datetime | None = None
    last: datetime | None = None

    for event in events:
        if event.is_prompt:
            if start is not None and last is not None:
                spans.append((start, last))
            start = event.timestamp
            last = event.timestamp
        elif start is not None and last is not None:
            last = max(last, event.timestamp)

    if start is not None and last is not None:
        spans.append((start, last))
    return [span for span in spans if span[1] > span[0]]


def _blocking_spans(events: list[Event]) -> list[tuple[datetime, datetime]]:
    """Intervals from a user-blocking tool call to the line that answers it."""
    pending: dict[str, tuple[datetime, str]] = {}
    spans: list[tuple[datetime, datetime]] = []

    for event in events:
        for use in event.tool_uses:
            pending[use.tool_use_id] = (event.timestamp, use.name)
        for tool_use_id in event.tool_result_ids:
            opened = pending.pop(tool_use_id, None)
            if opened is None:
                continue
            started, name = opened
            blocking = name in _BLOCKING_TOOLS or event.denial_kind in _BLOCKING_DENIAL_KINDS
            if blocking and event.timestamp > started:
                spans.append((started, event.timestamp))
    return spans


def _merge(spans: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    merged: list[tuple[datetime, datetime]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _overlap_seconds(
    spans: list[tuple[datetime, datetime]], blocking: list[tuple[datetime, datetime]]
) -> float:
    seconds = 0.0
    for span_start, span_end in spans:
        for block_start, block_end in blocking:
            start = max(span_start, block_start)
            end = min(span_end, block_end)
            if end > start:
                seconds += (end - start).total_seconds()
    return seconds


def active_seconds(events: list[Event]) -> float:
    live = [e for e in events if not e.is_sidechain]
    spans = _turn_spans(live)
    total = sum((end - start).total_seconds() for start, end in spans)
    return max(0.0, total - _overlap_seconds(spans, _merge(_blocking_spans(live))))


def summarize(session_id: str, events: list[Event]) -> SessionStats:
    models: set[str] = set()
    tokens = Tokens()
    for event in events:
        if event.is_sidechain or event.kind != "assistant":
            continue
        if event.model:
            models.add(event.model)
        tokens = tokens + event.tokens

    return SessionStats(
        session_id=session_id,
        seconds=active_seconds(events),
        models=sorted(models),
        tokens=tokens,
    )


def build_report(session_ids: list[str], projects_root: Path) -> Report:
    sessions: list[SessionStats] = []
    warnings: list[str] = []

    for session_id in session_ids:
        path = locate_transcript(session_id, projects_root)
        if path is None:
            warnings.append(f"warning: no transcript found for session {session_id}")
            continue
        events, malformed = parse_transcript(path)
        if malformed:
            warnings.append(f"warning: skipped {malformed} malformed line(s) in {path}")
        sessions.append(summarize(session_id, events))

    return Report(sessions=sessions, warnings=warnings)
