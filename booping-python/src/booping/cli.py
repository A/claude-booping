from __future__ import annotations

import argparse
from typing import cast

from booping.argparser import Parser
from booping.commands import budget as budget_cmd
from booping.commands import config_get as config_get_cmd
from booping.commands import correction as correction_cmd
from booping.commands import debug as debug_cmd
from booping.commands import defaults as defaults_cmd
from booping.commands import frontmatter_update as frontmatter_update_cmd
from booping.commands import items as items_cmd
from booping.commands import marker_set as marker_set_cmd
from booping.commands import plan as plan_cmd
from booping.commands import playbook_state as playbook_state_cmd
from booping.commands import playbook_transition as playbook_transition_cmd
from booping.commands import query as query_cmd
from booping.commands import render as render_cmd
from booping.commands import render_playbook as render_playbook_cmd
from booping.commands import run as run_cmd
from booping.commands import scaffold as scaffold_cmd
from booping.commands import session_stats as session_stats_cmd
from booping.commands import specs as specs_cmd
from booping.commands import status as status_cmd


def build_parser() -> argparse.ArgumentParser:
    # Subparsers inherit the Parser class at runtime; the commands' add_parser
    # signatures take the invariant _SubParsersAction[ArgumentParser].
    parser = cast(argparse.ArgumentParser, Parser(prog="booping", description="booping CLI"))
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")
    sub.required = True

    render_cmd.add_parser(sub)
    render_playbook_cmd.add_parser(sub)
    playbook_transition_cmd.add_parser(sub)
    playbook_state_cmd.add_parser(sub)
    config_get_cmd.add_parser(sub)
    marker_set_cmd.add_parser(sub)
    query_cmd.add_parser(sub)
    scaffold_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)
    frontmatter_update_cmd.add_parser(sub)
    session_stats_cmd.add_parser(sub)
    specs_cmd.add_parser(sub)
    correction_cmd.add_parser(sub)
    defaults_cmd.add_parser(sub)
    items_cmd.add_parser(sub)
    plan_cmd.add_parser(sub)
    status_cmd.add_parser(sub)
    run_cmd.add_parser(sub)
    budget_cmd.add_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
