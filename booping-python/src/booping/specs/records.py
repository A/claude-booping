from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter
from booping.specs.tiers import Tier

_FILENAME_RE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
_REF_RE = re.compile(r"^(?:([A-Za-z0-9][A-Za-z0-9._-]*):)?([a-z][a-z0-9_-]*)/(\d{4})$")


class Ref(BaseModel):
    namespace: str | None
    type: str
    number: int


class Record(BaseModel):
    type: str
    # None when the filename breaks the `NNNN-slug.md` shape; check reports it.
    number: int | None
    slug: str | None
    path: Path
    frontmatter: dict[str, Any]
    body: str
    frontmatter_error: str | None = None
    frontmatter_error_line: int = 1


def parse_filename(name: str) -> tuple[int, str] | None:
    match = _FILENAME_RE.match(name)
    if match is None:
        return None
    return int(match.group(1)), match.group(2)


def parse_ref(text: str) -> Ref | None:
    """`[{namespace}:]{type}/{NNNN}` — the number is exactly four digits."""
    match = _REF_RE.match(text)
    if match is None:
        return None
    return Ref(namespace=match.group(1), type=match.group(2), number=int(match.group(3)))


def _body_after_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    return text[end + 3 :].lstrip("\n")


def _frontmatter_error(exc: Exception) -> tuple[str, int]:
    """One-line message and file line. parse_frontmatter hands YAML the text right after
    the opening `---`, so mark line 0 is file line 1, shifted three columns."""
    if isinstance(exc, yaml.MarkedYAMLError) and exc.problem_mark is not None and exc.problem:
        mark = exc.problem_mark
        line = mark.line + 1
        column = mark.column + 1 + (3 if mark.line == 0 else 0)
        return f"{exc.problem}, line {line}, column {column}", line
    return str(exc).splitlines()[0], 1


def load_record(path: Path, type_: str) -> Record:
    parsed = parse_filename(path.name)
    number, slug = parsed if parsed is not None else (None, None)
    try:
        frontmatter, body = parse_frontmatter(path)
        error, error_line = None, 1
    except (yaml.YAMLError, ValueError) as exc:
        frontmatter, body = {}, _body_after_frontmatter(path.read_text())
        error, error_line = _frontmatter_error(exc)
    return Record(
        type=type_,
        number=number,
        slug=slug,
        path=path,
        frontmatter=frontmatter,
        body=body,
        frontmatter_error=error,
        frontmatter_error_line=error_line,
    )


def load_tier(tier: Tier, types: list[str]) -> list[Record]:
    """Every `*.md` one directory below the tier root, known types first in `types`
    order, then unknown directories by name — they still load so check can report them.
    Files at the root itself (its README.md) are not records."""
    if not tier.root.is_dir():
        return []
    dirs = [d for d in tier.root.iterdir() if d.is_dir()]
    order = {name: index for index, name in enumerate(types)}
    dirs.sort(key=lambda d: (order.get(d.name, len(order)), d.name))
    return [load_record(p, d.name) for d in dirs for p in sorted(d.glob("*.md"))]
