"""The run outcome, its normalization, and how it is matched against a case."""

from __future__ import annotations

import difflib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from pytest_txtar.case import Case

WILDCARD = "[..]"


@dataclass
class Outcome:
    stdout: str
    stderr: str
    exit_code: int
    files: dict[str, str | None]
    early_exit: tuple[str, int] | None = None


@dataclass
class Mismatch:
    label: str
    expected: str
    actual: str


def normalizer(roots: Mapping[str, Path], tokens: Mapping[str, str]) -> Callable[[str], str]:
    replacements: list[tuple[str, str]] = []
    for root, directory in roots.items():
        for form in (directory, directory.resolve()):
            replacements.append((str(form), tokens[root]))
    # Longest first so a nested root can never be shadowed by its parent.
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)

    def normalize(text: str) -> str:
        for literal, token in replacements:
            text = text.replace(literal, token)
        return text

    return normalize


def lines_of(text: str) -> list[str]:
    if text.endswith("\n"):
        text = text[:-1]
    return text.split("\n") if text else []


def text_matches(expected: str, actual: str) -> bool:
    expected_lines = lines_of(expected)
    actual_lines = lines_of(actual)
    if len(expected_lines) != len(actual_lines):
        return False
    return all(
        line_matches(want, got) for want, got in zip(expected_lines, actual_lines, strict=True)
    )


def line_matches(expected: str, actual: str) -> bool:
    if WILDCARD not in expected:
        return expected == actual
    pattern = ".*?".join(re.escape(part) for part in expected.split(WILDCARD))
    return re.fullmatch(pattern, actual) is not None


def compare(case: Case, outcome: Outcome) -> list[Mismatch]:
    mismatches: list[Mismatch] = []
    if outcome.early_exit is not None:
        line, code = outcome.early_exit
        mismatches.append(Mismatch("cmd", f"{line} exits 0\n", f"{line} exits {code}\n"))
    if case.stdout is not None and not text_matches(case.stdout, outcome.stdout):
        mismatches.append(Mismatch("stdout", case.stdout, outcome.stdout))
    if case.stderr is not None and not text_matches(case.stderr, outcome.stderr):
        mismatches.append(Mismatch("stderr", case.stderr, outcome.stderr))
    if case.exit_code != outcome.exit_code:
        mismatches.append(Mismatch("exit", f"{case.exit_code}\n", f"{outcome.exit_code}\n"))
    for name, expected in case.expected:
        actual = outcome.files[name]
        if actual is None:
            mismatches.append(Mismatch(name, expected, "<file does not exist>\n"))
        elif not text_matches(expected, actual):
            mismatches.append(Mismatch(name, expected, actual))
    return mismatches


def report(mismatch: Mismatch) -> str:
    diff = difflib.unified_diff(
        lines_of(mismatch.expected),
        lines_of(mismatch.actual),
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )
    return f"=== {mismatch.label} ===\n" + "\n".join(diff)
