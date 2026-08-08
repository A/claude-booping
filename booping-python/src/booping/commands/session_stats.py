from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn, cast

from booping.context._yaml import parse_frontmatter_only, update_frontmatter
from booping.session_stats import (
    Report,
    SessionStats,
    Tokens,
    build_report,
    default_projects_root,
)

# Flat and `metrics_`-prefixed: Obsidian Properties and Bases cannot address a
# nested mapping, and surfacing these as sprints.md columns is the whole point.
METRIC_KEYS = (
    "metrics_active_minutes",
    "metrics_models",
    "metrics_tokens_input",
    "metrics_tokens_output",
    "metrics_tokens_cache_creation",
    "metrics_tokens_cache_read",
)

ALREADY_STAMPED = "already stamped; --force to override"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "session-stats",
        help="Mine active minutes, tokens and models from artifacts' stamped sessions",
        description=(
            "Walk a directory by mask (or take a single file), mine each artifact's "
            "sessions: list, stamp the metrics_* frontmatter keys and print one JSON "
            "document on stdout."
        ),
    )
    p.add_argument("path", type=Path, help="Artifact file, or directory to walk")
    p.add_argument(
        "--mask",
        default="index.md",
        metavar="GLOB",
        help="Filename glob used when path is a directory (default: index.md)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite metrics_* values on artifacts that already carry them",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print without writing anything",
    )
    p.add_argument(
        "--projects-root",
        type=Path,
        default=None,
        metavar="PATH",
        help="Root of Claude Code session transcripts (default: ~/.claude/projects)",
    )
    p.set_defaults(func=_run)


def _fail(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    sys.exit(1)


def _metrics(minutes: int, models: list[str], tokens: Tokens) -> dict[str, Any]:
    return {
        "metrics_active_minutes": minutes,
        "metrics_models": models,
        "metrics_tokens_input": tokens.input,
        "metrics_tokens_output": tokens.output,
        "metrics_tokens_cache_creation": tokens.cache_creation,
        "metrics_tokens_cache_read": tokens.cache_read,
    }


def _session_entry(session: SessionStats) -> dict[str, Any]:
    metrics = _metrics(session.minutes, session.models, session.tokens)
    return {"session": session.session_id, **metrics}


def _totals(report: Report) -> dict[str, Any]:
    return _metrics(report.total_minutes, report.models, report.tokens)


def _frontmatter(path: Path) -> dict[str, Any]:
    try:
        return parse_frontmatter_only(path)
    except Exception as exc:
        _fail(f"error: cannot read frontmatter of {path}: {exc}")


def _session_ids(path: Path, raw: object) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        _fail(f"error: sessions: is not a list in {path}")
    return [str(item) for item in cast(list[object], raw) if item]


def _artifacts(root: Path, mask: str) -> list[Path]:
    if not root.exists():
        _fail(f"error: path not found: {root}")
    if not root.is_dir():
        return [root]
    found = sorted(p for p in root.rglob(mask) if p.is_file())
    if not found:
        _fail(f"error: no artifact matching {mask!r} under {root}")
    return found


def _process(path: Path, display: str, args: argparse.Namespace) -> dict[str, Any] | None:
    frontmatter = _frontmatter(path)
    if "sessions" not in frontmatter:
        print(f"note: no sessions: key in {path}; skipped", file=sys.stderr)
        return None

    if not args.force and any(frontmatter.get(key) is not None for key in METRIC_KEYS):
        return {
            "path": display,
            "written": False,
            "skipped": ALREADY_STAMPED,
            "sessions": [],
            "totals": {},
        }

    projects_root: Path = args.projects_root or default_projects_root()
    report = build_report(_session_ids(path, frontmatter["sessions"]), projects_root)
    for warning in report.warnings:
        print(warning, file=sys.stderr)

    totals = _totals(report)
    written = False
    if not args.dry_run:
        try:
            update_frontmatter(path, totals)
        except Exception as exc:
            print(f"error: cannot write {path}: {exc}", file=sys.stderr)
            sys.exit(2)
        written = True

    return {
        "path": display,
        "written": written,
        "sessions": [_session_entry(session) for session in report.sessions],
        "totals": totals,
    }


def _run(args: argparse.Namespace) -> None:
    root: Path = args.path
    artifacts = _artifacts(root, args.mask)

    entries: list[dict[str, Any]] = []
    for path in artifacts:
        display = str(path.relative_to(root)) if root.is_dir() else str(path)
        entry = _process(path, display, args)
        if entry is not None:
            entries.append(entry)

    print(json.dumps({"artifacts": entries}, indent=2))
