"""Frontmatter query engine — a spec into ordered rows over a vault.

A spec names an ordered list of globs; the first glob to claim a slug wins and
later claims on the same slug are skipped, so plan-shape precedence is list
order rather than hidden engine logic.  Results are sorted by slug before any
user sort applies, because ``Path.glob`` documents no ordering.

Pure logic — no argparse, no Jinja, no I/O beyond reading the matched files.
"""
from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel

from booping.context._yaml import parse_frontmatter
from booping.utils import PathError, deep_merge, resolve_path

_GLOB_MAGIC = frozenset("*?[")
_NE_SUFFIX = "!"
_IN_SUFFIX = ":in"

DEFAULT_GLOB_PATH = "plans.glob"


class QueryError(Exception):
    """A spec could not be resolved or built."""


class Row:
    """Attribute-accessible view over one file's frontmatter.

    Jinja resolves ``foo.bar`` as ``getattr`` before ``__getitem__``, so a plain
    dict whose frontmatter carries ``items`` / ``keys`` / ``get`` renders a bound
    method.  A row therefore carries no public methods at all: every name that is
    not a frontmatter key raises ``AttributeError``, which Jinja turns into the
    configured undefined.
    """

    __slots__ = ("__data__",)

    __data__: dict[str, Any]

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.__data__ = {key: _wrap(value) for key, value in data.items()}

    def __getattr__(self, name: str) -> Any:
        try:
            return self.__data__[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(self, key: str) -> Any:
        return self.__data__[key]

    def __contains__(self, key: str) -> bool:
        return key in self.__data__

    def __repr__(self) -> str:
        return f"Row({as_dict(self)!r})"


def _wrap(value: Any) -> Any:
    if isinstance(value, Mapping):
        return Row(value)  # pyright: ignore[reportUnknownArgumentType]
    if isinstance(value, list):
        return [_wrap(item) for item in value]  # pyright: ignore[reportUnknownVariableType]
    return value


def as_dict(row: Row) -> dict[str, Any]:
    """The row's underlying mapping, unwrapped recursively — for serialization."""
    return {key: _unwrap(value) for key, value in row.__data__.items()}


def _unwrap(value: Any) -> Any:
    if isinstance(value, Row):
        return as_dict(value)
    if isinstance(value, list):
        return [_unwrap(item) for item in value]  # pyright: ignore[reportUnknownVariableType]
    return value


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


def matches(row: Mapping[str, Any], where: Mapping[str, Any]) -> bool:
    """Whether *row* satisfies every clause of *where*.

    A clause key carries its operator as a suffix: ``k!`` is ``!=``, ``k:in`` is
    membership, a bare ``k`` is equality.  A row missing the field fails every
    operator.
    """
    for clause, expected in where.items():
        if clause.endswith(_IN_SUFFIX):
            field, op = clause[: -len(_IN_SUFFIX)], _IN_SUFFIX
        elif clause.endswith(_NE_SUFFIX):
            field, op = clause[: -len(_NE_SUFFIX)], _NE_SUFFIX
        else:
            field, op = clause, ""
        if field not in row:
            return False
        value = row[field]
        if op == _IN_SUFFIX:
            options = cast(list[Any], expected) if isinstance(expected, list) else [expected]
            if not any(_eq(value, option) for option in options):
                return False
        elif op == _NE_SUFFIX:
            if _eq(value, expected):
                return False
        elif not _eq(value, expected):
            return False
    return True


def _eq(value: Any, expected: Any) -> bool:
    # Flag-supplied values are always strings; frontmatter values may be dates or numbers.
    return bool(value == expected) or str(value) == str(expected)


def order(rows: Sequence[Mapping[str, Any]], sort: str) -> list[Mapping[str, Any]]:
    """Sort *rows* by the field *sort* names, ``-`` prefixed for descending.

    Rows without a value for the field keep their incoming order at the end,
    whichever direction is asked for.
    """
    descending = sort.startswith("-")
    field = sort[1:] if descending else sort
    present = [row for row in rows if row.get(field) is not None]
    missing = [row for row in rows if row.get(field) is None]
    try:
        ordered = sorted(present, key=lambda row: row[field], reverse=descending)
    except TypeError:  # mixed value types have no natural order
        ordered = sorted(present, key=lambda row: str(row[field]), reverse=descending)
    return ordered + missing


def project(row: Mapping[str, Any], columns: Sequence[str]) -> dict[str, Any]:
    """Narrow *row* to *columns* in declared order, keeping ``path`` and ``slug``."""
    keys = list(columns) + [key for key in ("path", "slug") if key not in columns]
    return {key: row[key] for key in keys if key in row}


def default_glob(config: Mapping[str, Any]) -> list[str]:
    """The `plans.glob` fallback a spec omitting `glob` inherits."""
    try:
        value: Any = resolve_path(dict(config), DEFAULT_GLOB_PATH)
    except PathError:
        return []
    if not isinstance(value, list):
        return []
    return [str(item) for item in cast("list[Any]", value)]


def build_spec(
    config: Mapping[str, Any],
    base: Mapping[str, Any],
    overrides: Mapping[str, Any] | None = None,
) -> QuerySpec:
    """Deep-merge *overrides* over *base* (neither is mutated) into a spec.

    A merged spec without a `glob` inherits the `plans.glob` default.
    """
    merged = deep_merge(dict(base), dict(overrides or {}))
    if not merged.get("glob"):
        merged["glob"] = default_glob(config)
    return QuerySpec(**merged)


def resolve_spec(config: Mapping[str, Any], dotted: str) -> dict[str, Any]:
    """The spec mapping at *dotted* in the merged config.

    Raises :class:`QueryError` naming the path when it does not resolve or does
    not carry a mapping.
    """
    try:
        value: Any = resolve_path(dict(config), dotted)
    except PathError as exc:
        raise QueryError(f"no query spec at config path: {dotted}") from exc
    if not isinstance(value, Mapping):
        raise QueryError(
            f"config path {dotted} is a {type(value).__name__}, not a query spec mapping"
        )
    return dict(cast("Mapping[str, Any]", value))


def table_columns(
    rows: Sequence[Mapping[str, Any]], columns: Sequence[str] | None = None
) -> list[str]:
    """Column order of a table over *rows* — their key union, or *columns* when empty."""
    seen: dict[str, None] = {}
    for row in rows:
        for key in row:
            seen[key] = None
    if seen:
        return list(seen)
    if columns:
        return list(columns) + [key for key in ("path", "slug") if key not in columns]
    return []


def cell(value: Any) -> str:
    """One table cell: `|` escaped, newlines collapsed, `None` empty."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        text = ", ".join(cell(item) for item in value)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
    else:
        text = str(value)
    return (
        text.replace("|", "\\|")
        .replace("\r\n", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def as_table(
    rows: Sequence[Row | Mapping[str, Any]], columns: Sequence[str] | None = None
) -> str:
    """A GFM table over *rows*, narrowed to *columns* when given.

    The one table writer — `booping query --output table` and the `as_table`
    filter both call it, so both emit the same bytes for the same rows.
    """
    dicts = [as_dict(row) if isinstance(row, Row) else dict(row) for row in rows]
    if columns is not None:
        dicts = [project(row, columns) for row in dicts]
    header = table_columns(dicts, columns)
    if not header:
        return ""
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines += [
        "| " + " | ".join(cell(row.get(col)) for col in header) + " |" for row in dicts
    ]
    return "\n".join(lines) + "\n"


def run(spec: QuerySpec, vault: Path) -> list[Row]:
    """Run *spec* against *vault*: discover, filter, sort, project, wrap."""
    rows: list[Mapping[str, Any]] = []
    for slug, path in discover(vault, spec.glob):
        row = read_row(vault, slug, path)
        if row is not None and matches(row, spec.where):
            rows.append(row)
    if spec.sort:
        rows = order(rows, spec.sort)
    if spec.columns is not None:
        rows = [project(row, spec.columns) for row in rows]
    return [Row(row) for row in rows]
