from __future__ import annotations

import argparse

from booping.commands import build as build_cmd
from booping.commands import config_get as config_get_cmd
from booping.commands import debug as debug_cmd
from booping.commands import frontmatter_update as frontmatter_update_cmd
from booping.commands import render as render_cmd
from booping.commands import render_sprints as render_sprints_cmd
from booping.commands import transition as transition_cmd
from booping.commands import vault_commit as vault_commit_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booping",
        description="booping CLI",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")
    sub.required = True

    render_cmd.add_parser(sub)
    render_sprints_cmd.add_parser(sub)
    config_get_cmd.add_parser(sub)
    build_cmd.add_parser(sub)
    debug_cmd.add_parser(sub)
    frontmatter_update_cmd.add_parser(sub)
    transition_cmd.add_parser(sub)
    vault_commit_cmd.add_parser(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
