"""The milestone contract as code: findings over one milestone file's text.

Pure: text in, findings out. Sections are located by the configured `##` heading
names, mapped in order onto tasks / definition of done / references / verify.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from booping.context._yaml import safe_load_str, split_frontmatter
from booping.plan.split import SECTION_KEYS, is_fence, split_lines

CHECKS: tuple[str, ...] = ("verify", "files", "dod", "sp")

CODE_SPAN = re.compile(r"`([^`\n]+)`")
LONE_CODE_SPAN = re.compile(r"`[^`]+`")
FILE_EXTENSION = re.compile(r"\.[A-Za-z0-9]+$")
CHECKBOX = re.compile(r"^\s*[-*+]\s+\[[ xX]\]")
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+\S")


@dataclass(frozen=True)
class Finding:
    check: str
    message: str


def _sections(body: str, names: Sequence[str]) -> dict[str, list[str]]:
    """Body lines under each configured `## {name}`, up to the next `##` heading
    outside a code fence."""
    keys = {name: key for name, key in zip(names, SECTION_KEYS, strict=True)}
    out: dict[str, list[str]] = {key: [] for key in SECTION_KEYS}
    current: str | None = None
    fence = False
    for line in split_lines(body):
        if is_fence(line):
            fence = not fence
        elif not fence and re.match(r"^#{1,2}\s", line):
            current = keys.get(line.lstrip("#").strip())
            continue
        if current is not None:
            out[current].append(line)
    return out


def _outside_fences(lines: Sequence[str]) -> list[str]:
    out: list[str] = []
    fence = False
    for line in lines:
        if is_fence(line):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return out


def _commands(lines: Sequence[str]) -> int:
    """Non-blank lines inside fenced blocks plus lines that are one inline code span."""
    count = 0
    fence = False
    for line in lines:
        if is_fence(line):
            fence = not fence
            continue
        text = line.strip()
        if not text:
            continue
        if fence or LONE_CODE_SPAN.fullmatch(text):
            count += 1
    return count


def _names_a_path(lines: Sequence[str]) -> bool:
    for line in _outside_fences(lines):
        for token in CODE_SPAN.findall(line):
            if "/" in token or FILE_EXTENSION.search(token.strip()):
                return True
    return False


def _tasks(lines: Sequence[str]) -> int:
    """Data rows of the first table whose header has a `Task` cell, else the
    top-level list items."""
    plain = _outside_fences(lines)
    for i, line in enumerate(plain):
        text = line.strip()
        if not text.startswith("|"):
            continue
        if i > 0 and plain[i - 1].strip().startswith("|"):
            continue
        cells = [c.strip().lower() for c in text.strip("|").split("|")]
        if "task" not in cells:
            continue
        rows = 0
        for row in plain[i + 1 :]:
            cell_text = row.strip()
            if not cell_text.startswith("|"):
                break
            if set(cell_text) <= set("|-: "):
                continue
            rows += 1
        return rows
    return sum(1 for line in plain if LIST_ITEM.match(line))


def check_milestone(
    text: str, sections: Sequence[str], redecompose_threshold: int
) -> list[Finding]:
    yaml_text, body = split_frontmatter(text)
    frontmatter = safe_load_str(yaml_text) if yaml_text is not None else {}
    parts = _sections(body, sections)
    findings: list[Finding] = []

    commands = _commands(parts["verify"])
    if commands != 1:
        findings.append(
            Finding("verify", f"Verify holds {commands} commands, expected exactly one")
        )

    if not _names_a_path(parts["tasks"]):
        findings.append(Finding("files", "Tasks names no file path"))

    tasks = _tasks(parts["tasks"])
    checkboxes = sum(1 for line in _outside_fences(parts["dod"]) if CHECKBOX.match(line))
    if tasks == 0:
        findings.append(Finding("dod", "Tasks holds no task"))
    elif checkboxes < tasks:
        findings.append(Finding("dod", f"{checkboxes} DoD checkboxes for {tasks} tasks"))

    sp = frontmatter.get("sp")
    if not isinstance(sp, int) or isinstance(sp, bool):
        findings.append(Finding("sp", "sp is not set"))
    elif sp >= redecompose_threshold:
        findings.append(
            Finding(
                "sp", f"sp {sp} is at or above the re-decompose threshold {redecompose_threshold}"
            )
        )
    return findings
