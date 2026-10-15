from __future__ import annotations

import datetime
import posixpath
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from booping.specs.site.fonts import font_files
from booping.specs.site.items import OpenItem
from booping.specs.site.labels import Labels, load_labels
from booping.specs.site.machine import index_json, lead_summary, llms_txt
from booping.specs.site.markdown import LinkRenderer, Mark, Rendered, render_body
from booping.specs.site.model import (
    RefMiss,
    Site,
    SiteRecord,
    SiteWarning,
    ref_keys,
    ref_values,
)
from booping.specs.site.state import RecordState, record_state
from booping.specs.site.tags import TagNode, record_tags, tag_page_path, tag_tree, tagged

_HERE = Path(__file__).parent
_MARK_KINDS = ("clarify", "unknown")
_PAGE_HEAD_KEYS = ("type", "title", "summary", "status", "tags")
_FACT_KEYS = ("created_by", "created_at", "updated_at", "reviewed", "sources")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_RECENT = 10


@dataclass(frozen=True)
class Chip:
    value: str
    label: str
    count: int
    icon: str | None = None


@dataclass(frozen=True)
class Facet:
    key: str
    chips: list[Chip]


LIST_FACETS = ("type", "source", "status", "flag")
LIST_FLAGS = ("unreviewed", "clarify", "unknown")
LIST_SORTS = ("number", "updated", "title")
REVIEW_FACETS = ("type", "source", "flag")
REVIEW_FLAGS = ("unreviewed", "clarify", "unknown", "conflict", "proposed", "open")
REVIEW_SORTS = ("review", "number", "updated", "title")
_FLAG_ICONS = {
    "unreviewed": "i-unreviewed",
    "clarify": "i-clarify",
    "unknown": "i-unknown",
    "conflict": "i-unknown",
    "proposed": "i-planned",
    "open": "i-open",
}


def filter_facets(
    rows: list[dict[str, Any]], facets: Sequence[str], flags: Sequence[str], labels: Labels
) -> list[Facet]:
    """Chips per facet with the number of rows carrying each value, counted on the whole
    page; a value no row carries has no chip, and a facet of fewer than two chips is
    dropped — except `flag`, kept with one."""
    out: list[Facet] = []
    for key in facets:
        if key == "flag":
            carried = [set(row["data"]["flags"].split()) for row in rows]
            chips = [
                Chip(flag, labels.ui(f"flag_{flag}"), n, _FLAG_ICONS.get(flag))
                for flag in flags
                if (n := sum(1 for c in carried if flag in c))
            ]
            if chips:
                out.append(Facet(key, chips))
            continue
        values = [row["data"][key] for row in rows if row["data"][key]]
        order = list(dict.fromkeys(values))
        label = {
            "type": labels.type_plural,
            "source": str,
            "status": labels.status,
        }[key]
        chips = [Chip(v, label(v), values.count(v)) for v in order]
        if len(chips) >= 2:
            out.append(Facet(key, chips))
    return out


