from __future__ import annotations

import argparse
import sys

from booping.commands import render as render_cmd


def _not_implemented(args: argparse.Namespace) -> None:
    print(f"not implemented: {args.subcommand}", file=sys.stderr)
    sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booping",
        description="booping CLI",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")
    sub.required = True

    render_cmd.add_parser(sub)

    for name in ("plans", "debug-context", "debug-template"):
        p = sub.add_parser(name)
        p.set_defaults(func=_not_implemented)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
