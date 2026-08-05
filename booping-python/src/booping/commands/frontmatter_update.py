from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from booping import logger
from booping.context._yaml import update_frontmatter
from booping.context.project import Project


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "frontmatter-update",
        help="Update frontmatter keys in a plan file with @now/@today/@head interpolation",
    )
    p.add_argument("plan", type=Path, help="Path to the plan markdown file")
    p.add_argument(
        "pairs",
        nargs="*",
        metavar="key=val",
        help="Frontmatter key=value pairs (@now, @today, @head interpolation)",
    )
    p.add_argument(
        "--remove",
        dest="removals",
        action="append",
        default=[],
        metavar="key",
        help="Frontmatter key to remove (repeatable); applied before key=value sets",
    )
    p.set_defaults(func=_run)


def interpolate(value: str, repo_dir: Path | None) -> str:
    if value == "@now":
        return datetime.now(UTC).strftime("%Y%m%d %H:%M")
    if value == "@today":
        return datetime.now(UTC).strftime("%Y-%m-%d")
    if value == "@head":
        cwd = repo_dir if repo_dir is not None else Path.cwd()
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"error: git rev-parse HEAD failed: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        return result.stdout.strip()
    return value


def parse_pairs(pairs: list[str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            print(f"error: malformed key=value pair: {pair!r}", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        if not key:
            print(f"error: empty key in pair: {pair!r}", file=sys.stderr)
            sys.exit(1)
        updates[key] = value
    return updates


def _run(args: argparse.Namespace) -> None:
    plan_path: Path = args.plan
    if not plan_path.is_file():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    removals: list[str] = list(getattr(args, "removals", None) or [])
    updates = parse_pairs(args.pairs)

    if not updates and not removals:
        print("error: nothing to do: provide key=value pairs and/or --remove", file=sys.stderr)
        sys.exit(1)

    project = Project.load_cwd_configured()
    repo_dir = project.repo_directory if project is not None else None

    resolved: dict[str, object] = {}
    for key, value in updates.items():
        resolved[key] = interpolate(value, repo_dir)

    try:
        update_frontmatter(plan_path, resolved, removals=removals)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    vault = project.directory if project is not None else None
    changed = [f"-{k}" for k in removals] + list(resolved.keys())
    logger.log(
        vault=vault, subcommand="frontmatter-update", message=f"{plan_path} {' '.join(changed)}"
    )

    parts = [f"-{k}" for k in removals] + [f"{k}={v}" for k, v in resolved.items()]
    print(f"updated {plan_path}: {', '.join(parts)}", file=sys.stderr)