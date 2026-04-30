from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


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
