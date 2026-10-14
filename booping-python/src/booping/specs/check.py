from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.context.lesson import TargetRejection, parse_target
from booping.specs.records import Record, load_tier
from booping.specs.tiers import Tier

LAYOUT_MESSAGE = "a record lives at {type}/{NNNN}-{slug}.md"


class Finding(BaseModel):
    path: Path
    line: int
    level: Literal["error", "warning"]
    check: str
    message: str


class CheckError(Exception):
    """An internal failure (exit 2): mdcheck missing, crashing or printing garbage."""


def display_path(path: Path) -> str:
    cwd = Path.cwd()
    return str(path.relative_to(cwd)) if path.is_relative_to(cwd) else str(path)


def format_finding(f: Finding) -> str:
    return f"{display_path(f.path)}:{f.line}  {f.level}  {f.check}  {f.message}"


def _error(path: Path, check: str, message: str, line: int = 1) -> Finding:
    return Finding(path=path, line=line, level="error", check=check, message=message)


def _type_key_line(path: Path) -> int:
    lines = path.read_text().splitlines()
    for index, text in enumerate(lines[1:], start=2):
        if text.strip() == "---":
            break
        if text.startswith("type:"):
            return index
    return 1


def _check_filename(record: Record) -> list[Finding]:
    if record.number is None:
        return [_error(record.path, "filename", "file name is not {NNNN}-{slug}.md")]
    return []


def _check_frontmatter(record: Record) -> list[Finding]:
    if record.frontmatter_error is not None:
        # PyYAML appends the location and a caret snippet on further lines; a finding is one line.
        return [_error(record.path, "frontmatter", record.frontmatter_error.splitlines()[0])]
    declared = record.frontmatter.get("type")
    if declared is not None and declared != record.type:
        return [
            _error(
                record.path,
                "frontmatter",
                f"type is `{declared}`, the directory is `{record.type}`",
                _type_key_line(record.path),
            )
        ]
    return []


def _check_targets(record: Record) -> list[Finding]:
    if record.type != "rule":
        return []
    raw = record.frontmatter.get("targets")
    has_brief = record.frontmatter.get("brief") is not None
    if raw is None:
        return [_error(record.path, "targets", "brief without targets")] if has_brief else []
    findings: list[Finding] = []
    if not has_brief:
        findings.append(_error(record.path, "targets", "targets without brief"))
    entries: list[Any] = list(raw) if isinstance(raw, list) else [raw]  # pyright: ignore[reportUnknownArgumentType]
    for entry in entries:
        result = parse_target(entry)
        if isinstance(result, TargetRejection):
            findings.append(
                _error(record.path, "targets", f"target `{result.entry}`: {result.reason}")
            )
    return findings


def run_mdcheck(schema: Path, record: Record) -> list[Finding]:
    try:
        proc = subprocess.run(
            ["mdcheck", str(schema), "-", "--format", "json"],
            input=record.path.read_text(),
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise CheckError("mdcheck not found on PATH — cargo install markdown-checker") from exc
    if proc.returncode not in (0, 1):
        detail = proc.stderr.strip().splitlines()
        raise CheckError(
            f"mdcheck exited {proc.returncode} on {display_path(record.path)}"
            + (f": {detail[0]}" if detail else "")
        )
    try:
        findings = json.loads(proc.stdout)["findings"]
        return [_error(record.path, "schema", str(f["message"]), int(f["line"])) for f in findings]
    except (ValueError, KeyError, TypeError) as exc:
        raise CheckError(
            f"mdcheck printed unparsable JSON for {display_path(record.path)}"
        ) from exc


def _check_ids(records: list[Record]) -> list[Finding]:
    by_number: dict[tuple[str, int], list[Record]] = {}
    for r in records:
        if r.number is not None:
            by_number.setdefault((r.type, r.number), []).append(r)
    findings: list[Finding] = []
    for (type_, number), group in by_number.items():
        for r in group:
            for other in group:
                if other is not r:
                    findings.append(
                        _error(
                            r.path,
                            "id",
                            f"{type_}/{number:04d} is also used by {display_path(other.path)}",
                        )
                    )
    return findings


# Checks over the whole tier's well-placed records; M05 appends link, ref, sources, namespace.
CROSS_FILE_CHECKS: list[Callable[[list[Record]], list[Finding]]] = [_check_ids]


def check_tier(tier: Tier, format_dir: Path, known: list[str]) -> tuple[list[Finding], int]:
    """Findings sorted by path then line, and the number of records checked."""
    if shutil.which("mdcheck") is None:
        raise CheckError("mdcheck not found on PATH — cargo install markdown-checker")

    records = load_tier(tier, known)
    strays = sorted(p for p in tier.root.glob("*.md") if p.is_file() and p.name != "README.md")
    findings = [_error(p, "layout", LAYOUT_MESSAGE) for p in strays]

    placed: list[Record] = []
    for record in records:
        if record.type not in known:
            findings.append(_error(record.path, "layout", LAYOUT_MESSAGE))
            continue
        placed.append(record)
        findings += _check_filename(record)
        findings += _check_frontmatter(record)
        findings += _check_targets(record)
        findings += run_mdcheck(format_dir / "schemas" / f"{record.type}.yaml", record)

    for cross_file in CROSS_FILE_CHECKS:
        findings += cross_file(placed)

    findings.sort(key=lambda f: (display_path(f.path), f.line))
    return findings, len(records) + len(strays)
