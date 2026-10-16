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

from booping.specs.site.backlinks import backlink_groups
from booping.specs.site.fonts import font_files
from booping.specs.site.items import OpenItem
from booping.specs.site.labels import Labels, load_labels
from booping.specs.site.machine import index_json, lead_summary, llms_txt
from booping.specs.site.markdown import LinkRenderer, Rendered, render_body
from booping.specs.site.model import (
    RefMiss,
    Site,
    SiteRecord,
    SiteWarning,
    ref_keys,
    ref_values,
)
from booping.specs.site.plan_pages import (
    plans_href,
    recent_plans,
    render_work,
    work_nav,
    work_search_entries,
)
from booping.specs.site.plans import Work
from booping.specs.site.search import search_body_js, search_index_js
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


def _shown_ref(record: SiteRecord, base: str) -> str:
    """`record`'s ref as shown on a page whose own root is `base`: bare in `base`,
    `{root}:{ref}` from any other root."""
    return record.ref if record.root == base else f"{record.root}:{record.ref}"


def _rel_item(target: SiteRecord, base: str) -> dict[str, Any]:
    return {
        "href": _record_href(target),
        "title": _title(target),
        "ref": _shown_ref(target, base),
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
    site: Site, record: SiteRecord, labels: Labels, warnings: set[SiteWarning], base: str
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
                items.append(_rel_item(resolved, base))
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
                "items": [_rel_item(r, base) for r in superseders],
            }
        )
    return rows


def _toc(rendered: Rendered, labels: Labels) -> list[dict[str, Any]]:
    """`h2` entries with their `h3` entries nested, then "Referenced by"; an `h3`
    before any `h2` stands on its own. Fewer than two entries → no ToC."""
    entries: list[dict[str, Any]] = []
    for heading in rendered.headings:
        entry: dict[str, Any] = {"href": f"#{heading.id}", "text": heading.text, "children": []}
        if heading.level == 2 or (heading.level == 3 and not entries):
            entries.append(entry)
        elif heading.level == 3:
            entries[-1]["children"].append(entry)
    entries.append({"href": "#referenced-by", "text": labels.ui("referenced_by"), "children": []})
    return entries if len(entries) >= 2 else []


def _questions(rendered: Rendered) -> list[dict[str, Any]]:
    return [
        {"href": f"#L{m.line}", "kind": m.kind, "text": m.text}
        for kind in _MARK_KINDS
        for m in rendered.marks
        if m.kind == kind
    ]


def _record_view(
    site: Site,
    record: SiteRecord,
    rendered: dict[int, Rendered],
    types: Sequence[str],
    state: RecordState,
    labels: Labels,
    warnings: set[SiteWarning],
    base: str,
) -> dict[str, Any]:
    """`base` is the root whose refs show bare; any other root's show namespaced."""
    fm = record.frontmatter
    own = rendered[id(record)]
    groups = backlink_groups(site, record, rendered, labels, types)
    raw_tags: Any = fm.get("tags") or []
    tags: list[Any] = raw_tags if isinstance(raw_tags, list) else [raw_tags]  # pyright: ignore[reportUnknownVariableType]
    linked = set(record_tags(record))
    refs = ref_keys(fm)
    skip = {*_PAGE_HEAD_KEYS, *_FACT_KEYS, *refs}
    return {
        "title": _title(record),
        "ref": _shown_ref(record, base),
        "page": record.page,
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
        "relations": _relations(site, record, labels, warnings, base),
        "raw": [
            {"key": key, "items": _fact_items(site, record, value, warnings)}
            for key, value in fm.items()
            if key not in skip
        ],
        "body": Markup(own.html),
        "toc": _toc(own, labels),
        "questions": _questions(own),
        "backlinks": {
            "by_type": [
                {
                    "label": group.label,
                    "items": [
                        {"item": _rel_item(b.record, base), "via": b.via} for b in group.items
                    ],
                }
                for group in groups.by_type
            ],
            "by_section": [
                {
                    "heading": section.heading,
                    "sources": [_rel_item(src, base) for src in section.sources],
                }
                for section in groups.by_section
            ],
        },
    }


