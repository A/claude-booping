from __future__ import annotations

import argparse

from booping.commands import build as build_cmd
from booping.commands import compile as compile_cmd
from booping.commands import debug as debug_cmd
from booping.commands import render as render_cmd
from booping.commands import render_cli_agent as render_cli_agent_cmd
from booping.commands import render_sprints as render_sprints_cmd
from booping.commands import run_agent as run_agent_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booping",
        description="booping CLI",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")
    sub.required = True

    render_cmd.add_parser(sub)
    render_sprints_cmd.add_parser(sub)
    build_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)
    run_agent_cmd.add_parser(sub)
    render_cli_agent_cmd.add_parser(sub)
    compile_cmd.add_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
