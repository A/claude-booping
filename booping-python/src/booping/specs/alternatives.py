"""The ADR alternatives check: table rows ↔ `###` option blocks, and the accepted count,
under the section and column names the record's own schema declares."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from markdown_it import MarkdownIt
from markdown_it.token import Token
from ruamel.yaml import YAML

from booping.specs.site.markdown import slug

ACCEPTED = "accepted"
EXACTLY_ONE = ("accepted", "superseded")
_TABLE_RE = re.compile(r'^SECTION\("([^"]+)"\)\s*>\s*TABLE$')


@dataclass(frozen=True)
class Names:
    section: str
    option: str
    # None: the schema constrains no column to an enum holding `accepted`.
    status: str | None


@dataclass
class _Row:
    line: int
    cells: dict[str, str]
    anchor: str | None


@dataclass
class _Section:
    rows: list[_Row] = field(default_factory=lambda: list[_Row]())
    headings: list[tuple[int, str]] = field(default_factory=lambda: list[tuple[int, str]]())
    has_table: bool = False


def names(schema: Path) -> list[Names]:
    """One `Names` per rule selecting `SECTION("{name}") > TABLE` with `columns:`; the
    option column is the first, the status column the one a `TD[col=…]` rule of that
    section gives an enum holding `accepted`."""
    # PyYAML rejects plain flow scalars like `[Criteria?, Decision]` that mdcheck accepts.
    data: Any = YAML(typ="safe", pure=True).load(schema.read_text())  # pyright: ignore[reportUnknownMemberType]
    raw: Any = cast("dict[str, Any]", data).get("rules") if isinstance(data, dict) else None
    rules = [
        cast("dict[str, Any]", r)
        for r in cast("list[Any]", raw if isinstance(raw, list) else [])
        if isinstance(r, dict)
    ]
    found: list[Names] = []
    for rule in rules:
        match = _TABLE_RE.match(str(rule.get("select", "")))
        columns: Any = rule.get("columns")
        if match is None or not isinstance(columns, list) or not columns:
            continue
        section = match.group(1)
        found.append(
            Names(
                section=section,
                option=str(cast("list[Any]", columns)[0]),
                status=_status_column(rules, section),
            )
        )
    return found


def _status_column(rules: list[dict[str, Any]], section: str) -> str | None:
    td = re.compile(rf'^SECTION\("{re.escape(section)}"\)\s*>\s*TABLE\s*>\s*TD\[col="([^"]+)"\]$')
    for rule in rules:
        match = td.match(str(rule.get("select", "")))
        enum: Any = rule.get("enum")
        if match is not None and isinstance(enum, list) and ACCEPTED in enum:
            return match.group(1)
    return None


def _plain(inline: Token) -> str:
    return "".join(
        c.content for c in inline.children or [] if c.type in ("text", "code_inline")
    ).strip()


def _anchor(inline: Token) -> str | None:
    for child in inline.children or []:
        if child.type == "link_open":
            href = str(child.attrGet("href") or "")
            return href[1:] if href.startswith("#") else None
    return None


def _section(body: str, first_line: int, names_: Names) -> _Section | None:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    # Keep anchors as written, so a Cyrillic anchor is compared, not its percent-encoding.
    md.normalizeLink = lambda url: url  # type: ignore[method-assign]
    tokens = md.parse(body)
    section: _Section | None = None
    inside = False
    header: list[str] = []
    in_body = False
    row: _Row | None = None
    column = 0
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h1", "h2"):
            inside = token.tag == "h2" and _plain(tokens[index + 1]) == names_.section
            if inside and section is None:
                section = _Section()
            continue
        if not inside or section is None:
            continue
        line = first_line + (token.map[0] if token.map else 0)
        if token.type == "heading_open" and token.tag == "h3":
            section.headings.append((line, _plain(tokens[index + 1])))
        elif token.type == "table_open":
            section.has_table = True
            header = []
        elif token.type in ("tbody_open", "tbody_close"):
            in_body = token.type == "tbody_open"
        elif token.type == "tr_open" and in_body:
            row, column = _Row(line=line, cells={}, anchor=None), 0
        elif token.type == "tr_close" and row is not None:
            section.rows.append(row)
            row = None
        elif token.type == "inline" and tokens[index - 1].type == "th_open":
            header.append(_plain(token))
        elif token.type == "inline" and row is not None:
            if column < len(header):
                row.cells[header[column]] = _plain(token)
                if header[column] == names_.option:
                    row.anchor = _anchor(token)
            column += 1
    return section


def check(body: str, first_line: int, status: Any, checks: list[Names]) -> list[tuple[int, str]]:
    """`(line, message)` per problem; a record missing the section or its table gets
    nothing — mdcheck reports that."""
    found: list[tuple[int, str]] = []
    for names_ in checks:
        section = _section(body, first_line, names_)
        if section is None or not section.has_table:
            continue
        found += _rows_and_headings(section, names_)
        if names_.status is not None:
            found += _accepted(section, names_, status)
    return sorted(found)


def _rows_and_headings(section: _Section, names_: Names) -> list[tuple[int, str]]:
    name = names_.section
    slugs = {slug(heading) for _, heading in section.headings}
    anchors = [r.anchor for r in section.rows if r.anchor is not None]
    found = [
        (r.line, f"option {r.anchor} names no ### in {name}")
        for r in section.rows
        if r.anchor is not None and r.anchor not in slugs
    ]
    for line, heading in section.headings:
        n = anchors.count(slug(heading))
        if n == 0:
            found.append((line, f"### {heading} has no row in {name}"))
        elif n > 1:
            found.append((line, f"### {heading} has {n} rows in {name}"))
    return found


def _accepted(section: _Section, names_: Names, status: Any) -> list[tuple[int, str]]:
    name = names_.section
    accepted = [r for r in section.rows if r.cells.get(str(names_.status)) == ACCEPTED]
    n = len(accepted)
    line = accepted[1].line if n > 1 else 1
    if status in EXACTLY_ONE:
        if n != 1:
            return [(line, f"{n} options accepted in {name}; a {status} record needs exactly one")]
    elif n > 1:
        return [(line, f"{n} options accepted in {name}; at most one")]
    return []
