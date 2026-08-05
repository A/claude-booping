"""Frontmatter query engine — a spec into ordered rows over a vault.

A spec names an ordered list of globs; the first glob to claim a slug wins and
later claims on the same slug are skipped, so plan-shape precedence is list
order rather than hidden engine logic.  Results are sorted by slug before any
user sort applies, because ``Path.glob`` documents no ordering.

Pure logic — no argparse, no Jinja, no I/O beyond reading the matched files.
"""
from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter

_GLOB_MAGIC = frozenset("*?[")


class QuerySpec(BaseModel):
    """A declared query: what to match, narrow, order and project."""

    glob: list[str] = []
    where: dict[str, Any] = {}
    sort: str | None = None
    columns: list[str] | None = None


def slug_for(pattern: str, rel_path: Path) -> str:
    """Slug identity of a match of *pattern*.

    A pattern ending in a literal filename below a wildcard segment
    (``plans/*/index.md``) addresses an index of a directory, so the directory
    carries the identity; anything else is identified by the file's own stem.
    """
    segments = pattern.split("/")
    if len(segments) > 1 and not _GLOB_MAGIC & set(segments[-1]):
        return rel_path.parent.name
    return rel_path.stem


def discover(vault: Path, globs: Sequence[str]) -> list[tuple[str, Path]]:
    """Return ``(slug, path)`` pairs for *globs*, de-duplicated by slug and slug-sorted."""
    claimed: dict[str, Path] = {}
    for pattern in globs:
        for path in sorted(vault.glob(pattern)):
            if not path.is_file():
                continue
            slug = slug_for(pattern, path.relative_to(vault))
            if slug in claimed:
                continue
            claimed[slug] = path
    return sorted(claimed.items())


def read_row(vault: Path, slug: str, path: Path) -> dict[str, Any] | None:
    """Read one file's frontmatter into a row, or ``None`` if it does not parse."""
    try:
        frontmatter, _ = parse_frontmatter(path)
    except Exception as exc:  # noqa: BLE001 — one bad file must not fail the query
        print(f"warning: skipping {path} — unparseable frontmatter ({exc})", file=sys.stderr)
        return None
    return {**frontmatter, "path": path.relative_to(vault).as_posix(), "slug": slug}


def run(spec: QuerySpec, vault: Path) -> list[dict[str, Any]]:
    """Run *spec* against *vault* and return its rows in slug order."""
    rows: list[dict[str, Any]] = []
    for slug, path in discover(vault, spec.glob):
        row = read_row(vault, slug, path)
        if row is not None:
            rows.append(row)
    return rows
