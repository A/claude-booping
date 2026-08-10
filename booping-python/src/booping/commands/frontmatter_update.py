from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, TemplateError
from ruamel.yaml import YAML as RuamelYAML
from ruamel.yaml.error import YAMLError as RuamelYAMLError
from ruamel.yaml.scalarstring import SingleQuotedScalarString

from booping import logger
from booping.context import Context
from booping.context._yaml import update_frontmatter
from booping.macros import MacroError, make_macro
from booping.utils import diff_report

_NULL_FORMS = {"null", "Null", "NULL", "~"}


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "frontmatter-update",
        help="Update frontmatter keys in a plan file, rendering Jinja macro calls",
    )
    p.add_argument("plan", type=Path, help="Path to the plan markdown file")
    p.add_argument(
        "pairs",
        nargs="*",
        metavar="key=val",
        help=(
            "Frontmatter key=value pairs; a value is rendered as Jinja with the `macro` "
            # argparse %-expands help strings, so literal percent signs are doubled.
            "global (e.g. \"{{ macro('core.macros.date', '+%%Y-%%m-%%d %%H:%%M') }}\")"
        ),
    )
    p.add_argument(
        "--remove",
        dest="removals",
        action="append",
        default=[],
        metavar="key",
        help="Frontmatter key to remove (repeatable); applied before key=value sets",
    )
    p.add_argument(
        "--append",
        dest="appends",
        action="append",
        default=[],
        metavar="key=val",
        help=(
            "Append a value to a frontmatter list (repeatable); a null or absent key "
            "becomes a one-element list, an already-present value is a no-op, an "
            "existing scalar is an error"
        ),
    )
    p.set_defaults(func=_run)


def interpolate(
    value: str,
    repo_dir: Path | None = None,
    config: Mapping[str, Any] | None = None,
    vault_dir: Path | None = None,
) -> str:
    """Render a hook value as Jinja whose only global is `macro`.

    A value carrying no Jinja passes through untouched.
    """
    if "{{" not in value and "{%" not in value:
        return value
    env = Environment()  # noqa: S701 — frontmatter values, not HTML
    globals_: dict[str, Any] = env.globals  # type: ignore[assignment]
    globals_["macro"] = make_macro(
        dict(config) if config else {}, repo_dir=repo_dir, vault_dir=vault_dir
    )
    try:
        return env.from_string(value).render()
    except MacroError as exc:
        print(f"error: value {value!r}: {exc}", file=sys.stderr)
        sys.exit(2)
    except TemplateError as exc:
        print(f"error: value {value!r}: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)


def coerce_scalar(value: str) -> object:
    """Return *value* as the Python type its plain YAML form loads as.

    An integer, float, boolean or null form becomes that type, so the emitter
    writes it unquoted.  Everything else stays a string; a string whose plain
    form would reload as another type under the YAML 1.1 resolver the readers
    use is marked single-quoted, so it reloads as the string it was written as.
    """
    if not value.strip():
        return value

    try:
        loaded: object = RuamelYAML(typ="rt").load(value)  # type: ignore[reportUnknownMemberType]
    except RuamelYAMLError:
        loaded = value

    if loaded is None:
        # An anchor or an empty tag also loads as None; only the null spellings
        # are a real null.
        return None if value.strip() in _NULL_FORMS else _quote_if_ambiguous(value)
    if isinstance(loaded, bool | int | float):
        return loaded
    return _quote_if_ambiguous(value)


def _quote_if_ambiguous(value: str) -> str:
    try:
        reloaded: object = yaml.safe_load(value)
    except yaml.YAMLError:
        return value
    if isinstance(reloaded, str) and reloaded == value:
        return value
    return SingleQuotedScalarString(value)


def parse_pairs(pairs: list[str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            print(f"error: malformed key=value pair: {pair!r}", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        if not key:
            print(f"error: empty key in pair: {pair!r}", file=sys.stderr)
            sys.exit(1)
        updates[key] = value
    return updates


def _run(args: argparse.Namespace) -> None:
    plan_path: Path = args.plan
    if not plan_path.is_file():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    removals: list[str] = list(getattr(args, "removals", None) or [])
    updates = parse_pairs(args.pairs)
    appends = parse_pairs(list(getattr(args, "appends", None) or []))

    if not updates and not removals and not appends:
        print(
            "error: nothing to do: provide key=value pairs, --append and/or --remove",
            file=sys.stderr,
        )
        sys.exit(1)

    ctx = Context.assemble()
    project = ctx.project
    repo_dir = project.repo_directory if project is not None else None
    vault_dir = project.directory if project is not None else None

    resolved: dict[str, object] = {}
    # The summary echoes the interpolated text, not the coerced value, so the
    # stderr line reads the same as before the typing rule.
    summary_values: dict[str, str] = {}
    for key, value in updates.items():
        rendered = interpolate(value, repo_dir, ctx.config, vault_dir)
        summary_values[key] = rendered
        resolved[key] = coerce_scalar(rendered)

    resolved_appends: dict[str, object] = {}
    for key, value in appends.items():
        resolved_appends[key] = interpolate(value, repo_dir, ctx.config, vault_dir)

    previous = plan_path.read_text()

    try:
        update_frontmatter(plan_path, resolved, removals=removals, appends=resolved_appends)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    report = diff_report(plan_path, previous, plan_path.read_text())
    if report:
        print(report)

    vault = project.directory if project is not None else None
    changed = [f"-{k}" for k in removals] + list(resolved.keys()) + list(resolved_appends.keys())
    logger.log(
        vault=vault, subcommand="frontmatter-update", message=f"{plan_path} {' '.join(changed)}"
    )

    parts = (
        [f"-{k}" for k in removals]
        + [f"{k}={v}" for k, v in summary_values.items()]
        + [f"{k}+={v}" for k, v in resolved_appends.items()]
    )
    print(f"updated {plan_path}: {', '.join(parts)}", file=sys.stderr)