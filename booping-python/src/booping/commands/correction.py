from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from booping import correction, logger
from booping.context import Context
from booping.correction import CorrectionError
from booping.session_stats import default_projects_root

# Checked by hand rather than argparse `required=True`: a missing flag must be one
# `error: …` line at exit 1, not argparse's usage block at exit 2.
_ADD_REQUIRED = ("target", "step", "did", "said")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "correction",
        help="Log the user's corrections of a run to corrections.md beside its artefact",
    )
    verbs = p.add_subparsers(dest="correction_verb", metavar="<verb>", required=True)

    add = verbs.add_parser(
        "add",
        help="Append the next R{n} entry to the target's corrections.md and print {sidecar}#R{n}",
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
    add.add_argument("--did", default=None, metavar="TEXT", help="What the model did")
    add.add_argument(
        "--said", default=None, metavar="TEXT", help="The user's words, verbatim; non-empty"
    )
    add.add_argument(
        "--why", default=None, metavar="TEXT", help="The reason the user gave (default: not stated)"
    )
    add.add_argument(
        "--record",
        default=None,
        metavar="REF",
        help="Spec record the correction names, [namespace:]type/NNNN; also files an open"
        " item (source: correction) and prints its path on a second line",
    )
    add.add_argument(
        "--session",
        default=None,
        metavar="ID",
        help="Session id whose transcript holds --said (default: $CLAUDE_CODE_SESSION_ID)",
    )
    add.set_defaults(func=_run_add)

    lst = verbs.add_parser(
        "list",
        help="Print every correction logged against a plan: its own corrections.md, then"
        " its code reviews'",
    )
    lst.add_argument(
        "--plan",
        required=True,
        metavar="PATH",
        help="The plan's index.md, vault-relative (plans/{dir}/index.md); must exist",
    )
    lst.set_defaults(func=_run_list)


def _fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def _run_add(args: argparse.Namespace) -> None:
    for name in _ADD_REQUIRED:
        if getattr(args, name) is None:
            _fail(f"--{name} is required")
    ctx = Context.assemble()
    try:
        added = correction.add(
            ctx,
            target=args.target,
            step=args.step,
            did=args.did,
            said=args.said,
            why=args.why,
            record=args.record,
            session=correction.resolve_session(args.session),
            projects_root=default_projects_root(),
        )
    except CorrectionError as exc:
        _fail(str(exc))
    for warning in added.warnings:
        print(warning, file=sys.stderr)
    ref = f"{added.sidecar}#R{added.number}"
    logger.log(vault=ctx.vault, subcommand="correction", message=f"add {ref}")
    print(ref)
    if added.item is not None:
        print(added.item)


def _run_list(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    try:
        text = correction.feed(ctx, args.plan)
    except CorrectionError as exc:
        _fail(str(exc))
    logger.log(vault=ctx.vault, subcommand="correction", message=f"list {args.plan}")
    print(text, end="")
