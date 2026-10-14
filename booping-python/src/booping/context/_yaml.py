from __future__ import annotations

import re
from io import StringIO
from pathlib import Path
from typing import Any

import yaml
from ruamel.yaml import YAML as _RuamelYAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.representer import RoundTripRepresenter


class _NullPreservingRepresenter(RoundTripRepresenter):
    """Round-trip representer that outputs ``null`` instead of empty for None values."""

    def represent_none(self, data: Any) -> Any:
        return self.represent_scalar("tag:yaml.org,2002:null", "null")  # type: ignore[reportUnknownMemberType]


_NullPreservingRepresenter.add_representer(type(None), _NullPreservingRepresenter.represent_none)  # type: ignore[reportUnknownMemberType]


def _rt_yaml() -> _RuamelYAML:
    """Return a ruamel.yaml instance configured for round-trip with null preservation."""
    ry = _RuamelYAML(typ="rt")
    ry.Representer = _NullPreservingRepresenter
    ry.preserve_quotes = True
    return ry


# Wide enough that round-tripping never re-wraps an untouched long line.
_MARKER_WIDTH = 4096


def _load_dict(raw: Any) -> dict[str, Any]:
    # yaml.safe_load returns Any; the isinstance check narrows to dict[Unknown, Unknown]
    # in basedpyright strict mode. The explicit annotation here bridges the gap.
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Any] = {}
    for k, v in raw.items():  # type: ignore[reportUnknownVariableType]
        out[str(k)] = v  # type: ignore[reportUnknownVariableType]
    return out


def safe_load_path(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file; return empty dict on missing or non-dict content."""
    if not path.exists():
        return {}
    return _load_dict(yaml.safe_load(path.read_text()))


def safe_load_str(text: str) -> dict[str, Any]:
    """Parse YAML from a string; return empty dict on non-dict content."""
    return _load_dict(yaml.safe_load(text))


# The block closes at the first line that is exactly `---`; a `---` inside a value
# or an indented block scalar line must not end it.
_FRONTMATTER_RE = re.compile(r"\A---[ \t\r]*\n(.*?)^---[ \t\r]*$\n?", re.S | re.M)


class UnclosedFrontmatterError(ValueError):
    def __init__(self) -> None:
        super().__init__("frontmatter block is not closed")


def _match_frontmatter(text: str) -> re.Match[str] | None:
    """Match of the frontmatter block, or None when the text does not open one.

    Raises :class:`UnclosedFrontmatterError` when the opening line has no closing line.
    """
    if not text.startswith("---"):
        return None
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        raise UnclosedFrontmatterError
    return match


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """YAML text between the delimiter lines (None without frontmatter) and the body."""
    match = _match_frontmatter(text)
    if match is None:
        return None, text
    return match.group(1), text[match.end() :].lstrip("\n")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Split markdown frontmatter from body; frontmatter is parsed YAML."""
    yaml_text, body = split_frontmatter(path.read_text())
    if yaml_text is None:
        return {}, body
    return safe_load_str(yaml_text), body


def parse_frontmatter_only(path: Path) -> dict[str, Any]:
    """Parse only the frontmatter section; ignore body."""
    fm, _ = parse_frontmatter(path)
    return fm


def split_frontmatter_md(text: str) -> tuple[str, str, str]:
    """Split markdown with frontmatter into (before_yaml, yaml_text, after_yaml).

    * ``before_yaml``: opening ``---`` delimiter line.
    * ``yaml_text``: YAML content between the two delimiter lines (may be empty).
    * ``after_yaml``: closing ``---`` delimiter line and body text.

    The original text can be reconstructed as ``before_yaml + yaml_text + after_yaml``.

    Raises :class:`ValueError` if no frontmatter delimiters are found.
    """
    match = _match_frontmatter(text)
    if match is None:
        raise ValueError("No frontmatter opening delimiter")

    before_yaml = text[: match.start(1)]
    yaml_text = match.group(1)
    after_yaml = text[match.end(1) :]

    return before_yaml, yaml_text, after_yaml


def update_marker(path: Path, updates: dict[str, object]) -> None:
    """Set top-level keys on a `.booping` marker file, in place.

    The marker is a bare YAML mapping with no `---` delimiters, so
    :func:`update_frontmatter` cannot serve it: its no-frontmatter fallback
    prepends a frontmatter block and leaves a two-document stream behind.  Here
    the whole file is round-tripped — comments, quoting and key order survive,
    and only the touched lines change.

    Raises :class:`ValueError` when the file is not a YAML mapping.
    """
    ry = _rt_yaml()
    ry.width = _MARKER_WIDTH

    data = ry.load(path.read_text())  # type: ignore[reportUnknownMemberType]
    if data is None:
        data = CommentedMap()
    if not isinstance(data, dict):
        raise ValueError(f"not a YAML mapping: {path}")

    for key, value in updates.items():
        data[key] = value  # type: ignore[reportUnknownMemberType]

    stream = StringIO()
    ry.dump(data, stream)  # type: ignore[reportUnknownMemberType]
    path.write_text(stream.getvalue())


def update_frontmatter(
    path: Path,
    updates: dict[str, object],
    removals: list[str] | None = None,
    appends: list[tuple[str, object]] | None = None,
) -> None:
    """Update frontmatter keys in a markdown file using ruamel.yaml round-trip mode.

    Preserves comments, key order, and body text.  Only the extracted YAML
    block is passed to the parser — the body is never parsed as YAML.

    ``removals`` lists keys to drop from the frontmatter; missing keys are
    ignored.  Removals are applied before updates so a key may be removed and
    re-added in one call.

    ``appends`` lists ``(key, value)`` pairs, each value appended to that
    key's list in order, applied after ``updates``; one key may repeat.  An
    absent or null key becomes a one-element list, a value already in the
    list is a no-op, and an existing scalar raises :class:`ValueError`.

    A file without a frontmatter block gets one prepended; the existing
    content becomes the body unchanged.
    """
    text = path.read_text()
    try:
        before_yaml, yaml_text, after_yaml = split_frontmatter_md(text)
    except ValueError:
        body = text.lstrip("\n")
        before_yaml, yaml_text = "---\n", ""
        after_yaml = "---\n\n" + body if body else "---\n"

    ry = _rt_yaml()
    data = ry.load(yaml_text)  # type: ignore[reportUnknownMemberType]
    if data is None:
        data = CommentedMap()

    for key in removals or []:
        if key in data:
            del data[key]

    for key, value in updates.items():
        data[key] = value

    for key, value in appends or []:
        current: Any = data.get(key)  # type: ignore[reportUnknownMemberType]
        if current is None:
            data[key] = [value]
            continue
        if not isinstance(current, list):
            raise ValueError(f"cannot append to scalar key {key!r} in {path}")
        if value not in current:  # type: ignore[reportUnknownMemberType]
            current.append(value)  # type: ignore[reportUnknownMemberType]

    stream = StringIO()
    ry.dump(data, stream)  # type: ignore[reportUnknownMemberType]
    new_yaml = stream.getvalue()

    path.write_text(before_yaml + new_yaml + after_yaml)
