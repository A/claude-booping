from __future__ import annotations

import argparse
import sys
from typing import Any

from booping import logger
from booping.commands.specs import (
    _add_tier,  # pyright: ignore[reportPrivateUsage]
    _assemble,  # pyright: ignore[reportPrivateUsage]
    _fail,  # pyright: ignore[reportPrivateUsage]
    _format_dir,  # pyright: ignore[reportPrivateUsage]
    _known_types,  # pyright: ignore[reportPrivateUsage]
    _resolve,  # pyright: ignore[reportPrivateUsage]
    _select_tier,  # pyright: ignore[reportPrivateUsage]
)
from booping.context import Context
from booping.specs import open_items
from booping.specs.check import CheckError, check_tier
from booping.specs.open_items import OpenItemError
from booping.specs.records import load_tier


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "items",
        help="File, list and move items — user requests and specs-to-code gaps under"
        " {vault}/open-items",
    )
    verbs = p.add_subparsers(dest="items_verb", metavar="<verb>", required=True)

    add = verbs.add_parser(
        "add",
        help="File the next open item and print its vault-relative path",
    )
    add.add_argument("--title", default=None, metavar="TEXT", help="Item title")
    add.add_argument(
        "--direction",
        default=None,
        metavar="D",
        help=f"One of: {', '.join(open_items.DIRECTIONS)} (default with --record adr/NNNN:"
        " spec-to-code)",
    )
    add.add_argument(
        "--record",
        default=None,
        metavar="REF",
        help="Record the item is about, e.g. adr/0025#consequences; adr/NNNN without"
        " --title takes the title from the ADR's Confirmation: line",
    )
    add.add_argument(
        "--source",
        default=None,
        metavar="S",
        help=f"One of: {', '.join(open_items.SOURCES)} (default: adr with --record adr/NNNN,"
        " manual with --direction, otherwise request)",
    )
    add.add_argument(
        "--text", default=None, metavar="TEXT", help="The item body, verbatim; - reads stdin"
    )
    add.set_defaults(func=_run_add)

    scan = verbs.add_parser(
        "scan",
        help="File one clarify item per [clarify]/[unknown] mark and per `specs check`"
        " finding in a tier, skipping any already tracked",
    )
    _add_tier(scan, "Tier to scan (default: project)")
    scan.set_defaults(func=_run_scan)

    lst = verbs.add_parser(
        "list",
        help="Print the open-items index as a markdown table (open and planned items)",
    )
    lst.add_argument("--all", action="store_true", help="Include closed items too")
    lst.set_defaults(func=_run_list)

    pln = verbs.add_parser("plan", help="Link open items to a plan and move them to planned")
    pln.add_argument("ids", nargs="+", metavar="ID", help="Open item id, e.g. OI-0001")
    pln.add_argument(
        "--plan",
        required=True,
        metavar="PATH",
        help="The plan's index.md, vault-relative (plans/{dir}/index.md); must exist",
    )
    pln.set_defaults(func=_run_plan)

    close = verbs.add_parser(
        "close",
        help="Close planned items as done (or open/planned ones as dropped with --dropped)",
    )
    close.add_argument("ids", nargs="*", metavar="ID", help="Open item id, e.g. OI-0001")
    close.add_argument(
        "--plan",
        default=None,
        metavar="PATH",
        help="Instead of ids: every planned item linked to this plan",
    )
    close.add_argument(
        "--dropped", action="store_true", help="Close as dropped (no work done); accepts open items"
    )
    close.add_argument("--reason", default=None, metavar="TEXT", help="Why the item closed")
    close.set_defaults(func=_run_close)

    reopen = verbs.add_parser("reopen", help="Return planned items to open, clearing their plan")
    reopen.add_argument("ids", nargs="*", metavar="ID", help="Open item id, e.g. OI-0001")
    reopen.add_argument(
        "--plan",
        default=None,
        metavar="PATH",
        help="Instead of ids: every planned item linked to this plan",
    )
    reopen.set_defaults(func=_run_reopen)


