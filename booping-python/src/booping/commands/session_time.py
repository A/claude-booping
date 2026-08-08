from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.session_time import build_report, default_projects_root


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "session-time",
        help="Report active minutes and model ids for a plan's stamped sessions",
    )
    p.add_argument("plan", type=Path, help="Path to the plan markdown file")
    p.add_argument(
        "--write",
        action="store_true",
        help="Stamp active_minutes: and models: onto the plan frontmatter",
    )
    p.add_argument(
        "--projects-root",
        type=Path,
        default=None,
        metavar="PATH",
        help="Root of Claude Code session transcripts (default: ~/.claude/projects)",
    )
    p.set_defaults(func=_run)


def _session_ids(plan_path: Path) -> list[str]:
    try:
        frontmatter = parse_frontmatter_only(plan_path)
    except Exception as exc:
        print(f"error: cannot read frontmatter of {plan_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    if "sessions" not in frontmatter:
        print(f"error: no sessions: key in {plan_path}", file=sys.stderr)
        sys.exit(1)

    raw = frontmatter["sessions"]
    if raw is None:
        return []
    if not isinstance(raw, list):
        print(f"error: sessions: is not a list in {plan_path}", file=sys.stderr)
        sys.exit(1)
    return [str(item) for item in raw if item]  # type: ignore[reportUnknownVariableType]


def _run(args: argparse.Namespace) -> None:
    plan_path: Path = args.plan
    if not plan_path.is_file():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    session_ids = _session_ids(plan_path)
    projects_root: Path = args.projects_root or default_projects_root()
    report = build_report(session_ids, projects_root)

    for warning in report.warnings:
        print(warning, file=sys.stderr)

    for session in report.sessions:
        print(f"{session.session_id}  {session.minutes}m  {','.join(session.models)}")
    print(f"total  {report.total_minutes}m")
    print(f"models  {','.join(report.models)}")

    if args.write:
        try:
            update_frontmatter(
                plan_path,
                {"active_minutes": report.total_minutes, "models": report.models},
            )
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(2)
