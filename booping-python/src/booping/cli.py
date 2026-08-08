from __future__ import annotations

import argparse

from booping.commands import build as build_cmd
from booping.commands import config_get as config_get_cmd
from booping.commands import debug as debug_cmd
from booping.commands import frontmatter_update as frontmatter_update_cmd
from booping.commands import marker_set as marker_set_cmd
from booping.commands import playbook_state as playbook_state_cmd
from booping.commands import playbook_transition as playbook_transition_cmd
from booping.commands import query as query_cmd
from booping.commands import render as render_cmd
from booping.commands import render_playbook as render_playbook_cmd
from booping.commands import scaffold as scaffold_cmd
from booping.commands import session_time as session_time_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booping",
        description="booping CLI",
    )
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
    build_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)
    frontmatter_update_cmd.add_parser(sub)
    session_time_cmd.add_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
