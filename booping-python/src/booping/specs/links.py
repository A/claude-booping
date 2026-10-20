from __future__ import annotations

import re
from urllib.parse import unquote

from pydantic import BaseModel

_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"(`+)(?:.+?)(?<!`)\1(?!`)")
_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+[^)]*)?\)")


class Link(BaseModel):
    line: int
    # As written between the parentheses, a `<…>` wrapper removed.
    dest: str
    # `dest` with any `#anchor` stripped, percent-decoded: the file the link points at.
    path: str


def _local_path(dest: str) -> str | None:
    if "://" in dest or dest.startswith(("mailto:", "/", "#")):
        return None
    return unquote(dest.split("#", 1)[0])


def relative_links(text: str, first_line: int = 1) -> list[Link]:
    """Inline links to relative paths, numbered from `first_line`; fenced code
    blocks and inline code spans are skipped."""
    links: list[Link] = []
    fence: str | None = None
    for number, line in enumerate(text.splitlines(), start=first_line):
        opener = _FENCE_RE.match(line)
        if fence is not None:
            if (
                opener is not None
                and opener.group(1)[0] == fence[0]
                and len(opener.group(1)) >= len(fence)
            ):
                fence = None
            continue
        if opener is not None:
            fence = opener.group(1)
            continue
        for match in _LINK_RE.finditer(_CODE_SPAN_RE.sub("", line)):
            dest = match.group(1)
            if dest.startswith("<") and dest.endswith(">"):
                dest = dest[1:-1]
            path = _local_path(dest)
            if path:
                links.append(Link(line=number, dest=dest, path=path))
    return links
