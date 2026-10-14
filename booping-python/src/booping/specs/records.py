from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from booping.context._yaml import safe_load_str
from booping.specs.tiers import Tier

_FILENAME_RE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
_REF_RE = re.compile(r"^(?:([A-Za-z0-9][A-Za-z0-9._-]*):)?([a-z][a-z0-9_-]*)/(\d{4})$")
# Delimiters are whole lines, so a `---` inside a value does not end the block.
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)^---[ \t]*$\n?", re.S | re.M)


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


class _UnclosedFrontmatterError(ValueError):
    pass


def _split_frontmatter(text: str) -> tuple[str | None, str]:
    """YAML text between the delimiter lines (None without frontmatter) and the body."""
    if not text.startswith("---"):
        return None, text
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        raise _UnclosedFrontmatterError
    return match.group(1), text[match.end() :].lstrip("\n")


def _frontmatter_error(exc: yaml.YAMLError) -> tuple[str, int]:
    """One-line message and file line. YAML sees the text after the opening delimiter
    line, so its mark line 0 is file line 2."""
    if isinstance(exc, yaml.MarkedYAMLError) and exc.problem_mark is not None and exc.problem:
        mark = exc.problem_mark
        line = mark.line + 2
        return f"{exc.problem}, line {line}, column {mark.column + 1}", line
    return str(exc).splitlines()[0], 1


def load_record(path: Path, type_: str) -> Record:
    parsed = parse_filename(path.name)
    number, slug = parsed if parsed is not None else (None, None)
    text = path.read_text()
    frontmatter: dict[str, Any] = {}
    error, error_line = None, 1
    try:
        yaml_text, body = _split_frontmatter(text)
    except _UnclosedFrontmatterError:
        yaml_text, body = None, text
        error = "frontmatter block is not closed"
    if yaml_text is not None:
        try:
            frontmatter = safe_load_str(yaml_text)
        except yaml.YAMLError as exc:
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