def _filters(
    rows: list[dict[str, Any]],
    labels: Labels,
    sort: str = "number",
    sorts: Sequence[str] = LIST_SORTS,
    facets: Sequence[str] = LIST_FACETS,
    flags: Sequence[str] = LIST_FLAGS,
) -> dict[str, Any]:
    return {
        "facets": filter_facets(rows, facets, flags, labels),
        "sort": sort,
        "sorts": list(sorts),
        "total": len(rows),
    }


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
    env.policies["json.dumps_kwargs"] = {"ensure_ascii": False, "sort_keys": True}
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
    linked = set(record_tags(record))
    refs = ref_keys(fm)
    skip = {*_PAGE_HEAD_KEYS, *_FACT_KEYS, *refs}
    return {
        "title": _title(record),
        "stem": record.stem,
        "state": state,
        "tags": [
            {
                "text": str(t),
                "href": f"../../{tag_page_path(record.root, t)}" if t in linked else None,
            }
            for t in tags
        ],
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


def _iso_date(value: Any) -> str:
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    text = "" if value is None else str(value)
    return text if _ISO_DATE.fullmatch(text) else ""


def _row(record: SiteRecord, state: RecordState, order: int) -> dict[str, Any]:
    """One list row: what `record_row` shows plus the `data-*` the filter reads."""
    fm = record.frontmatter
    created_by = fm.get("created_by")
    return {
        "ref": record.ref,
        "page": record.page,
        "title": _title(record),
        "summary": _summary(record),
        "state": state,
        "data": {
            "type": record.type,
            "source": record.root,
            "status": state.status or "",
            "flags": " ".join(state.reasons),
            "updated": _iso_date(fm.get("updated_at")),
            "title": _title(record),
            "created-by": "" if created_by is None else str(created_by),
            "order": str(order),
        },
    }


def _item_row(site: Site, item: OpenItem, items_root: str | None, order: int) -> dict[str, Any]:
    """An open item's review row: the `record_row` data keys, flag `open`, no type or source."""
    target = None if item.record is None else site.resolve_ref(item.record, items_root or "")
    return {
        "item": True,
        "ref": item.id,
        "page": target.page if isinstance(target, SiteRecord) else None,
        "title": item.title,
        "data": {
            "type": "",
            "source": "",
            "status": "open",
            "flags": "open",
            "updated": "",
            "title": item.title,
            "created-by": "",
            "order": str(order),
        },
    }


def _tree_view(root: str, nodes: Sequence[TagNode]) -> list[dict[str, Any]]:
    """Tag nodes for `tag_tree`, each linking its page from inside `{root}/tags/`."""
    return [
        {
            "tag": node.tag,
            "count": node.count,
            "description": node.description,
            "href": posixpath.basename(tag_page_path(root, node.tag)),
            "children": _tree_view(root, node.children),
        }
        for node in nodes
    ]


def _nav(
    site: Site,
    present: list[str],
    states: dict[SiteRecord, RecordState],
    labels: Labels,
    open_items: Sequence[OpenItem],
    trees: dict[str, list[TagNode]],
) -> dict[str, Any]:
    """The sidebar: overview, review, all records, types, tags per root, sources."""
    return {
        "review": sum(1 for r in site.records if states[r].reasons) + len(open_items),
        "records": len(site.records),
        "types": [
            {
                "label": labels.type_plural(type_),
                "count": sum(1 for r in site.records if r.type == type_),
                "href": f"records.html#type={type_}",
            }
            for type_ in present
        ],
        "tags": [
            {
                "root": root.name,
                "href": f"{root.name}/tags/index.html",
                "nodes": [
                    {
                        "tag": node.tag,
                        "count": node.count,
                        "href": tag_page_path(root.name, node.tag),
                    }
                    for node in nodes
                ],
            }
            for root in site.roots
            if (nodes := trees[root.name])
        ],
        "sources": [
            {
                "label": root.name,
                "count": sum(1 for r in site.records if r.root == root.name),
                "href": f"{root.name}/index.html",
            }
            for root in site.roots
        ],
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
    *,
    open_items: Sequence[OpenItem] = (),
    items_root: str | None = None,
) -> tuple[dict[str, str | bytes], list[SiteWarning]]:
    """Out-root-relative path → file content, plus the resolution warnings sorted by
    `(path, line)`, each once per record. Types order as `known_types`, then the types
    a root's `_schemas/` added, sorted. No `labels` → English. A `site_url` adds a
    `404.html` resolving its links against the URL's path. `open_items` are the
    vault's open items, their `record:` refs resolved from root `items_root`."""
    if labels is None:
        labels, lang, _ = load_labels({})
    env = environment(labels, lang, site_title)
    files: dict[str, str | bytes] = {
        **font_files(),
        "style.css": (_HERE / "style.css").read_text(),
        "site.js": (_HERE / "site.js").read_text(),
        "filter.js": (_HERE / "filter.js").read_text(),
    }
    warnings: set[SiteWarning] = set()

    added = sorted({r.type for r in site.records} - set(known_types))
    present = [t for t in [*known_types, *added] if any(r.type == t for r in site.records)]
    # Page order: roots in order, types in site type order, records by number.
    ordered = [
        r
        for root in site.roots
        for type_ in present
        for r in site.records
        if r.root == root.name and r.type == type_
    ]

    marks: dict[int, list[Mark]] = {}
    states: dict[SiteRecord, RecordState] = {}
    rendered: dict[int, Rendered] = {}
    for record in site.records:
        own = rendered[id(record)] = _render(site, record)
        marks[id(record)] = own.marks
        states[record] = record_state(record, own.marks)

    trees: dict[str, list[TagNode]] = {}
    for root in site.roots:
        trees[root.name], tree_warnings = tag_tree(root, site.records)
        warnings.update(tree_warnings)
    nav = _nav(site, present, states, labels, open_items, trees)

    def page(template: str, path: str, title: str, crumbs: list[Crumb], **ctx: Any) -> None:
        prefix = "../" * path.count("/")
        files[path] = env.get_template(template).render(
            title=title, prefix=prefix, path=path, crumbs=crumbs, nav=nav, **ctx
        )

    for record in site.records:
        own = rendered[id(record)]
        state = states[record]
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

    for root in site.roots:
        records = [r for r in site.records if r.root == root.name]
        types_: list[dict[str, Any]] = []
        for type_ in present:
            of_type = [r for r in records if r.type == type_]
            if not of_type:
                continue
            types_.append({"type": type_, "count": len(of_type)})
            type_rows = [_row(r, states[r], n) for n, r in enumerate(of_type)]
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
                rows=type_rows,
                filters=_filters(type_rows, labels),
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

    for root in site.roots:
        nodes = trees[root.name]
        if not nodes:
            continue
        overview = Crumb(labels.ui("overview"), "../../index.html")
        source = Crumb(root.name, "../index.html")
        page(
            "tags.html.j2",
            f"{root.name}/tags/index.html",
            labels.ui("tags"),
            [overview, source, Crumb(labels.ui("tags"), None)],
            tree=_tree_view(root.name, nodes),
        )
        own = [r for r in ordered if r.root == root.name]
        stack = list(nodes)
        while stack:
            node = stack.pop()
            stack.extend(node.children)
            parts = node.tag.split(":")
            ancestors = [":".join(parts[:n]) for n in range(1, len(parts))]
            rows = [_row(r, states[r], n) for n, r in enumerate(tagged(node.tag, own))]
            page(
                "tag.html.j2",
                tag_page_path(root.name, node.tag),
                node.tag,
                [
                    overview,
                    source,
                    Crumb(labels.ui("tags"), "index.html"),
                    *(Crumb(a, posixpath.basename(tag_page_path(root.name, a))) for a in ancestors),
                    Crumb(node.tag, None),
                ],
                tag=node.tag,
                description=node.description,
                tree=_tree_view(root.name, node.children),
                rows=rows,
                filters=_filters(rows, labels, facets=("type", "status", "flag")),
            )

    all_rows = [_row(r, states[r], n) for n, r in enumerate(ordered)]
    page(
        "records.html.j2",
        "records.html",
        labels.ui("all_records"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("all_records"), None)],
        rows=all_rows,
        filters=_filters(all_rows, labels),
    )
    pool = [r for r in ordered if states[r].reasons]
    review_rows = [_row(r, states[r], n) for n, r in enumerate(pool)]
    review_rows += [
        _item_row(site, item, items_root, len(pool) + n) for n, item in enumerate(open_items)
    ]
    page(
        "review.html.j2",
        "review.html",
        labels.ui("review_title"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("review"), None)],
        rows=review_rows,
        filters=_filters(review_rows, labels, "review", REVIEW_SORTS, REVIEW_FACETS, REVIEW_FLAGS),
    )
    dated = [(_iso_date(r.frontmatter.get("updated_at")), r) for r in ordered]
    # Stable sort: equal dates keep page order.
    recent = sorted((d for d in dated if d[0]), key=lambda d: d[0], reverse=True)[:_RECENT]
    page(
        "index.html.j2",
        "index.html",
        site_title,
        [Crumb(labels.ui("overview"), None)],
        lead=lead_summary(site),
        needs=nav["review"],
        questions=sum(states[r].clarify for r in site.records),
        types=[
            {
                "type": type_,
                "count": sum(1 for r in site.records if r.type == type_),
                "href": f"records.html#type={type_}",
            }
            for type_ in present
        ],
        recent=[
            {
                "ref": r.ref,
                "page": r.page,
                "title": _title(r),
                "datetime": iso,
                "date": labels.date(iso),
            }
            for iso, r in recent
        ],
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
