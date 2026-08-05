from __future__ import annotations

import argparse
import sys

import yaml

from booping.context import Context
from booping.utils import PathError, resolve_path


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "config-get",
        help="Print a resolved (merged) config value by dotted key path",
    )
    p.add_argument(
        "key",
        help=(
            "Dot-separated key path into the merged config"
            " (e.g. core.sprint.default_threshold_sp)"
        ),
    )
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    try:
        ctx = Context.assemble()
    except Exception as exc:  # noqa: BLE001 — surface any loader failure as internal error
        print(f"error: could not load config: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        value: object = resolve_path(ctx.config, args.key)
    except PathError:
        print(f"error: key not found: {args.key}", file=sys.stderr)
        sys.exit(1)

    if isinstance(value, (dict, list)):
        sys.stdout.write(yaml.dump(value, allow_unicode=True, sort_keys=False))
    else:
        sys.stdout.write(f"{value}\n")
