from __future__ import annotations

import re
from collections.abc import Callable, Collection
from dataclasses import dataclass
from html import escape

from markdown_it import MarkdownIt
from markdown_it.token import Token

from booping.specs.site.adr import option_cards
from booping.specs.site.labels import Labels, load_labels

LinkRenderer = Callable[[str], tuple[str | None, str | None]]

_MARK_RE = re.compile(r"\[(clarify|unknown)\]")
_SLUG_DROP_RE = re.compile(r"[^\w\- ]")
_WS_RE = re.compile(r"\s+")
_MARK_TEXT_LIMIT = 160
_ANCHOR_OPEN = ("tr_open", "list_item_open", "paragraph_open", "heading_open")
_ANCHOR_CLOSE = ("tr_close", "list_item_close", "paragraph_close", "heading_close")
_SECTION_TAGS = ("h2", "h3", "h4")


@dataclass(frozen=True)
class Mark:
    line: int
    kind: str
    text: str


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    id: str
    line: int


@dataclass(frozen=True)
class Rendered:
    html: str
    marks: list[Mark]
    links: list[tuple[int, str]]
    headings: list[Heading]
    # The body's plain text for search: every inline token's text, whitespace collapsed.
    text: str = ""


def section_anchor(id_: str, text: str, labels: Labels) -> str:
    label = escape(f"{labels.ui('section_link')}: {text}")
    return f'<a class="anchor" href="#{escape(id_)}" aria-label="{label}">§</a>'


def slug(text: str) -> str:
    """GitHub's heading anchor, so the `#anchors` records already write keep working."""
    return _SLUG_DROP_RE.sub("", text.lower()).replace(" ", "-")


def _unique_slug(text: str, seen: dict[str, int]) -> str:
    base = slug(text)
    count = seen.get(base, 0)
    seen[base] = count + 1
    return base if count == 0 else f"{base}-{count}"


def _plain(inline: Token) -> str:
    parts: list[str] = []
    for child in inline.children or []:
        if child.type in ("text", "code_inline"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts)


def _cut(text: str) -> str:
    text = _WS_RE.sub(" ", text).strip()
    if len(text) > _MARK_TEXT_LIMIT:
        return text[:_MARK_TEXT_LIMIT] + "…"
    return text


def _html_token(content: str) -> Token:
    return Token("html_inline", "", 0, content=content)


def _split_marks(children: list[Token]) -> tuple[list[Token], list[tuple[Token, str]]]:
    """Text children with `[clarify]`/`[unknown]` split around a `<mark>`; code spans are
    separate tokens, so they are never touched."""
    out: list[Token] = []
    marks: list[tuple[Token, str]] = []
    for child in children:
        if child.type != "text" or _MARK_RE.search(child.content) is None:
            out.append(child)
            continue
        pos = 0
        for match in _MARK_RE.finditer(child.content):
            if match.start() > pos:
                out.append(Token("text", "", 0, content=child.content[pos : match.start()]))
            kind = match.group(1)
            token = _html_token(
                f'<mark class="mk mk-{kind}"><svg class="ic" aria-hidden="true">'
                f'<use href="#i-{kind}"/></svg>[{kind}]</mark>'
            )
            out.append(token)
            marks.append((token, kind))
            pos = match.end()
        if pos < len(child.content):
            out.append(Token("text", "", 0, content=child.content[pos:]))
    return out, marks


def _render_links(
    children: list[Token], start_line: int, link: LinkRenderer, links: list[tuple[int, str]]
) -> None:
    line = start_line
    pending_span: list[bool] = []
    for index, child in enumerate(children):
        if child.type in ("softbreak", "hardbreak"):
            line += 1
        elif child.type == "link_open":
            dest = str(child.attrGet("href") or "")
            links.append((line, dest))
            href, css_class = link(dest)
            if href is None:
                attr = f' class="{escape(css_class)}"' if css_class else ""
                children[index] = _html_token(f"<span{attr}>")
                pending_span.append(True)
            else:
                child.attrSet("href", href)
                if css_class:
                    child.attrSet("class", css_class)
                pending_span.append(False)
        elif child.type == "link_close" and pending_span.pop():
            children[index] = _html_token("</span>")


