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


def record_state(record: SiteRecord, marks: list[Mark]) -> RecordState:
    fm = record.frontmatter
    status = fm.get("status")
    kind = fm.get("kind")
    return RecordState(
        status=None if status is None else str(status),
        kind=None if kind is None else str(kind),
        clarify=sum(1 for m in marks if m.kind == "clarify"),
        unknown=sum(1 for m in marks if m.kind == "unknown"),
        unreviewed=unreviewed(record),
        first_mark=f"L{marks[0].line}" if marks else None,
    )
