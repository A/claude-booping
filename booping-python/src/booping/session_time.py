"""Mine active working time and model ids from Claude Code session transcripts.

A turn starts at a real user prompt and ends at the last conversational event
before the next one; idle time between turns never enters the sum.  The jsonl
schema is internal to Claude Code and shifts between versions, so every line is
parsed defensively: unknown types are skipped, broken lines are counted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Only conversational lines carry turn boundaries.  Bookkeeping types
# (`mode`, `queue-operation`, `last-prompt`, …) are emitted while the user is
# idle, so counting them would fill the very gaps the algorithm drops.
_CONVERSATIONAL_TYPES = frozenset({"user", "assistant"})


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    is_prompt: bool
    model: str | None


@dataclass(frozen=True)
class SessionSummary:
    session_id: str
    seconds: float
    models: list[str]

    @property
    def minutes(self) -> int:
        return round(self.seconds / 60)


@dataclass(frozen=True)
class Report:
    sessions: list[SessionSummary]
    warnings: list[str]

    @property
    def total_minutes(self) -> int:
        return round(sum(s.seconds for s in self.sessions) / 60)

    @property
    def models(self) -> list[str]:
        return sorted({m for s in self.sessions for m in s.models})


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


def _model_of(record: dict[str, object]) -> str | None:
    message = record.get("message")
    if not isinstance(message, dict):
        return None
    model = message.get("model")  # type: ignore[reportUnknownMemberType]
    return model if isinstance(model, str) and model else None


def _is_real_prompt(record: dict[str, object]) -> bool:
    """A user line typed by the human: not meta, and plain-string content.

    Tool results and injected context arrive as `user` lines too, but their
    content is a list of blocks, or they carry `isMeta`.
    """
    if record.get("isMeta"):
        return False
    message = record.get("message")
    if not isinstance(message, dict):
        return False
    return isinstance(message.get("content"), str)  # type: ignore[reportUnknownMemberType]


def parse_transcript(path: Path) -> tuple[list[Event], int]:
    """Stream a transcript into conversational events plus a malformed-line count."""
    events: list[Event] = []
    malformed = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record: object = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if not isinstance(record, dict):
                malformed += 1
                continue
            typed: dict[str, object] = {str(k): v for k, v in record.items()}  # type: ignore[reportUnknownVariableType]
            kind = typed.get("type")
            if kind not in _CONVERSATIONAL_TYPES:
                continue
            if typed.get("isSidechain"):
                continue
            timestamp = _parse_timestamp(typed.get("timestamp"))
            if timestamp is None:
                malformed += 1
                continue
            is_assistant = kind == "assistant"
            events.append(
                Event(
                    timestamp=timestamp,
                    is_prompt=not is_assistant and _is_real_prompt(typed),
                    model=_model_of(typed) if is_assistant else None,
                )
            )
    return events, malformed


def summarize(session_id: str, events: list[Event]) -> SessionSummary:
    seconds = 0.0
    models: set[str] = set()
    start: datetime | None = None
    last: datetime | None = None

    for event in events:
        if event.model:
            models.add(event.model)
        if event.is_prompt:
            if start is not None and last is not None:
                seconds += max(0.0, (last - start).total_seconds())
            start = event.timestamp
            last = event.timestamp
        elif start is not None and last is not None:
            last = max(last, event.timestamp)

    if start is not None and last is not None:
        seconds += max(0.0, (last - start).total_seconds())

    return SessionSummary(session_id=session_id, seconds=seconds, models=sorted(models))


def build_report(session_ids: list[str], projects_root: Path) -> Report:
    sessions: list[SessionSummary] = []
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
