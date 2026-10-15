from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple
from urllib.parse import urlsplit

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from booping.specs.site.fonts import font_files
from booping.specs.site.labels import Labels, load_labels
from booping.specs.site.machine import index_json, llms_txt
from booping.specs.site.markdown import LinkRenderer, Mark, Rendered, render_body
from booping.specs.site.model import RefMiss, Site, SiteRecord, ref_keys, ref_values
from booping.specs.site.state import RecordState, record_state

_HERE = Path(__file__).parent
_MARK_KINDS = ("clarify", "unknown")
_PAGE_HEAD_KEYS = ("type", "title", "summary", "status", "tags")
_FACT_KEYS = ("created_by", "created_at", "updated_at", "reviewed", "sources")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class SiteWarning(NamedTuple):
    path: Path
    line: int
    message: str


@dataclass(frozen=True)
class Crumb:
    label: str
    href: str | None


def environment(labels: Labels, lang: str, site_title: str) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_HERE / "templates")),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    shared: dict[str, Any] = {"labels": labels, "lang": lang, "site_title": site_title}
    env.globals.update(shared)
    return env


def _title(record: SiteRecord) -> str:
    title = record.frontmatter.get("title")
    return str(title) if title else record.stem


def _record_href(record: SiteRecord) -> str:
    # Every link source sits two directories below the out root ({root}/{type}/…).
    return f"../../{record.page}"


def _link_renderer(site: Site, record: SiteRecord) -> LinkRenderer:
    def link(dest: str) -> tuple[str | None, str | None]:
        target = site.resolve_link(dest, record)
        if target.kind == "external":
            return dest, None
        if target.kind == "anchor":
            return dest, None
        if target.kind == "record" and target.record is not None:
            anchor = f"#{target.anchor}" if target.anchor else ""
            return _record_href(target.record) + anchor, None
        return None, target.kind

    return link


def _summary(record: SiteRecord) -> str | None:
    summary = record.frontmatter.get("summary")
    return None if summary is None else str(summary)


def _ref_line(record: SiteRecord, ref: str) -> int:
    lines = record.path.read_text().splitlines()[: record.body_first_line - 1]
    return next((n for n, line in enumerate(lines, start=1) if ref in line), 1)


def _fact_items(
    site: Site, record: SiteRecord, value: Any, warnings: set[SiteWarning]
) -> list[dict[str, Any]]:
    values: list[Any] = value if isinstance(value, list) else [value]  # pyright: ignore[reportUnknownVariableType]
    items: list[dict[str, Any]] = []
    for item in values:
        text = "" if item is None else str(item)
        resolved = site.resolve_ref(text, record.root) if isinstance(item, str) else None
        if resolved is None:
            items.append({"text": text, "href": None, "code": False, "css": None})
        elif isinstance(resolved, RefMiss):
            if resolved.warn:
                warnings.add(
                    SiteWarning(record.path, _ref_line(record, text), f"unresolved ref {text}")
                )
            css = "unresolved" if resolved.warn else None
            items.append({"text": text, "href": None, "code": True, "css": css})
        else:
            items.append({"text": text, "href": _record_href(resolved), "code": True, "css": None})
    return items


def _status_state(record: SiteRecord) -> RecordState:
    status = record.frontmatter.get("status")
    return RecordState(
        status=None if status is None else str(status),
        kind=None,
        clarify=0,
        unknown=0,
        unreviewed=False,
        first_mark=None,
    )


def _rel_item(target: SiteRecord, from_root: str) -> dict[str, Any]:
    return {
        "href": _record_href(target),
        "title": _title(target),
        "ref": target.ref if target.root == from_root else f"{target.root}:{target.ref}",
        "state": _status_state(target),
        "text": None,
        "css": None,
    }


def _text_item(text: str, css: str | None = None) -> dict[str, Any]:
    return {"href": None, "title": None, "ref": None, "state": None, "text": text, "css": css}