def _iso_date(value: Any) -> str:
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    text = "" if value is None else str(value)
    return text if _ISO_DATE.fullmatch(text) else ""


def _landing(
    records: Sequence[SiteRecord],
    states: dict[SiteRecord, RecordState],
    present: Sequence[str],
    labels: Labels,
    needs: int,
    type_href: str,
    prefix: str,
    base: str | None,
) -> dict[str, Any]:
    """The Overview landing over `records` (in page order): callout counts, one card per
    present type holding records, and the latest-updated records. `type_href` is
    formatted with `type`; `prefix` leads each recent record's page path; `base` is the
    root whose refs show bare, None for every root's."""
    dated = [(_iso_date(r.frontmatter.get("updated_at")), r) for r in records]
    # Stable sort: equal dates keep page order.
    recent = sorted((d for d in dated if d[0]), key=lambda d: d[0], reverse=True)[:_RECENT]
    return {
        "needs": needs,
        "unreviewed": sum(states[r].unreviewed for r in records),
        "questions": sum(states[r].clarify for r in records),
        "types": [
            {"type": type_, "count": count, "href": type_href.format(type=type_)}
            for type_ in present
            if (count := sum(1 for r in records if r.type == type_))
        ],
        "recent": [
            {
                "ref": _shown_ref(r, base or r.root),
                "page": f"{prefix}{r.page}",
                "title": _title(r),
                "datetime": iso,
                "date": labels.date(iso),
            }
            for iso, r in recent
        ],
    }


