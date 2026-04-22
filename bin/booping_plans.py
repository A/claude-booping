import argparse
import datetime
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError
from ruamel.yaml.parser import ParserError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_VALUES = [
    "backlog",
    "in-spec",
    "ready-for-dev",
    "in-progress",
    "awaiting-retro",
    "awaiting-learning",
    "done",
    "fail",
    "cancelled",
]

GOAL_VALUES = ["success", "partial", "fail"]

TYPE_VALUES = ["feature", "bug", "refactoring"]

TERMINAL_STATUSES = {"done", "fail", "cancelled"}

KNOWN_KEYS = {
    "title",
    "type",
    "status",
    "sp",
    "source",
    "created",
    "planned",
    "started",
    "completed",
    "retro",
    "goal",
    "business_goal",
}

ENUM_FIELDS = {
    "status": STATUS_VALUES,
    "goal": GOAL_VALUES,
    "type": TYPE_VALUES,
}

DATE_FIELDS = {"planned", "started", "completed", "created"}

# Status → auto-fill mapping: status value → (field_to_fill,)
AUTO_FILL = {
    "ready-for-dev": "planned",
    "in-progress": "started",
    "awaiting-retro": "completed",
    "fail": "completed",
    "cancelled": "completed",
}

EXIT_OK = 0
EXIT_GENERIC = 1
EXIT_NOT_FOUND = 2
EXIT_MALFORMED_NONFATAL = 3
EXIT_MISSING_PROJECT = 4
EXIT_INVALID_ENUM = 5
EXIT_MALFORMED_FATAL = 6


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def _make_yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    return y


