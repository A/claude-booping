from __future__ import annotations

import argparse

from booping import logger
from booping.commands.specs import (
    _assemble,  # pyright: ignore[reportPrivateUsage]
    _fail,  # pyright: ignore[reportPrivateUsage]
)
from booping.specs import open_items
from booping.specs.open_items import OpenItemError
from booping.status import SECTIONS, StatusContext, StatusError


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "status",
        help="Print the project status computed from the vault — short by default, detail"
        " per section",
    )
    p.add_argument(
        "section",
        nargs="*",
        choices=[section.name for section in SECTIONS],
        help="Print these sections in detail",
    )
    p.add_argument("--detail", action="store_true", help="Print every section in detail")
    p.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> None:
    ctx = _assemble()[0]
    named: list[str] = args.section
    sc = StatusContext(ctx)
    try:
        open_items.require_vault(ctx)
        if not named and not args.detail:
            out = [section.summary(sc) for section in SECTIONS]
        else:
            out = [
                f"## {section.name}\n\n{section.detail(sc)}\n"
                for section in SECTIONS
                if args.detail or section.name in named
            ]
    except (OpenItemError, StatusError) as exc:
        _fail(str(exc))
    logger.log(vault=ctx.vault, subcommand="status", message=f"status {' '.join(named) or 'short'}")
    print("\n".join(out).rstrip("\n"))
