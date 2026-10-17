from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

from markdown_it.token import Token

from booping.specs.site.labels import Labels

_COLUMNS = ["Option", "Status", "Complexity", "Reversibility", "Verdict"]
_OPTION = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")
_LEVELS = ("low", "medium", "high")
_STATUS_CSS = {"accepted": "ok", "proposed": "warn"}
_STATUS_ICONS = {"accepted": "i-accepted", "proposed": "i-planned", "rejected": "i-rejected"}


@dataclass(frozen=True)
class Row:
    status: str
    complexity: str
    reversibility: str
    verdict: Token


def _badge(css: str, icon: str | None, text: str) -> str:
    svg = f'<svg class="ic" aria-hidden="true"><use href="#{icon}"/></svg>' if icon else ""
    return f'<span class="b {css}">{svg}{escape(text)}</span>'


def _chosen(labels: Labels) -> str:
    return _badge("ok", "i-accepted", labels.ui("chosen"))


def _level(labels: Labels, value: str) -> str:
    return labels.ui(f"level_{value}") if value in _LEVELS else value


def _meta(row: Row, labels: Labels) -> str:
    if row.status == "accepted":
        status = _chosen(labels)
    else:
        status = _badge(
            _STATUS_CSS.get(row.status, "plain"),
            _STATUS_ICONS.get(row.status, "i-open"),
            labels.status(row.status),
        )
    complexity = f"{labels.ui('complexity')}: {_level(labels, row.complexity)}"
    reversibility = f"{labels.ui('reversibility')}: {_level(labels, row.reversibility)}"
    return (
        f'<span class="meta">{status}{_badge("plain", None, complexity)}'
        f"{_badge('plain', None, reversibility)}</span>"
    )


def _block(content: str) -> Token:
    return Token("html_block", "", 0, content=content, block=True)


def _verdict(row: Row) -> list[Token]:
    open_ = Token("paragraph_open", "p", 1, block=True)
    open_.attrSet("class", "verdict")
    inline = Token(
        "inline", "", 0, content=row.verdict.content, children=list(row.verdict.children or [])
    )
    return [open_, inline, Token("paragraph_close", "p", -1, block=True)]


def _section_end(tokens: list[Token], start: int, max_level: int) -> int:
    for index in range(start, len(tokens)):
        token = tokens[index]
        if token.type == "heading_open" and token.level == 0 and int(token.tag[1:]) <= max_level:
            return index
    return len(tokens)


def _rows(tokens: list[Token], start: int, end: int) -> list[tuple[Token, list[Token]]]:
    rows: list[tuple[Token, list[Token]]] = []
    for token in tokens[start:end]:
        if token.type == "tr_open":
            rows.append((token, []))
        elif token.type == "inline" and rows:
            rows[-1][1].append(token)
    return rows


def option_cards(tokens: list[Token], labels: Labels) -> list[Token]:
    """An ADR's `## Alternatives`: the options table marks accepted rows `chosen`, and
    each `###` option becomes a `<details class="opt">` card — accepted first and open,
    with the row's meta and verdict. Any other shape returns `tokens` untouched."""
    alts = [
        i
        for i, t in enumerate(tokens)
        if t.type == "heading_open"
        and t.tag == "h2"
        and t.level == 0
        and tokens[i + 1].content.strip() == "Alternatives"
    ]
    if len(alts) != 1:
        return tokens
    table = alts[0] + 3
    end = _section_end(tokens, table, 2)
    if table >= end or tokens[table].type != "table_open":
        return tokens
    table_end = next(i for i in range(table, end) if tokens[i].type == "table_close")
    rows = _rows(tokens, table, table_end)
    if not rows or [c.content.strip() for c in rows[0][1]] != _COLUMNS:
        return tokens

    tokens[table].attrJoin("class", "alts")
    by_anchor: dict[str, Row] = {}
    for tr, cells in rows[1:]:
        if len(cells) != len(_COLUMNS):
            continue
        status = cells[1].content.strip()
        if status == "accepted":
            tr.attrJoin("class", "chosen")
            badge = Token("html_inline", "", 0, content=" " + _chosen(labels))
            cells[1].children = [*(cells[1].children or []), badge]
        match = _OPTION.fullmatch(cells[0].content.strip())
        if match is not None:
            by_anchor.setdefault(
                match.group(1),
                Row(status, cells[2].content.strip(), cells[3].content.strip(), cells[4]),
            )

    starts = [
        i
        for i in range(table_end, end)
        if tokens[i].type == "heading_open" and tokens[i].tag == "h3" and tokens[i].level == 0
    ]
    cards: list[tuple[bool, list[Token]]] = []
    for n, start in enumerate(starts):
        stop = starts[n + 1] if n + 1 < len(starts) else end
        row = by_anchor.get(str(tokens[start].attrGet("id")))
        chosen = row is not None and row.status == "accepted"
        css = "opt chosen" if chosen else "opt"
        card = [
            _block(f'<details class="{css}"{" open" if chosen else ""}>\n<summary>'),
            *tokens[start : start + 3],
            _block(f'{_meta(row, labels) if row else ""}</summary>\n<div class="in">\n'),
            *(_verdict(row) if row else []),
            *tokens[start + 3 : stop],
            _block("</div>\n</details>\n"),
        ]
        cards.append((chosen, card))
    ordered = [t for chosen, card in cards if chosen for t in card]
    ordered += [t for chosen, card in cards if not chosen for t in card]
    head = tokens[: starts[0]] if starts else tokens[:end]
    return [*head, *ordered, *tokens[end:]]