def _parse_frontmatter(path: Path):
    """Parse YAML frontmatter from a markdown file.

    Returns (frontmatter_dict, body_text) on success.
    Raises ScannerError/ParserError/ValueError on malformed content.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("no frontmatter delimiter found")
    # Find the closing ---
    rest = text[3:]
    end = rest.find("\n---")
    if end == -1:
        raise ValueError("frontmatter closing delimiter not found")
    yaml_text = rest[:end + 1]  # include the trailing newline
    body = rest[end + 4:]  # skip \n---
    y = _make_yaml()
    import io
    fm = y.load(io.StringIO(yaml_text))
    if not isinstance(fm, dict):
        raise ValueError("frontmatter is not a mapping")
    return fm, body, yaml_text


def _write_frontmatter(path: Path, fm, body: str):
    """Write updated frontmatter back to the file, preserving round-trip fidelity."""
    import io
    y = _make_yaml()
    buf = io.StringIO()
    y.dump(fm, buf)
    fm_text = buf.getvalue()
    path.write_text("---\n" + fm_text + "---" + body, encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_enum(key: str, value: str) -> int:
    """Return EXIT_INVALID_ENUM and print error if invalid, else EXIT_OK."""
    allowed = ENUM_FIELDS[key]
    if value not in allowed:
        print(
            f"error: {key} must be one of: {', '.join(allowed)}",
            file=sys.stderr,
        )
        return EXIT_INVALID_ENUM
    return EXIT_OK


def _validate_date(key: str, value: str) -> int:
    try:
        datetime.date.fromisoformat(value)
        return EXIT_OK
    except ValueError:
        print(f"error: {key} must be YYYY-MM-DD", file=sys.stderr)
        return EXIT_INVALID_ENUM


# ---------------------------------------------------------------------------
# Subcommand: list
# ---------------------------------------------------------------------------

def _cmd_list(args) -> int:
    # Validate --status filter early
    if args.status and args.status not in STATUS_VALUES:
        print(
            f"error: status must be one of: {', '.join(STATUS_VALUES)}",
            file=sys.stderr,
        )
        return EXIT_INVALID_ENUM

    plans_dir = Path.home() / "Claude" / args.project / "plans"
    plan_files = sorted(plans_dir.glob("*.md")) if plans_dir.exists() else []

    rows = []
    had_malformed = False

    for p in plan_files:
        try:
            fm, _, _ = _parse_frontmatter(p)
        except (ScannerError, ParserError, ValueError) as e:
            print(f"warning: {p}: {e}", file=sys.stderr)
            had_malformed = True
            continue

        status = fm.get("status", "")
        if args.status and status != args.status:
            continue

        sp = fm.get("sp")
        sp_str = _format_sp(sp)
        plan_type = fm.get("type", "")
        title = fm.get("title", "")
        rows.append((str(status), sp_str, str(plan_type), str(title), str(p)))

    # Print table
    if rows:
        headers = ("status", "sp", "type", "title", "path")
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        def fmt_row(cells):
            return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

        print(fmt_row(headers))
        print("-+-".join("-" * w for w in widths))
        for row in rows:
            print(fmt_row(row))

    return EXIT_MALFORMED_NONFATAL if had_malformed else EXIT_OK


# ---------------------------------------------------------------------------
# Subcommand: set
# ---------------------------------------------------------------------------

def _cmd_set(args) -> int:
    plan_path = Path(args.plan_path)
    if not plan_path.exists():
        print(f"error: plan not found: {plan_path}", file=sys.stderr)
        return EXIT_NOT_FOUND

    # Parse key=value pairs
    updates: dict[str, str] = {}
    for kv in args.assignments:
        parts = kv.split("=", 1)
        if len(parts) != 2:
            print(f"error: invalid assignment (expected key=value): {kv}", file=sys.stderr)
            return EXIT_GENERIC
        key, value = parts
        updates[key] = value

    # Validate keys
    for key in updates:
        if key not in KNOWN_KEYS:
            print(
                f"error: {key} must be one of: {', '.join(sorted(KNOWN_KEYS))}",
                file=sys.stderr,
            )
            return EXIT_INVALID_ENUM

    # Validate values before loading the file
    for key, value in updates.items():
        if key in ENUM_FIELDS:
            rc = _validate_enum(key, value)
            if rc != EXIT_OK:
                return rc
        elif key in DATE_FIELDS:
            rc = _validate_date(key, value)
            if rc != EXIT_OK:
                return rc

    # Load the file
    try:
        fm, body, _ = _parse_frontmatter(plan_path)
    except (ScannerError, ParserError, ValueError) as e:
        print(f"error: {plan_path}: {e}", file=sys.stderr)
        return EXIT_MALFORMED_FATAL

    today = datetime.date.today()

    # Apply auto-fill for status transitions
    new_status = updates.get("status")
    if new_status and new_status in AUTO_FILL:
        fill_field = AUTO_FILL[new_status]
        # Auto-fill only when: user didn't pass it AND current value is None
        if fill_field not in updates and fm.get(fill_field) is None:
            updates[fill_field] = today.isoformat()

    # Apply updates to frontmatter
    for key, value in updates.items():
        if key in DATE_FIELDS:
            fm[key] = datetime.date.fromisoformat(value)
        elif key == "sp":
            # Parse sp as number
            try:
                if "." in value:
                    fm[key] = float(value)
                else:
                    fm[key] = int(value)
            except ValueError:
                print(f"error: sp must be a number", file=sys.stderr)
                return EXIT_GENERIC
        else:
            fm[key] = value

    _write_frontmatter(plan_path, fm, body)
    return EXIT_OK


# ---------------------------------------------------------------------------
# Subcommand: sync-sprints
# ---------------------------------------------------------------------------

def _cmd_sync_sprints(args) -> int:
    plans_dir = Path.home() / "Claude" / args.project / "plans"
    plan_files = sorted(plans_dir.glob("*.md")) if plans_dir.exists() else []

    active = []
    history = []
    had_malformed = False

    for p in plan_files:
        try:
            fm, _, _ = _parse_frontmatter(p)
        except (ScannerError, ParserError, ValueError) as e:
            print(f"warning: {p}: {e}", file=sys.stderr)
            had_malformed = True
            continue

        status = str(fm.get("status", ""))
        if status in TERMINAL_STATUSES:
            history.append((p, fm))
        else:
            active.append((p, fm))

    # Sort active: planned asc, fallback created, then filename asc
    def active_sort_key(item):
        p, fm = item
        planned = _coerce_date(fm.get("planned"))
        created = _coerce_date(fm.get("created"))
        primary = planned if planned is not None else (created if created is not None else datetime.date.min)
        return (primary, p.name)

    active.sort(key=active_sort_key)

    # Sort history: completed desc, fallback planned → created, filename desc
    def history_sort_key(item):
        p, fm = item
        completed = _coerce_date(fm.get("completed"))
        planned = _coerce_date(fm.get("planned"))
        created = _coerce_date(fm.get("created"))
        primary = completed if completed is not None else (
            planned if planned is not None else (
                created if created is not None else datetime.date.min
            )
        )
        return (primary, p.name)

    # Sort ascending, then reverse the full sequence — this gives desc-by-date with
    # desc-by-filename as the tie-breaker, matching the plan's M1.4 DoD.
    history.sort(key=history_sort_key, reverse=True)

    # Build output
    lines = []
    lines.append("# Sprints")
    lines.append("")
    lines.append("Generated by booping-plans sync-sprints — do not hand-edit; run the CLI to update.")
    lines.append("")

    # Active table
    lines.append("## Active")
    lines.append("")
    lines.append("| Status | Title | Type | SP | Planned | Started | Business Goal |")
    lines.append("|--------|-------|------|----|---------|---------|---------------|")
    for p, fm in active:
        status = str(fm.get("status", ""))
        title = _escape_pipe(str(fm.get("title", "")))
        ftype = str(fm.get("type", ""))
        sp = _format_sp(fm.get("sp"))
        planned = _format_date(fm.get("planned"))
        started = _format_date(fm.get("started"))
        bg = fm.get("business_goal")
        bg_str = _escape_pipe(str(bg)) if bg else "—"
        lines.append(f"| {status} | {title} | {ftype} | {sp} | {planned} | {started} | {bg_str} |")

    lines.append("")

    # History table
    lines.append("## History")
    lines.append("")
    lines.append("| Status | Title | Type | SP | Planned | Completed | Goal | Retro |")
    lines.append("|--------|-------|------|----|---------|-----------|------|-------|")
    for p, fm in history:
        status = str(fm.get("status", ""))
        title = _escape_pipe(str(fm.get("title", "")))
        ftype = str(fm.get("type", ""))
        sp = _format_sp(fm.get("sp"))
        planned = _format_date(fm.get("planned"))
        completed = _format_date(fm.get("completed"))
        goal = str(fm.get("goal", "")) if fm.get("goal") else "—"
        retro = str(fm.get("retro", "")) if fm.get("retro") else "—"
        lines.append(f"| {status} | {title} | {ftype} | {sp} | {planned} | {completed} | {goal} | {retro} |")

    lines.append("")

    content = "\n".join(lines)

    sprints_path = Path.home() / "Claude" / args.project / "sprints.md"
    sprints_path.write_text(content, encoding="utf-8")

    return EXIT_MALFORMED_NONFATAL if had_malformed else EXIT_OK


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _coerce_date(value) -> datetime.date | None:
    """Convert a value to datetime.date or return None."""
    if value is None:
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _format_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def _format_sp(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        # Remove trailing zeros
        return f"{value:g}"
    return str(value)


def _escape_pipe(s: str) -> str:
    return s.replace("|", "\\|")


# ---------------------------------------------------------------------------
# Argparse setup
# ---------------------------------------------------------------------------

def _print_missing_project():
    print(
        "error: --project is required. "
        "Usage: booping-plans <subcommand> --project=<name> [...]. "
        "Example: booping-plans list --project=claude-booping",
        file=sys.stderr,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booping-plans",
        description=(
            "Manage booping plan frontmatter and sprint rollup.\n\n"
            "Exit codes:\n"
            "  0  ok\n"
            "  1  generic error\n"
            "  2  file not found (set never creates)\n"
            "  3  malformed frontmatter (non-fatal: list/sync-sprints warn + skip)\n"
            "  4  missing --project argument\n"
            "  5  invalid enum value or unknown key\n"
            "  6  malformed frontmatter (fatal: set can't round-trip broken YAML)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="subcommand")

    # list
    p_list = subparsers.add_parser("list", help="List plans")
    p_list.add_argument("--project", metavar="NAME", default=None)
    p_list.add_argument("--status", metavar="STATUS", default=None)

    # set
    p_set = subparsers.add_parser("set", help="Set frontmatter keys on a plan")
    p_set.add_argument("--project", metavar="NAME", default=None)
    p_set.add_argument("plan_path", metavar="PLAN_PATH")
    p_set.add_argument("assignments", metavar="KEY=VALUE", nargs="+")

    # sync-sprints
    p_sync = subparsers.add_parser("sync-sprints", help="Regenerate sprints.md")
    p_sync.add_argument("--project", metavar="NAME", default=None)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.subcommand is None:
        parser.print_help()
        return EXIT_GENERIC

    # Check --project presence for all subcommands
    if not getattr(args, "project", None):
        _print_missing_project()
        return EXIT_MISSING_PROJECT

    if args.subcommand == "list":
        return _cmd_list(args)
    elif args.subcommand == "set":
        return _cmd_set(args)
    elif args.subcommand == "sync-sprints":
        return _cmd_sync_sprints(args)
    else:
        print(f"error: unknown subcommand: {args.subcommand}", file=sys.stderr)
        return EXIT_GENERIC
