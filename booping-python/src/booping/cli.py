from __future__ import annotations

import argparse
import sys

from booping.commands import render as render_cmd
from booping.commands import debug as debug_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="booping")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    render_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)

    for name in ("plans",):
        p = sub.add_parser(name)
        p.set_defaults(func=_not_implemented, func_name=name)

    return parser


def _not_implemented(args: argparse.Namespace) -> None:
    print(f"'{args.func_name}' not implemented", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()