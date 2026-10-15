from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from booping import defaults, logger
from booping.context import Context
from booping.defaults import DefaultsError

# Checked by hand rather than argparse `required=True`: a missing flag must be one
# `error: …` line at exit 1, not argparse's usage block at exit 2.
_ADD_REQUIRED = ("target", "step", "asked", "default")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "defaults",
        help="Log what a run decided without the user to defaults.md beside its artefact",
    )
    verbs = p.add_subparsers(dest="defaults_verb", metavar="<verb>", required=True)

    add = verbs.add_parser(
        "add",
        help="Append the next D{n} entry to the target's defaults.md and print {sidecar}#D{n}",
    )
    add.add_argument(
        "--target",
        default=None,
        metavar="PATH",
        help="Vault-relative run artefact (plan index.md or review record); must exist",
    )
    add.add_argument(
        "--step", default=None, metavar="TEXT", help="Where it happened: {playbook}/{step}"
    )
    add.add_argument(
        "--asked", default=None, metavar="TEXT", help="The gate or question settled; non-empty"
    )
    add.add_argument("--default", default=None, metavar="TEXT", help="What was decided; non-empty")
    add.add_argument(
        "--why", default=None, metavar="TEXT", help="Why that default (default: not stated)"
    )
    add.set_defaults(func=_run_add)


def _fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def _run_add(args: argparse.Namespace) -> None:
    for name in _ADD_REQUIRED:
        if getattr(args, name) is None:
            _fail(f"--{name} is required")
    ctx = Context.assemble()
    try:
        added = defaults.add(
            ctx,
            target=args.target,
            step=args.step,
            asked=args.asked,
            default=args.default,
            why=args.why,
        )
    except DefaultsError as exc:
        _fail(str(exc))
    ref = f"{added.sidecar}#D{added.number}"
    logger.log(vault=ctx.vault, subcommand="defaults", message=f"add {ref}")
    print(ref)
