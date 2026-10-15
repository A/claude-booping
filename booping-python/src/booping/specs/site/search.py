from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from booping.specs.site.labels import Labels
from booping.specs.site.markdown import Rendered
from booping.specs.site.model import Site, SiteRecord
from booping.specs.site.state import RecordState

_FLAGS = ("unreviewed", "clarify", "unknown")


def _id(record: SiteRecord) -> str:
    return f"{record.root}:{record.ref}"


def _text(value: Any) -> str | None:
    return None if value is None else str(value)


def _tags(record: SiteRecord) -> list[str]:
    tags: Any = record.frontmatter.get("tags")
    if tags is None:
        return []
    items: list[Any] = tags if isinstance(tags, list) else [tags]  # pyright: ignore[reportUnknownVariableType]
    return [str(t) for t in items]


def _js(name: str, value: Any) -> str:
    return f"window.{name} = {json.dumps(value, ensure_ascii=False, separators=(',', ':'))};\n"


def search_index_js(site: Site, labels: Labels, states: Mapping[SiteRecord, RecordState]) -> str:
    """`window.SPECS_INDEX`: every record's searchable metadata, in page order."""
    entries: list[dict[str, Any]] = []
    for record in site.records:
        fm = record.frontmatter
        state = states[record]
        entries.append(
            {
                "id": _id(record),
                "ref": record.ref,
                "root": record.root,
                "type": record.type,
                "type_label": labels.type_name(record.type),
                "title": _text(fm.get("title")),
                "summary": _text(fm.get("summary")),
                "status": state.status,
                "status_label": None if state.status is None else labels.status(state.status),
                "tags": _tags(record),
                "url": record.page,
                "flags": [flag for flag in _FLAGS if flag in state.reasons],
            }
        )
    return _js("SPECS_INDEX", entries)


def search_body_js(site: Site, rendered: Mapping[int, Rendered]) -> str:
    """`window.SPECS_BODY`: record id → plain body text, keyed by `id(record)` in `rendered`."""
    return _js("SPECS_BODY", {_id(r): rendered[id(r)].text for r in site.records})
