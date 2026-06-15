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
        nargs="+",
        metavar="key=val",
        help="Frontmatter key=value pairs (@now, @today, @head interpolation)",
    )
    p.set_defaults(func=_run)


def _interpolate(value: str, repo_dir: Path | None) -> str:
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


def _parse_pairs(pairs: list[str]) -> dict[str, str]:
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

    updates = _parse_pairs(args.pairs)

    project = Project.load_cwd()
    repo_dir = project.repo_directory if project is not None else None

    resolved: dict[str, object] = {}
    for key, value in updates.items():
        resolved[key] = _interpolate(value, repo_dir)

    try:
        update_frontmatter(plan_path, resolved)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    vault = project.directory if project is not None else None
    keys_str = " ".join(resolved.keys())
    logger.log(vault=vault, subcommand="frontmatter-update", message=f"{plan_path} {keys_str}")

    print(
        f"updated {plan_path}: {', '.join(f'{k}={v}' for k, v in resolved.items())}",
        file=sys.stderr,
    )