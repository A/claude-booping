from __future__ import annotations

import argparse
from typing import cast

from booping.argparser import Parser
from booping.commands import config as config_cmd
from booping.commands import create as create_cmd
from booping.commands import debug as debug_cmd
from booping.commands import plan as plan_cmd
from booping.commands import query as query_cmd
from booping.commands import render as render_cmd
from booping.commands import render_playbook as render_playbook_cmd
from booping.commands import run as run_cmd
from booping.commands import session_stats as session_stats_cmd
from booping.commands import set as set_cmd
from booping.commands import specs as specs_cmd
from booping.commands import state as state_cmd
from booping.commands import status as status_cmd
from booping.commands import transition as transition_cmd


def build_parser() -> argparse.ArgumentParser:
    # Subparsers inherit the Parser class at runtime; the commands' add_parser
    # signatures take the invariant _SubParsersAction[ArgumentParser].
    parser = cast(argparse.ArgumentParser, Parser(prog="booping", description="booping CLI"))
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")
    sub.required = True

    render_cmd.add_parser(sub)
    render_playbook_cmd.add_parser(sub)
    transition_cmd.add_parser(sub)
    state_cmd.add_parser(sub)
    config_cmd.add_parser(sub)
    set_cmd.add_parser(sub)
    query_cmd.add_parser(sub)
    create_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)
    session_stats_cmd.add_parser(sub)
    specs_cmd.add_parser(sub)
    plan_cmd.add_parser(sub)
    status_cmd.add_parser(sub)
    run_cmd.add_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
