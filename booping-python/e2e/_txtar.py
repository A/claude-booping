"""Vendored txtar parser — stdlib-only implementation matching Go's txtar package."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Archive:
    """A parsed txtar archive: leading comment + ordered file list."""

    comment: str = ""
    files: list[tuple[str, str]] = field(default_factory=list)


_HEADER_RE = re.compile(r"^-- (.+) --$")


def parse(text: str) -> Archive:
    """Parse a txtar-format string into an Archive.

    Rules follow Go's txtar package:
    - Text before the first ``-- name --`` line is the leading comment.
    - Each ``-- name --`` line starts a new section; content runs until the
      next header or end of input.
    - Section names may contain ``/``.
    - Duplicate section names raise ``ValueError``.
    """
    seen: set[str] = set()
    files: list[tuple[str, str]] = []
    lines = text.split("\n")

    # Find first header
    header_idx = -1
    for i, line in enumerate(lines):
        if _HEADER_RE.match(line):
            header_idx = i
            break

    if header_idx == -1:
        return Archive(comment=text, files=[])

    comment = "\n".join(lines[:header_idx])

    # Walk headers in order, collecting content between them
    cursor = header_idx
    while cursor < len(lines):
        m = _HEADER_RE.match(lines[cursor])
        if not m:
            break  # safety: should not happen in well-formed input

        name = m.group(1)
        if name in seen:
            raise ValueError(f"duplicate section name: {name!r}")
        seen.add(name)
        cursor += 1  # move past header line

        # Find next header (or end of lines)
        next_header = cursor
        while next_header < len(lines):
            if _HEADER_RE.match(lines[next_header]):
                break
            next_header += 1

        content = "\n".join(lines[cursor:next_header])
        files.append((name, content))
        cursor = next_header

    return Archive(comment=comment, files=files)


def serialize(archive: Archive) -> str:
    """Serialize an Archive back to txtar format.

    Produces a byte-exact roundtrip for any archive produced by ``parse``.
    """
    parts: list[str] = []

    if archive.comment:
        parts.append(archive.comment)

    for name, content in archive.files:
        parts.append(f"-- {name} --")
        parts.append(content)

    return "\n".join(parts)