def _run_add(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    title: str | None = args.title
    direction: str | None = args.direction
    record: str | None = args.record
    source: str | None = args.source
    text: str | None = sys.stdin.buffer.read().decode("utf-8") if args.text == "-" else args.text
    try:
        open_items.require_vault(ctx)
        if record is not None and open_items.is_adr_ref(record):
            source = source or "adr"
            if source not in open_items.REQUEST_SOURCES:
                known = _known_types(ctx, root)
                tier = _select_tier(ctx, root, home_dir, "project")
                adr = open_items.find_adr(load_tier(tier, known), record)
                if title is None:
                    title = open_items.confirmation_title(adr)
                    if title is None:
                        raise OpenItemError(
                            f"{record} has no `Confirmation:` line under ## Consequences"
                        )
                direction = direction or "spec-to-code"
                record = f"{record}#consequences"
        if source is None:
            source = "manual" if direction is not None else "request"
        if source in open_items.REQUEST_SOURCES:
            if text is None:
                raise OpenItemError(f"--text is required for source {source}")
            if not text.strip():
                raise OpenItemError("--text is empty")
            if direction is not None:
                raise OpenItemError(f"--direction does not apply to source {source}")
            title = title or open_items.derived_title(text)
        else:
            if title is None:
                raise OpenItemError("--title is required unless --record names an ADR")
            if direction is None:
                raise OpenItemError("--direction is required unless --record names an ADR")
            open_items.check_choice("--direction", direction, open_items.DIRECTIONS)
        open_items.check_choice("--source", source, open_items.SOURCES)
        path = open_items.write_item(
            ctx, title=title, direction=direction, record=record, source=source, body=text
        )
    except OpenItemError as exc:
        _fail(str(exc))
    rel = open_items.vault_relative(ctx, path)
    logger.log(vault=ctx.vault, subcommand="items", message=f"add {rel}")
    print(rel)


def _run_scan(args: argparse.Namespace) -> None:
    ctx, root, home_dir = _assemble()
    try:
        open_items.require_vault(ctx)
    except OpenItemError as exc:
        _fail(str(exc))
    known = _known_types(ctx, root)
    tier = _select_tier(ctx, root, home_dir, args.tier)
    records = load_tier(tier, known)
    try:
        findings, _ = check_tier(tier, _format_dir(ctx, root), known, _resolve(ctx, root, home_dir))
    except CheckError as exc:
        _fail(str(exc), 2)
    candidates = open_items.mark_candidates(
        [r for r in records if r.type in known], tier.root
    ) + open_items.finding_candidates(findings, tier.root)
    try:
        created, skipped = open_items.scan(ctx, candidates)
    except OpenItemError as exc:
        _fail(str(exc))
    for path in created:
        print(open_items.vault_relative(ctx, path))
    logger.log(vault=ctx.vault, subcommand="items", message=f"scan --tier {args.tier}")
    print(f"{len(created)} created, {skipped} already tracked")


def _run_list(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    try:
        where: dict[str, Any] = (
            {} if args.all else {"status:in": open_items.open_statuses(open_items.machine(ctx))}
        )
        rows, columns = open_items.index_rows(ctx, where)
    except OpenItemError as exc:
        _fail(str(exc))
    logger.log(vault=ctx.vault, subcommand="items", message="list")
    print(open_items.index_table(rows, columns) if rows else "no open items")


def _selected(ctx: Context, ids: list[str], plan: str | None) -> list[str]:
    """The ids a close/reopen acts on: given outright, or every planned item of a plan."""
    if bool(ids) == (plan is not None):
        raise OpenItemError("pass item ids or --plan PATH, not both")
    if plan is None:
        return ids
    selected = open_items.planned_for(ctx, open_items.vault_path(ctx, plan))
    if not selected:
        print(f"no planned items for {plan}")
    return selected


def _run_move(verb: str, ids: list[str], plan: str | None, to: str, fields: dict[str, str]) -> None:
    ctx = _assemble()[0]
    try:
        for item_id in _selected(ctx, ids, plan):
            print("\n".join(open_items.move(ctx, item_id, to, fields)))
            logger.log(vault=ctx.vault, subcommand="items", message=f"{verb} {item_id}")
    except OpenItemError as exc:
        _fail(str(exc))


def _run_plan(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    try:
        plan = open_items.vault_path(ctx, args.plan)
        if not (open_items.require_vault(ctx) / plan).is_file():
            raise OpenItemError(f"plan not found: {plan}")
    except OpenItemError as exc:
        _fail(str(exc))
    _run_move("plan", args.ids, None, "planned", {"plan": plan})


def _run_close(args: argparse.Namespace) -> None:
    fields = {"reason": args.reason} if args.reason is not None else {}
    to = "dropped" if args.dropped else "done"
    _run_move("close", args.ids, args.plan, to, fields)


def _run_reopen(args: argparse.Namespace) -> None:
    _run_move("reopen", args.ids, args.plan, "open", {})
