from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from booping.specs.links import relative_links
from booping.specs.records import Record, load_tier, parse_ref
from booping.specs.targets import TargetRejection, parse_target
from booping.specs.tiers import Tier

LAYOUT_MESSAGE = "a record lives at {type}/{NNNN}-{slug}.md"

REF_FIELDS = {"values": "value", "rules": "rule", "supersedes": "adr"}


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


def _key_line(path: Path, key: str) -> int:
    lines = path.read_text().splitlines()
    for index, text in enumerate(lines[1:], start=2):
        if text.strip() == "---":
            break
        if text.startswith(f"{key}:"):
            return index
    return 1


def _check_filename(record: Record) -> list[Finding]:
    if record.number is None:
        return [_error(record.path, "filename", "file name is not {NNNN}-{slug}.md")]
    return []


def _check_frontmatter(record: Record) -> list[Finding]:
    if record.frontmatter_error is not None:
        return [
            _error(
                record.path,
                "frontmatter",
                record.frontmatter_error,
                record.frontmatter_error_line,
            )
        ]
    declared = record.frontmatter.get("type")
    if declared is not None and declared != record.type:
        return [
            _error(
                record.path,
                "frontmatter",
                f"type is `{declared}`, the directory is `{record.type}`",
                _key_line(record.path, "type"),
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


def _check_ids(records: list[Record], scope: Scope) -> list[Finding]:
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


class Scope(BaseModel):
    """What a cross-file check sees beyond the records: the checked tier and the
    `{namespace → (tier, {type → {number}})}` index over every resolved tier."""

    tier: Tier
    own: dict[str, set[int]]
    namespaces: dict[str, tuple[Tier, dict[str, set[int]]]]


def _numbers(records: list[Record]) -> dict[str, set[int]]:
    index: dict[str, set[int]] = {}
    for r in records:
        if r.number is not None:
            index.setdefault(r.type, set()).add(r.number)
    return index


def _check_links(records: list[Record], scope: Scope) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        text = record.path.read_text()
        first_line = text[: len(text) - len(record.body)].count("\n") + 1
        for link in relative_links(record.body, first_line):
            if not (record.path.parent / link.path).exists():
                findings.append(
                    _error(
                        record.path,
                        "link",
                        f"link target `{link.dest}` does not exist",
                        link.line,
                    )
                )
    return findings


def _list_field(record: Record, field: str) -> tuple[list[Any] | None, Finding | None]:
    value = record.frontmatter.get(field)
    if value is None:
        return None, None
    if not isinstance(value, list):
        line = _key_line(record.path, field)
        check = "ref" if field in REF_FIELDS else field
        return None, _error(record.path, check, f"{field}: must be a list", line)
    return list(value), None  # pyright: ignore[reportUnknownArgumentType]


def _namespace(record: Record, line: int, message: str) -> Finding:
    return Finding(path=record.path, line=line, level="warning", check="namespace", message=message)


def _check_refs(records: list[Record], scope: Scope) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        for field, type_ in REF_FIELDS.items():
            items, invalid = _list_field(record, field)
            if invalid is not None:
                findings.append(invalid)
            if not items:
                continue
            line = _key_line(record.path, field)
            for item in items:
                ref = parse_ref(str(item))
                if ref is None or ref.type != type_:
                    findings.append(
                        _error(record.path, "ref", f"{field}: `{item}` is not a {type_} ref", line)
                    )
                    continue
                if ref.namespace is None:
                    numbers = scope.own
                elif ref.namespace not in scope.namespaces:
                    findings.append(
                        _namespace(
                            record, line, f"{field}: namespace `{ref.namespace}` names no tier"
                        )
                    )
                    continue
                else:
                    target, numbers = scope.namespaces[ref.namespace]
                    if not target.root.is_dir():
                        message = f"tier `{target.name}` has no specs at {target.root}"
                        findings.append(_namespace(record, line, f"{field}: {message}"))
                        continue
                if ref.number not in numbers.get(ref.type, set()):
                    findings.append(
                        _error(record.path, "ref", f"{field}: `{item}` does not exist", line)
                    )
    return findings


def _check_sources(records: list[Record], scope: Scope) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        entries, invalid = _list_field(record, "sources")
        if invalid is not None:
            findings.append(invalid)
        if not entries:
            continue
        line = _key_line(record.path, "sources")
        for entry in entries:
            text = str(entry)
            if "://" not in text and not (scope.tier.anchor / text).exists():
                findings.append(
                    _error(record.path, "sources", f"sources: `{text}` does not exist", line)
                )
    return findings


# Checks over the whole tier's well-placed records.
CROSS_FILE_CHECKS: list[Callable[[list[Record], Scope], list[Finding]]] = [
    _check_ids,
    _check_links,
    _check_refs,
    _check_sources,
]


def _scope(tier: Tier, records: list[Record], tiers: list[Tier], known: list[str]) -> Scope:
    namespaces: dict[str, tuple[Tier, dict[str, set[int]]]] = {}
    for t in tiers:
        if t.namespace is None:
            continue
        loaded = records if t.root == tier.root else load_tier(t, known)
        namespaces[t.namespace] = (t, _numbers([r for r in loaded if r.type in known]))
    return Scope(tier=tier, own=_numbers(records), namespaces=namespaces)


def check_tier(
    tier: Tier, format_dir: Path, known: list[str], tiers: list[Tier]
) -> tuple[list[Finding], int]:
    """Findings sorted by path then line, and the number of records checked.
    `tiers` is every resolved tier; namespaced refs resolve against them."""
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

    scope = _scope(tier, placed, tiers, known)
    for cross_file in CROSS_FILE_CHECKS:
        findings += cross_file(placed, scope)

    findings.sort(key=lambda f: (display_path(f.path), f.line))
    return findings, len(records) + len(strays)
