from __future__ import annotations

import argparse
import sys

from booping import logger
from booping.context._yaml import update_marker
from booping.context.project import Project
from booping.migrations import latest_shipped_id


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "marker-set",
        help="Set a key on the resolved .booping marker",
    )
    p.add_argument(
        "pair",
        metavar="key=value",
        help="Marker key=value pair (e.g. latest_migration=3, latest_migration=@latest)",
    )
    p.set_defaults(func=_run)


def _parse_pair(pair: str) -> tuple[str, object]:
    if "=" not in pair:
        print(f"error: malformed key=value pair: {pair!r}", file=sys.stderr)
        sys.exit(1)
    key, _, value = pair.partition("=")
    if not key:
        print(f"error: empty key in pair: {pair!r}", file=sys.stderr)
        sys.exit(1)
    if key == "latest_migration":
        if value == "@latest":
            return key, latest_shipped_id()
        try:
            return key, int(value)
        except ValueError:
            print(
                f"error: latest_migration must be an integer, got {value!r}",
                file=sys.stderr,
            )
            sys.exit(1)
    return key, value


def _run(args: argparse.Namespace) -> None:
    key, value = _parse_pair(args.pair)

    project = Project.load_cwd_configured()
    if project is None or project.repo_directory is None:
        print("error: no .booping marker found from the current directory", file=sys.stderr)
        sys.exit(2)

    marker = project.repo_directory / ".booping"
    try:
        update_marker(marker, {key: value})
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    logger.log(vault=project.directory, subcommand="marker-set", message=f"{marker} {key}={value}")
    print(f"marker: {key}={value}", file=sys.stderr)