def _row(
    record: SiteRecord, state: RecordState, order: int, home: str | None = None
) -> dict[str, Any]:
    """One list row: what `record_row` shows plus the `data-*` the filter reads; a record
    outside a `home` root shows its ref namespaced."""
    fm = record.frontmatter
    created_by = fm.get("created_by")
    return {
        "ref": _shown_ref(record, home or record.root),
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


def _item_row(
    site: Site, item: OpenItem, items_root: str | None, order: int, home: str | None = None
) -> dict[str, Any]:
    """An open item's review row: the `record_row` data keys, flag `open`, no type; its
    source is the `home` root, the vault's own, else none."""
    target = None if item.record is None else site.resolve_ref(item.record, items_root or "")
    return {
        "item": True,
        "ref": item.id,
        "page": target.page if isinstance(target, SiteRecord) else None,
        "title": item.title,
        "data": {
            "type": "",
            "source": home or "",
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
    home: str | None = None,
) -> dict[str, Any]:
    """The sidebar: overview, review, all records, types, tags per root, sources. With a
    `home` root the types count that root's records only and link its type pages, and
    every other root has its own group in place of the sources."""
    registries: list[dict[str, Any]] = []
    types: list[dict[str, Any]] = [
        {
            "label": labels.type_plural(type_),
            "count": sum(1 for r in site.records if r.type == type_),
            "href": f"records.html#type={type_}",
        }
        for type_ in present
    ]
    if home is not None:
        types = _root_types(site, home, present, labels)
        registries = [
            {
                "root": root.name,
                "href": f"{root.name}/index.html",
                "types": _root_types(site, root.name, present, labels),
            }
            for root in site.roots
            if root.name != home
        ]
    return {
        "review": sum(1 for r in site.records if states[r].reasons) + len(open_items),
        "records": len(site.records),
        "types": types,
        "registries": registries,
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
            if (nodes := [node for node in trees[root.name] if node.count])
        ],
        "sources": [
            {
                "label": root.name,
                "count": sum(1 for r in site.records if r.root == root.name),
                "href": f"{root.name}/index.html",
            }
            for root in site.roots
        ]
        if home is None
        else [],
    }


def _root_types(
    site: Site, root: str, present: Sequence[str], labels: Labels
) -> list[dict[str, Any]]:
    """Sidebar entries for the types `root` holds records of, each linking its type page."""
    return [
        {"label": labels.type_plural(type_), "count": count, "href": f"{root}/{type_}/index.html"}
        for type_ in present
        if (count := sum(1 for r in site.records if r.root == root and r.type == type_))
    ]


def _render(site: Site, record: SiteRecord, labels: Labels) -> Rendered:
    return render_body(
        record.body,
        first_line=record.body_first_line,
        link=_link_renderer(site, record),
        statuses=site.statuses,
        labels=labels,
        alternatives=record.type == "adr",
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
    home: str | None = None,
    work: Work | None = None,
) -> tuple[dict[str, str | bytes], list[SiteWarning]]:
    """Out-root-relative path → file content, plus the resolution warnings sorted by
    `(path, line)`, each once per record. Types order as `known_types`, then the types
    a root's `_schemas/` added, sorted. No `labels` → English. A `site_url` adds a
    `404.html` resolving its links against the URL's path. `open_items` are the
    vault's open items, their `record:` refs resolved from root `items_root`.

    `home` names the project's own root: the Overview, its counters and the sidebar
    types cover that root alone, every other root gets its own Overview block and
    sidebar group, its records show refs as `{root}:{ref}`, and the home root's page
    redirects to the Overview. No `home` → every root counts together, refs bare.

    `work` is the home vault's plans and retrospectives: list pages, a page per plan,
    milestone, plan sibling and retrospective, a sidebar group each and the Overview's
    recent plans; ignored without `home`."""
    if labels is None:
        labels, lang, _ = load_labels({})
    env = environment(labels, lang, site_title)
    files: dict[str, str | bytes] = {
        **font_files(),
        "style.css": (_HERE / "style.css").read_text(),
        "site.js": (_HERE / "site.js").read_text(),
        "filter.js": (_HERE / "filter.js").read_text(),
        "filter-format.js": (_HERE / "filter-format.js").read_text(),
        "search.js": (_HERE / "search.js").read_text(),
        "comments-format.js": (_HERE / "comments-format.js").read_text(),
        "comments.js": (_HERE / "comments.js").read_text(),
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

    states: dict[SiteRecord, RecordState] = {}
    rendered: dict[int, Rendered] = {}
    for record in site.records:
        own = rendered[id(record)] = _render(site, record, labels)
        states[record] = record_state(record, own.marks)

    trees: dict[str, list[TagNode]] = {}
    for root in site.roots:
        trees[root.name], tree_warnings = tag_tree(root, site.records)
        warnings.update(tree_warnings)
    nav = _nav(site, present, states, labels, open_items, trees, home)
    if home is None or work is None or not work:
        work = Work()
    nav["work"] = work_nav(work, labels, home) if home is not None else None

    def root_crumbs(root: str, href: str) -> list[Crumb]:
        return [] if root == home else [Crumb(root, href)]

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
                *root_crumbs(record.root, "../index.html"),
                Crumb(labels.type_plural(record.type), "index.html"),
                Crumb(_shown_ref(record, home or record.root), None),
            ],
            record=_record_view(
                site, record, rendered, present, state, labels, warnings, home or record.root
            ),
        )
        files[f"{record.root}/{record.type}/{record.stem}.md"] = record.path.read_bytes()

    for root in site.roots:
        records = [r for r in ordered if r.root == root.name]
        for type_ in present:
            of_type = [r for r in records if r.type == type_]
            if not of_type:
                continue
            type_rows = [_row(r, states[r], n, home) for n, r in enumerate(of_type)]
            page(
                "type.html.j2",
                f"{root.name}/{type_}/index.html",
                labels.type_plural(type_),
                [
                    Crumb(labels.ui("overview"), "../../index.html"),
                    *root_crumbs(root.name, "../index.html"),
                    Crumb(labels.type_plural(type_), None),
                ],
                type=type_,
                rows=type_rows,
                filters=_filters(type_rows, labels),
            )
        if root.name == home:
            files[f"{root.name}/index.html"] = env.get_template("redirect.html.j2").render(
                title=site_title, target="../index.html"
            )
            continue
        page(
            "root.html.j2",
            f"{root.name}/index.html",
            root.name,
            [Crumb(labels.ui("overview"), "../index.html"), Crumb(root.name, None)],
            root=root.name,
            **_landing(
                records,
                states,
                present,
                labels,
                sum(1 for r in records if states[r].reasons),
                "{type}/index.html",
                "../",
                home or root.name,
            ),
        )

    for root in site.roots:
        nodes = trees[root.name]
        if not nodes:
            continue
        overview = Crumb(labels.ui("overview"), "../../index.html")
        source = root_crumbs(root.name, "../index.html")
        page(
            "tags.html.j2",
            f"{root.name}/tags/index.html",
            labels.ui("tags"),
            [overview, *source, Crumb(labels.ui("tags"), None)],
            tree=_tree_view(root.name, nodes),
        )
        own = [r for r in ordered if r.root == root.name]
        stack = list(nodes)
        while stack:
            node = stack.pop()
            stack.extend(node.children)
            parts = node.tag.split(":")
            ancestors = [":".join(parts[:n]) for n in range(1, len(parts))]
            rows = [_row(r, states[r], n, home) for n, r in enumerate(tagged(node.tag, own))]
            page(
                "tag.html.j2",
                tag_page_path(root.name, node.tag),
                node.tag,
                [
                    overview,
                    *source,
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

    if home is not None and work:
        work_statuses = {
            str(doc.frontmatter["status"])
            for doc in work.docs()
            if doc.frontmatter.get("status") is not None
        }
        render_work(site, work, labels, home, site.statuses | work_statuses, page, _filters, Crumb)

    all_rows = [_row(r, states[r], n, home) for n, r in enumerate(ordered)]
    page(
        "records.html.j2",
        "records.html",
        labels.ui("all_records"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("all_records"), None)],
        rows=all_rows,
        filters=_filters(all_rows, labels),
    )
    pool = [r for r in ordered if states[r].reasons]
    review_rows = [_row(r, states[r], n, home) for n, r in enumerate(pool)]
    review_rows += [
        _item_row(site, item, items_root, len(pool) + n, home) for n, item in enumerate(open_items)
    ]
    page(
        "review.html.j2",
        "review.html",
        labels.ui("review_title"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("review"), None)],
        rows=review_rows,
        filters=_filters(review_rows, labels, "review", REVIEW_SORTS, REVIEW_FACETS, REVIEW_FLAGS),
    )
    page(
        "search.html.j2",
        "search.html",
        labels.ui("search"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("search"), None)],
    )
    page(
        "comments.html.j2",
        "comments.html",
        labels.ui("outbox"),
        [Crumb(labels.ui("overview"), "index.html"), Crumb(labels.ui("outbox"), None)],
    )
    if home is None:
        landing = _landing(
            ordered, states, present, labels, nav["review"], "records.html#type={type}", "", None
        )
        review_href = "review.html"
    else:
        home_records = [r for r in ordered if r.root == home]
        needs = sum(1 for r in home_records if states[r].reasons) + len(open_items)
        landing = _landing(
            home_records, states, present, labels, needs, f"{home}/{{type}}/index.html", "", home
        )
        review_href = f"review.html#source={home}"
    registries: list[dict[str, Any]] = []
    for root in site.roots:
        if home is None or root.name == home:
            continue
        records = [r for r in ordered if r.root == root.name]
        other = _landing(
            records,
            states,
            present,
            labels,
            sum(1 for r in records if states[r].reasons),
            f"{root.name}/{{type}}/index.html",
            "",
            home,
        )
        registries.append(
            {
                **other,
                "root": root.name,
                "href": f"{root.name}/index.html",
                "total": len(records),
                "review_href": f"review.html#source={root.name}",
            }
        )
    page(
        "index.html.j2",
        "index.html",
        site_title,
        [Crumb(labels.ui("overview"), None)],
        lead=lead_summary(site, home),
        review_href=review_href,
        registries=registries,
        recent_plans=recent_plans(work, labels),
        plans_href=plans_href(home) if home is not None else "",
        **landing,
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
    files["search-index.js"] = search_index_js(
        site, labels, states, home, work_search_entries(work, labels)
    )
    files["search-body.js"] = search_body_js(site, rendered)
    return files, sorted(warnings)
