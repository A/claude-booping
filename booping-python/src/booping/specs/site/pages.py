from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from booping.specs.records import unreviewed
from booping.specs.site.markdown import LinkRenderer, Mark, Rendered, render_body
from booping.specs.site.model import RefMiss, Site, SiteRecord

_HERE = Path(__file__).parent
_HEADER_KEYS = ("type", "title", "summary", "status", "kind")
_MARK_KINDS = ("clarify", "unknown")


class SiteWarning(NamedTuple):
    path: Path
    line: int
    message: str


@dataclass(frozen=True)
class Crumb:
    label: str
    href: str | None


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_HERE / "templates")),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _title(record: SiteRecord) -> str:
    title = record.frontmatter.get("title")
    return str(title) if title else record.stem


def _record_href(record: SiteRecord) -> str:
    # Every link source sits two directories below the out root ({root}/{type}/…).
    return f"../../{record.page}"


def _link_renderer(site: Site, record: SiteRecord, id_prefix: str) -> LinkRenderer:
    def link(dest: str) -> tuple[str | None, str | None]:
        target = site.resolve_link(dest, record)
        if target.kind == "external":
            return dest, None
        if target.kind == "anchor":
            return (f"#{id_prefix}{dest[1:]}" if id_prefix else dest), None
        if target.kind == "record" and target.record is not None:
            anchor = f"#{target.anchor}" if target.anchor else ""
            return _record_href(target.record) + anchor, None
        return None, target.kind

    return link


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


def _counts(marks: list[Mark]) -> dict[str, int]:
    return {kind: sum(1 for m in marks if m.kind == kind) for kind in _MARK_KINDS}


def _block(
    site: Site,
    record: SiteRecord,
    rendered: Rendered,
    title_href: str | None,
    warnings: set[SiteWarning],
) -> dict[str, Any]:
    fm = record.frontmatter
    badge = fm.get("status") if fm.get("status") is not None else fm.get("kind")
    summary = fm.get("summary")
    counts = _counts(rendered.marks)
    return {
        "title": _title(record),
        "title_href": title_href,
        "ref": record.ref,
        "stem": record.stem,
        "badge": None if badge is None else str(badge),
        "unreviewed": unreviewed(record),
        "clarify": counts["clarify"],
        "unknown": counts["unknown"],
        "summary": None if summary is None else str(summary),
        "facts": [
            {"key": key, "items": _fact_items(site, record, value, warnings)}
            for key, value in fm.items()
            if key not in _HEADER_KEYS
        ],
        "body": Markup(rendered.html),
    }


def _render(site: Site, record: SiteRecord, id_prefix: str) -> Rendered:
    return render_body(
        record.body,
        first_line=record.body_first_line,
        id_prefix=id_prefix,
        link=_link_renderer(site, record, id_prefix),
        statuses=site.statuses,
    )


def build_site(site: Site, known_types: list[str]) -> tuple[dict[str, str], list[SiteWarning]]:
    """Out-root-relative path → file content, plus the resolution warnings sorted by
    `(path, line)`, each once per record."""
    env = _env()
    files: dict[str, str] = {"style.css": (_HERE / "style.css").read_text()}
    warnings: set[SiteWarning] = set()

    def page(template: str, path: str, title: str, crumbs: list[Crumb], **ctx: Any) -> None:
        prefix = "../" * path.count("/")
        files[path] = env.get_template(template).render(
            title=title, prefix=prefix, crumbs=crumbs, **ctx
        )

    marks: dict[int, list[Mark]] = {}
    type_blocks: dict[int, dict[str, Any]] = {}
    for record in site.records:
        own = _render(site, record, "")
        marks[id(record)] = own.marks
        for line, dest in own.links:
            if site.resolve_link(dest, record).kind == "unresolved":
                warnings.add(SiteWarning(record.path, line, f"unresolved link {dest}"))
        title = _title(record)
        backlinks = [
            {
                "href": _record_href(src),
                "ref": src.ref if src.root == record.root else f"{src.root}:{src.ref}",
                "title": _title(src),
            }
            for src in site.backlinks(record)
        ]
        page(
            "record.html.j2",
            record.page,
            title,
            [
                Crumb("Specs", "../../index.html"),
                Crumb(record.root, "../index.html"),
                Crumb(record.type, "index.html"),
                Crumb(record.ref, None),
            ],
            record=_block(site, record, own, None, warnings),
            backlinks=backlinks,
        )
        in_type = _render(site, record, f"{record.stem}--")
        type_blocks[id(record)] = _block(site, record, in_type, f"{record.stem}.html", warnings)

    present = [t for t in known_types if any(r.type == t for r in site.records)]
    index_rows: list[dict[str, Any]] = []
    for root in site.roots:
        records = [r for r in site.records if r.root == root.name]
        root_marks = [m for r in records for m in marks[id(r)]]
        type_rows: list[dict[str, Any]] = []
        for type_ in present:
            of_type = [r for r in records if r.type == type_]
            if not of_type:
                continue
            type_marks = [m for r in of_type for m in marks[id(r)]]
            type_rows.append(
                {
                    "name": type_,
                    "href": f"{type_}/index.html",
                    "records": len(of_type),
                    "unreviewed": sum(1 for r in of_type if unreviewed(r)),
                    **_counts(type_marks),
                }
            )
            page(
                "type.html.j2",
                f"{root.name}/{type_}/index.html",
                type_,
                [
                    Crumb("Specs", "../../index.html"),
                    Crumb(root.name, "../index.html"),
                    Crumb(type_, None),
                ],
                type=type_,
                records=[type_blocks[id(r)] for r in of_type],
            )
        mark_lists = [
            (
                kind,
                [
                    {
                        "href": f"{r.type}/{r.stem}.html#L{m.line}",
                        "ref": r.ref,
                        "title": _title(r),
                        "text": m.text,
                    }
                    for r in records
                    for m in marks[id(r)]
                    if m.kind == kind
                ],
            )
            for kind in _MARK_KINDS
        ]
        page(
            "root.html.j2",
            f"{root.name}/index.html",
            root.name,
            [Crumb("Specs", "../index.html"), Crumb(root.name, None)],
            root=root.name,
            rows=type_rows,
            marks=mark_lists,
        )
        counts_by_type = {row["name"]: row["records"] for row in type_rows}
        index_rows.append(
            {
                "name": root.name,
                "href": f"{root.name}/index.html",
                "records": len(records),
                "cells": [
                    {
                        "count": counts_by_type.get(type_, 0),
                        "href": f"{root.name}/{type_}/index.html",
                    }
                    for type_ in present
                ],
                "unreviewed": sum(1 for r in records if unreviewed(r)),
                **_counts(root_marks),
            }
        )

    page(
        "index.html.j2",
        "index.html",
        "Specs",
        [Crumb("Specs", None)],
        types=present,
        rows=index_rows,
    )
    return files, sorted(warnings)
