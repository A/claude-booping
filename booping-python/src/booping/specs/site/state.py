from __future__ import annotations

from dataclasses import dataclass

from booping.specs.records import unreviewed
from booping.specs.site.markdown import Mark
from booping.specs.site.model import SiteRecord


@dataclass(frozen=True)
class RecordState:
    status: str | None
    kind: str | None
    clarify: int
    unknown: int
    unreviewed: bool
    # Anchor id of the record's first mark, the target of the clarify badge.
    first_mark: str | None
    first_clarify: str | None = None
    first_unknown: str | None = None
    # Why the record needs the owner, in the fixed flag order of the review filter.
    reasons: tuple[str, ...] = ()


def _first(marks: list[Mark], kind: str) -> str | None:
    return next((f"L{m.line}" for m in marks if m.kind == kind), None)


def record_state(record: SiteRecord, marks: list[Mark]) -> RecordState:
    fm = record.frontmatter
    status = fm.get("status")
    kind = fm.get("kind")
    status_text = None if status is None else str(status)
    clarify = sum(1 for m in marks if m.kind == "clarify")
    unknown = sum(1 for m in marks if m.kind == "unknown")
    is_unreviewed = unreviewed(record)
    flags = {
        "unreviewed": is_unreviewed,
        "clarify": clarify > 0,
        "unknown": unknown > 0,
        "conflict": record.type == "conflict" and status_text == "open",
        "proposed": record.type == "adr" and status_text == "proposed",
        "open": record.type == "idea" and status_text == "open",
    }
    return RecordState(
        status=status_text,
        kind=None if kind is None else str(kind),
        clarify=clarify,
        unknown=unknown,
        unreviewed=is_unreviewed,
        first_mark=f"L{marks[0].line}" if marks else None,
        first_clarify=_first(marks, "clarify"),
        first_unknown=_first(marks, "unknown"),
        reasons=tuple(flag for flag, on in flags.items() if on),
    )