def render_body(
    text: str,
    *,
    first_line: int,
    link: LinkRenderer,
    statuses: Collection[str],
    labels: Labels | None = None,
    alternatives: bool = False,
) -> Rendered:
    if labels is None:
        labels = load_labels({})[0]
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    # Keep each destination as written, so callers resolve and report the author's text.
    md.normalizeLink = lambda url: url  # type: ignore[method-assign]
    tokens = md.parse(text)
    row_text = _row_texts(tokens)
    seen_slugs: dict[str, int] = {}
    anchored_lines: set[int] = set()
    marks: list[Mark] = []
    links: list[tuple[int, str]] = []
    headings: list[tuple[Token, Heading]] = []
    texts: list[str] = []
    # Open blocks that can carry a mark anchor.
    stack: list[Token] = []

    for index, token in enumerate(tokens):
        if token.type in _ANCHOR_OPEN:
            stack.append(token)
        elif token.type in _ANCHOR_CLOSE:
            stack.pop()
        if token.type == "heading_open":
            text = _plain(tokens[index + 1])
            heading_id = _unique_slug(text, seen_slugs)
            token.attrSet("id", heading_id)
            line = first_line + (token.map or [0])[0]
            heading = Heading(int(token.tag[1:]), text.strip(), heading_id, line)
            headings.append((tokens[index + 1], heading))
        if token.type == "inline":
            texts.append(_plain(token))
        if token.type != "inline" or token.map is None:
            continue
        if tokens[index - 1].type in ("td_open", "th_open") and token.content.strip() in statuses:
            status = escape(token.content.strip())
            token.children = [_html_token(f'<span class="badge st-{status}">{status}</span>')]
            continue
        plain = _plain(token)
        children, found = _split_marks(token.children or [])
        _render_links(children, first_line + token.map[0], link, links)
        token.children = children
        if not found:
            continue
        block = _anchor_block(stack)
        line = first_line + (block.map or token.map)[0]
        if line not in anchored_lines:
            anchored_lines.add(line)
            anchor_id = f"L{line}"
            if block.type == "heading_open":
                first_mark = found[0][0]
                first_mark.content = first_mark.content.replace(
                    "<mark ", f'<mark id="{anchor_id}" ', 1
                )
            else:
                block.attrSet("id", anchor_id)
        block_text = _cut(row_text[id(block)] if block.type == "tr_open" else plain)
        seen_kinds: set[str] = set()
        for _, kind in found:
            if kind not in seen_kinds:
                seen_kinds.add(kind)
                marks.append(Mark(line=line, kind=kind, text=block_text))

    for inline, heading in headings:
        if f"h{heading.level}" in _SECTION_TAGS:
            inline.children = [
                *(inline.children or []),
                _html_token(section_anchor(heading.id, heading.text, labels)),
            ]
    if alternatives:
        tokens = option_cards(tokens, labels)
    return Rendered(
        html=md.renderer.render(tokens, md.options, {}),
        marks=marks,
        links=links,
        headings=[h for _, h in headings],
        text=_WS_RE.sub(" ", " ".join(texts)).strip(),
    )


def _row_texts(tokens: list[Token]) -> dict[int, str]:
    """Plain text of every table row, its cells joined by a space, keyed by `id` of the
    row's `tr_open` token."""
    rows: dict[int, str] = {}
    row: Token | None = None
    cells: list[str] = []
    for token in tokens:
        if token.type == "tr_open":
            row, cells = token, []
        elif token.type == "tr_close" and row is not None:
            rows[id(row)] = " ".join(cells)
            row = None
        elif token.type == "inline" and row is not None:
            cells.append(_plain(token))
    return rows


def _anchor_block(stack: list[Token]) -> Token:
    """The innermost visible block: a tight list's paragraph renders no tag, so its list
    item carries the anchor; a table cell's row carries it for the cell."""
    for token in reversed(stack):
        if token.type == "paragraph_open" and token.hidden:
            continue
        return token
    raise ValueError("inline token outside any block")
