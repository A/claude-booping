"""txtar archive format — parse and serialize.

A port of Go's ``golang.org/x/tools/txtar``: an archive is a leading comment
followed by file sections, each introduced by a ``-- name --`` marker line.

Deviation from Go: duplicate section names raise :class:`ValueError` rather
than being silently kept — a case with two ``cmd`` sections is a mistake, not
an archive with two files.

Ported from golang.org/x/tools/txtar, Copyright 2018 The Go Authors, used under
the BSD-3-Clause license; see the LICENSE file at the root of this
distribution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_MARKER_PREFIX = "-- "
_MARKER_SUFFIX = " --"


@dataclass
class Archive:
    """The text before the first marker, then the sections in file order."""

    comment: str = ""
    files: list[tuple[str, str]] = field(default_factory=list)


def parse(text: str) -> Archive:
    archive = Archive()
    name: str | None = None
    buffer: list[str] = []

    for line in _split_lines(text):
        marker = _marker_name(line)
        if marker is None:
            buffer.append(line)
            continue
        _flush(archive, name, buffer)
        if any(marker == existing for existing, _ in archive.files):
            raise ValueError(f"duplicate section: {marker}")
        name = marker
        buffer = []

    _flush(archive, name, buffer)
    return archive


def serialize(archive: Archive) -> str:
    parts = [_fix_newline(archive.comment)]
    for name, data in archive.files:
        parts.append(f"{_MARKER_PREFIX}{name}{_MARKER_SUFFIX}\n")
        parts.append(_fix_newline(data))
    return "".join(parts)


def _flush(archive: Archive, name: str | None, buffer: list[str]) -> None:
    data = _fix_newline("".join(buffer))
    if name is None:
        archive.comment = data
    else:
        archive.files.append((name, data))


def _marker_name(line: str) -> str | None:
    """The section name of a ``-- name --`` line, or ``None`` for content.

    An empty name is not a marker, matching Go, which treats such a line as
    ordinary content.
    """
    stripped = line.removesuffix("\n")
    if not (stripped.startswith(_MARKER_PREFIX) and stripped.endswith(_MARKER_SUFFIX)):
        return None
    if len(stripped) < len(_MARKER_PREFIX) + len(_MARKER_SUFFIX):
        return None
    name = stripped[len(_MARKER_PREFIX) : -len(_MARKER_SUFFIX)].strip()
    return name or None


def _split_lines(text: str) -> list[str]:
    """Split on ``\\n`` only, keeping the terminator.

    ``str.splitlines`` also breaks on form feed and the Unicode separators,
    which would corrupt section content that contains them.
    """
    lines: list[str] = []
    start = 0
    while start < len(text):
        end = text.find("\n", start)
        if end < 0:
            lines.append(text[start:])
            break
        lines.append(text[start : end + 1])
        start = end + 1
    return lines


def _fix_newline(data: str) -> str:
    if data == "" or data.endswith("\n"):
        return data
    return data + "\n"