def _date_item(labels: Labels, value: Any) -> dict[str, Any]:
    if isinstance(value, datetime.datetime):
        iso: str | None = value.date().isoformat()
    elif isinstance(value, datetime.date):
        iso = value.isoformat()
    elif _ISO_DATE.fullmatch(str(value)) and labels.date(value) != str(value):
        iso = str(value)
    else:
        iso = None
    return {"text": labels.date(value), "href": None, "datetime": iso}


def _facts(labels: Labels, fm: dict[str, Any]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for key in _FACT_KEYS:
        value = fm.get(key)
        if key == "reviewed" and not value:
            items = [{"text": labels.ui("not_reviewed"), "href": None, "datetime": None}]
        elif value is None or value == "" or value == []:
            continue
        elif key == "created_by":
            items = [{"text": labels.author(str(value)), "href": None, "datetime": None}]
        elif key == "sources":
            values: list[Any] = value if isinstance(value, list) else [value]  # pyright: ignore[reportUnknownVariableType]
            items = [
                {"text": str(v), "href": str(v) if "://" in str(v) else None, "datetime": None}
                for v in values
            ]
        else:
            items = [_date_item(labels, value)]
        facts.append({"label": labels.fact(key), "items": items})
    return facts


def _relations(
    site: Site, record: SiteRecord, labels: Labels, warnings: set[SiteWarning]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(ref_keys(record.frontmatter)):
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for text in ref_values(record.frontmatter[key]):
            if text in seen:
                continue
            seen.add(text)
            resolved = site.resolve_ref(text, record.root)
            if isinstance(resolved, SiteRecord):
                items.append(_rel_item(resolved, record.root))
            elif isinstance(resolved, RefMiss):
                if resolved.warn:
                    warnings.add(
                        SiteWarning(record.path, _ref_line(record, text), f"unresolved ref {text}")
                    )
                items.append(_text_item(text, "unresolved" if resolved.warn else None))
        rows.append({"label": labels.fact(key), "items": items})
    superseders = site.superseded_by(record)
    if superseders:
        rows.append(
            {
                "label": labels.ui("superseded_by"),
                "items": [_rel_item(r, record.root) for r in superseders],
            }
        )
    return rows


def _record_view(
    site: Site,
    record: SiteRecord,
    rendered: Rendered,
    state: RecordState,
    labels: Labels,
    warnings: set[SiteWarning],
) -> dict[str, Any]:
    fm = record.frontmatter
    raw_tags: Any = fm.get("tags") or []
    tags: list[Any] = raw_tags if isinstance(raw_tags, list) else [raw_tags]  # pyright: ignore[reportUnknownVariableType]
    refs = ref_keys(fm)
    skip = {*_PAGE_HEAD_KEYS, *_FACT_KEYS, *refs}
    return {
        "title": _title(record),
        "stem": record.stem,
        "state": state,
        "tags": [str(t) for t in tags],
        "summary": _summary(record),
        "facts": _facts(labels, fm),
        "relations": _relations(site, record, labels, warnings),
        "raw": [
            {"key": key, "items": _fact_items(site, record, value, warnings)}
            for key, value in fm.items()
            if key not in skip
        ],
        "body": Markup(rendered.html),
        "backlinks": [_rel_item(src, record.root) for src in site.backlinks(record)],
    }


def _render(site: Site, record: SiteRecord) -> Rendered:
    return render_body(
        record.body,
        first_line=record.body_first_line,
        link=_link_renderer(site, record),
        statuses=site.statuses,
    )


def build_site(
    site: Site,
    known_types: list[str],
    labels: Labels | None = None,
    lang: str = "en",
    site_title: str = "Specs",
    site_url: str | None = None,
) -> tuple[dict[str, str | bytes], list[SiteWarning]]:
    """Out-root-relative path → file content, plus the resolution warnings sorted by
    `(path, line)`, each once per record. Types order as `known_types`, then the types
    a root's `_schemas/` added, sorted. No `labels` → English. A `site_url` adds a
    `404.html` resolving its links against the URL's path."""
    if labels is None:
        labels, lang, _ = load_labels({})
    env = environment(labels, lang, site_title)
    files: dict[str, str | bytes] = {
        **font_files(),
        "style.css": (_HERE / "style.css").read_text(),
        "site.js": (_HERE / "site.js").read_text(),
    }
    warnings: set[SiteWarning] = set()

    added = sorted({r.type for r in site.records} - set(known_types))
    present = [t for t in [*known_types, *added] if any(r.type == t for r in site.records)]
    nav = [
        {
            "root": root.name,
            "types": [
                {
                    "type": type_,
                    "label": labels.type_plural(type_),
                    "count": count,
                    "href": f"{root.name}/{type_}/index.html",
                }
                for type_ in present
                if (
                    count := sum(1 for r in site.records if r.root == root.name and r.type == type_)
                )
            ],
        }
        for root in site.roots
    ]

    def page(template: str, path: str, title: str, crumbs: list[Crumb], **ctx: Any) -> None:
        prefix = "../" * path.count("/")
        files[path] = env.get_template(template).render(
            title=title, prefix=prefix, path=path, crumbs=crumbs, nav=nav, **ctx
        )

    marks: dict[int, list[Mark]] = {}
    states: dict[SiteRecord, RecordState] = {}
    for record in site.records:
        own = _render(site, record)
        marks[id(record)] = own.marks
        state = states[record] = record_state(record, own.marks)
        for line, dest in own.links:
            if site.resolve_link(dest, record).kind == "unresolved":
                warnings.add(SiteWarning(record.path, line, f"unresolved link {dest}"))
        page(
            "record.html.j2",
            record.page,
            _title(record),
            [
                Crumb(labels.ui("overview"), "../../index.html"),
                Crumb(record.root, "../index.html"),
                Crumb(labels.type_plural(record.type), "index.html"),
                Crumb(record.ref, None),
            ],
            record=_record_view(site, record, own, state, labels, warnings),
        )
        files[f"{record.root}/{record.type}/{record.stem}.md"] = record.path.read_bytes()

    root_types: list[dict[str, Any]] = []
    for root in site.roots:
        records = [r for r in site.records if r.root == root.name]
        types_: list[dict[str, Any]] = []
        for type_ in present:
            of_type = [r for r in records if r.type == type_]
            if not of_type:
                continue
            types_.append({"type": type_, "count": len(of_type)})
            page(
                "type.html.j2",
                f"{root.name}/{type_}/index.html",
                labels.type_plural(type_),
                [
                    Crumb(labels.ui("overview"), "../../index.html"),
                    Crumb(root.name, "../index.html"),
                    Crumb(labels.type_plural(type_), None),
                ],
                type=type_,
                rows=[
                    {
                        "ref": r.ref,
                        "href": f"{r.stem}.html",
                        "title": _title(r),
                        "summary": _summary(r),
                        "state": states[r],
                    }
                    for r in of_type
                ],
            )
        page(
            "root.html.j2",
            f"{root.name}/index.html",
            root.name,
            [Crumb(labels.ui("overview"), "../index.html"), Crumb(root.name, None)],
            root=root.name,
            types=types_,
            marks=[
                {
                    "kind": kind,
                    "href": f"{r.type}/{r.stem}.html#L{m.line}",
                    "ref": r.ref,
                    "title": _title(r),
                    "text": m.text,
                }
                for kind in _MARK_KINDS
                for r in records
                for m in marks[id(r)]
                if m.kind == kind
            ],
        )
        root_types.append({"root": root.name, "types": types_})

    page(
        "index.html.j2",
        "index.html",
        site_title,
        [Crumb(labels.ui("overview"), None)],
        roots=root_types,
    )
    if site_url is not None:
        base = urlsplit(site_url).path
        page(
            "not_found.html.j2",
            "404.html",
            labels.ui("not_found"),
            [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("not_found"), None)],
            base_href=base if base.endswith("/") else f"{base}/",
        )
    files["llms.txt"] = llms_txt(site, states, labels, site_title)
    files["index.json"] = index_json(site, states, labels, site_title, lang)
    return files, sorted(warnings)
