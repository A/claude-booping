from __future__ import annotations

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


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Split markdown frontmatter from body; frontmatter is parsed YAML."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}, text
    end = text.index("---", 3)
    fm = safe_load_str(text[3:end])
    body = text[end + 3 :].lstrip("\n")
    return fm, body


def parse_frontmatter_only(path: Path) -> dict[str, Any]:
    """Parse only the frontmatter section; ignore body."""
    fm, _ = parse_frontmatter(path)
    return fm


def split_frontmatter_md(text: str) -> tuple[str, str, str]:
    """Split markdown with frontmatter into (before_yaml, yaml_text, after_yaml).

    * ``before_yaml``: opening ``---\\n`` delimiter.
    * ``yaml_text``: YAML content between the two delimiters (may be empty).
    * ``after_yaml``: closing ``---`` delimiter and body text.

    The original text can be reconstructed as ``before_yaml + yaml_text + after_yaml``.

    Raises :class:`ValueError` if no frontmatter delimiters are found.
    """
    if not text.startswith("---"):
        raise ValueError("No frontmatter opening delimiter")
    if text[3:4] != "\n":
        raise ValueError("Opening --- must be followed by newline")

    close_pos = text.find("---", 3)
    if close_pos == -1:
        raise ValueError("No frontmatter closing delimiter")

    before_yaml = text[:4]  # "---\n"
    yaml_text = text[4:close_pos]
    after_yaml = text[close_pos:]  # "---\n<body>"

    return before_yaml, yaml_text, after_yaml


def update_frontmatter(
    path: Path,
    updates: dict[str, object],
    removals: list[str] | None = None,
) -> None:
    """Update frontmatter keys in a markdown file using ruamel.yaml round-trip mode.

    Preserves comments, key order, and body text.  Only the extracted YAML
    block is passed to the parser — the body is never parsed as YAML.

    ``removals`` lists keys to drop from the frontmatter; missing keys are
    ignored.  Removals are applied before updates so a key may be removed and
    re-added in one call.

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

    stream = StringIO()
    ry.dump(data, stream)  # type: ignore[reportUnknownMemberType]
    new_yaml = stream.getvalue()

    path.write_text(before_yaml + new_yaml + after_yaml)
