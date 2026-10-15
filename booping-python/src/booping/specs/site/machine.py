from __future__ import annotations

import datetime
import json
from collections.abc import Mapping
from typing import Any

from booping.specs.site.labels import Labels
from booping.specs.site.model import Site, SiteRecord
from booping.specs.site.state import RecordState


def _id(record: SiteRecord) -> str:
    return f"{record.root}:{record.ref}"


def _md(record: SiteRecord) -> str:
    return f"{record.root}/{record.type}/{record.stem}.md"


def _title(record: SiteRecord) -> str:
    title = record.frontmatter.get("title")
    return str(title) if title else record.stem


def _text(value: Any) -> str | None:
    return None if value is None else str(value)


def _tags(record: SiteRecord) -> list[str]:
    tags: Any = record.frontmatter.get("tags")
    if tags is None:
        return []
    items: list[Any] = tags if isinstance(tags, list) else [tags]  # pyright: ignore[reportUnknownVariableType]
    return [str(t) for t in items]


def _value(value: Any) -> Any:
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def llms_txt(
    site: Site, states: Mapping[SiteRecord, RecordState], labels: Labels, title: str
) -> str:
    """llmstxt.org shape: H1, the first value summary as a blockquote, then one section
    per root and type, a line per record linking its `.md` copy."""
    lines = [f"# {title}"]
    lead = next(
        (
            str(r.frontmatter["summary"])
            for r in site.records
            if r.type == "value" and r.frontmatter.get("summary")
        ),
        None,
    )
    if lead is not None:
        lines += ["", f"> {lead}"]
    for root in site.roots:
        records = [r for r in site.records if r.root == root.name]
        for type_ in dict.fromkeys(r.type for r in records):
            lines += ["", f"## {labels.type_plural(type_)} — {root.name}", ""]
            for record in (r for r in records if r.type == type_):
                name = _title(record).replace("[", "\\[").replace("]", "\\]")
                line = f"- [{record.ref} {name}]({_md(record)})"
                summary = record.frontmatter.get("summary")
                if summary:
                    status = states[record].status
                    parts = [labels.status(status)] if status else []
                    tags = ", ".join(_tags(record))
                    if tags:
                        parts.append(tags)
                    line += f": {summary}"
                    if parts:
                        line += f" ({'; '.join(parts)})"
                lines.append(line)
    return "\n".join(lines) + "\n"


def index_json(
    site: Site,
    states: Mapping[SiteRecord, RecordState],
    labels: Labels,
    title: str,
    lang: str,
) -> str:
    """Every record's metadata and resolved relations as ids `{root}:{ref}`, in page order."""
    # No label reaches the JSON; the parameter keeps one call shape for both machine files.
    del labels
    records: list[dict[str, Any]] = []
    for record in site.records:
        fm = record.frontmatter
        state = states[record]
        records.append(
            {
                "id": _id(record),
                "root": record.root,
                "ref": record.ref,
                "type": record.type,
                "title": _text(fm.get("title")),
                "summary": _text(fm.get("summary")),
                "status": state.status,
                "kind": state.kind,
                "tags": _tags(record),
                "created_by": _value(fm.get("created_by")),
                "created_at": _value(fm.get("created_at")),
                "updated_at": _value(fm.get("updated_at")),
                "reviewed": _value(fm.get("reviewed")),
                "url": record.page,
                "md": _md(record),
                "marks": {"clarify": state.clarify, "unknown": state.unknown},
                "relations": {
                    key: [_id(t) for t in targets]
                    for key, targets in site.relations(record).items()
                },
                "superseded_by": [_id(r) for r in site.superseded_by(record)],
                "backlinks": [_id(r) for r in site.backlinks(record)],
            }
        )
    document = {"title": title, "lang": lang, "records": records}
    return json.dumps(document, ensure_ascii=False, indent=1) + "\n"
