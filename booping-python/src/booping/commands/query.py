"""`booping query` — run a frontmatter query and emit rows in one of four formats.

A thin shell over :mod:`booping.query`: argparse surface, output formatting,
exit-code mapping. A spec is addressed by dotted config path (`--config`) or
given inline (`--glob`); inline `--where` / `--sort` / `--columns` narrow a
resolved spec by deep-merging over it.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NoReturn

import yaml

from booping.context import Context
from booping.query import (
    QueryError,
    QuerySpec,
    Row,
    as_dict,
    as_table,
    build_spec,
    resolve_spec,
    run,
)

OUTPUTS = ("table", "json", "yaml", "paths")

_IN_SUFFIX = ":in"
_NE_SUFFIX = "!"


class _ValueFriendlyParser(argparse.ArgumentParser):
    """Parser that reads a single-dash token as a value, not an option.

    `--sort -created` is the documented descending form; argparse would otherwise
    classify `-created` as an unknown option and leave `--sort` starving.
    """

    def _parse_optional(self, arg_string: str) -> Any:
        if (
            arg_string.startswith("-")
            and not arg_string.startswith("--")
            and arg_string not in self._option_string_actions
        ):
            return None
        return super()._parse_optional(arg_string)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    previous = subparsers._parser_class  # pyright: ignore[reportPrivateUsage]
    subparsers._parser_class = _ValueFriendlyParser  # pyright: ignore[reportPrivateUsage]
    try:
        p = subparsers.add_parser(
            "query",
            help="Query markdown files by frontmatter and print the matching rows",
        )
    finally:
        subparsers._parser_class = previous  # pyright: ignore[reportPrivateUsage]
    p.add_argument(
        "--config",
        dest="config_path",
        default=None,
        metavar="DOTTED.PATH",
        help=(
            "Dotted path into the merged config whose value is the query spec;"
            " mutually exclusive with --glob"
        ),
    )
    p.add_argument(
        "--glob",
        action="append",
        dest="globs",
        default=None,
        metavar="PATTERN",
        help=(
            "Vault-relative glob to match; repeatable and ordered — the first"
            " glob claiming a slug wins"
        ),
    )
    p.add_argument(
        "--where",
        action="append",
        dest="where",
        default=None,
        metavar="K=V",
        help="Filter clause: k=v, k!=v, or k:in=a,b; repeatable, all clauses apply",
    )
    p.add_argument(
        "--sort",
        default=None,
        metavar="FIELD",
        help="Sort by this frontmatter field; '-' prefix for descending",
    )
    p.add_argument(
        "--columns",
        default=None,
        metavar="A,B",
        help="Comma-separated projection; declared order is preserved",
    )
    p.add_argument(
        "--output",
        default="table",
        metavar="FORMAT",
        help=f"Output format: {', '.join(OUTPUTS)} (default: table)",
    )
    p.add_argument(
        "--project",
        default=None,
        metavar="PATH",
        help="Resolve context against this vault instead of the attached project",
    )
    p.set_defaults(func=_run)


def _fail(message: str, code: int = 1) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def parse_where(pairs: Sequence[str]) -> dict[str, Any]:
    """`k=v` / `k!=v` / `k:in=a,b` → clause keys `k` / `k!` / `k:in`.

    Raises ValueError carrying the offending pair.
    """
    where: dict[str, Any] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ValueError(pair)
        if key.endswith(_IN_SUFFIX):
            field = key[: -len(_IN_SUFFIX)]
            if not field:
                raise ValueError(pair)
            where[key] = [item.strip() for item in value.split(",")]
            continue
        field = key[: -len(_NE_SUFFIX)] if key.endswith(_NE_SUFFIX) else key
        if not field:
            raise ValueError(pair)
        where[key] = value
    return where


def _inline_spec(args: argparse.Namespace) -> dict[str, Any]:
    inline: dict[str, Any] = {}
    if args.globs:
        inline["glob"] = list(args.globs)
    try:
        where = parse_where(args.where or [])
    except ValueError as exc:
        _fail(f"malformed --where clause (expected k=v, k!=v or k:in=a,b): {exc}")
    if where:
        inline["where"] = where
    if args.sort is not None:
        inline["sort"] = args.sort
    if args.columns is not None:
        inline["columns"] = [col.strip() for col in args.columns.split(",") if col.strip()]
    return inline


def _resolve_spec(config: dict[str, Any], dotted: str) -> dict[str, Any]:
    try:
        return resolve_spec(config, dotted)
    except QueryError as exc:
        _fail(str(exc))


def _format(rows: list[Row], spec: QuerySpec, output: str) -> str:
    dicts = [as_dict(row) for row in rows]
    if output == "table":
        return as_table(dicts, spec.columns)
    if output == "json":
        return json.dumps(dicts, indent=2, default=str, ensure_ascii=False) + "\n"
    if output == "yaml":
        return yaml.dump(dicts, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return "".join(f"{row.get('path', '')}\n" for row in dicts)


def _run(args: argparse.Namespace) -> None:
    output: str = args.output
    if output not in OUTPUTS:
        _fail(f"unknown --output format: {output} (expected {', '.join(OUTPUTS)})")

    config_path: str | None = args.config_path
    if config_path is not None and args.globs:
        _fail("--config and --glob are mutually exclusive")
    if config_path is None and not args.globs:
        _fail("one of --config or --glob is required")

    inline = _inline_spec(args)

    project_str: str | None = args.project
    vault_override = (
        Path(project_str).expanduser().resolve() if project_str is not None else None
    )
    ctx = Context.assemble(vault_override=vault_override)

    base = _resolve_spec(ctx.config, config_path) if config_path is not None else {}
    try:
        spec = build_spec(ctx.config, base, inline)
    except Exception as exc:  # noqa: BLE001 — a malformed spec is a user error
        source = f"config path {config_path}" if config_path else "inline flags"
        _fail(f"invalid query spec from {source}: {exc}")

    vault = vault_override
    if vault is None and ctx.project is not None:
        vault = ctx.project.directory
    if vault is None:
        _fail("no vault resolved — run inside a booping project or pass --project", code=2)
    if not vault.is_dir():
        _fail(f"vault is not a readable directory: {vault}", code=2)

    try:
        rows = run(spec, vault)
    except OSError as exc:
        _fail(f"failed to read vault {vault}: {exc}", code=2)

    sys.stdout.write(_format(rows, spec, output))
