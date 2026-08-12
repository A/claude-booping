#!/usr/bin/env python3
"""Contract corpus runner — see README.md, which is the specification.

Runs each `cases/**/*.txtar` case in a fresh sandbox against the repository's
`bin/booping`, compares the normalized output against the case's assertions, and
reports pass/fail. `--update` rewrites the assertions from the actual run.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import _txtar

E2E_DIR = Path(__file__).resolve().parent
CASES_DIR = E2E_DIR / "cases"
BOOPING = E2E_DIR.parent.parent / "bin" / "booping"

ROOTS = ("home", "xdg", "cwd")
TOKENS = {"cwd": "{CWD}", "home": "{HOME}", "xdg": "{XDG}"}
WILDCARD = "[..]"


class CaseError(Exception):
    """A malformed case file: the run aborts with exit 2."""


@dataclass
class Case:
    path: Path
    name: str
    archive: _txtar.Archive
    cmd: list[str]
    exit_code: int = 0
    stdout: str | None = None
    stderr: str | None = None
    fixtures: list[tuple[str, str]] = field(default_factory=list)
    expected: list[tuple[str, str]] = field(default_factory=list)


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


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_case(path: Path) -> Case:
    try:
        archive = _txtar.parse(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CaseError(str(exc)) from exc

    case = Case(path=path, name=case_name(path), archive=archive, cmd=[])
    seen_cmd = False
    for name, data in archive.files:
        if name == "cmd":
            case.cmd = [line for line in data.splitlines() if line.strip()]
            seen_cmd = True
        elif name == "exit":
            case.exit_code = parse_exit(data)
        elif name == "stdout":
            case.stdout = data
        elif name == "stderr":
            case.stderr = data
        elif name.startswith("fixtures/"):
            case.fixtures.append((check_tree_path(name), data))
        elif name.startswith("expected/"):
            case.expected.append((check_tree_path(name), data))
        else:
            raise CaseError(f"unknown section: {name}")

    if not seen_cmd:
        raise CaseError("missing section: cmd")
    if not case.cmd:
        raise CaseError("empty section: cmd")
    return case


def case_name(path: Path) -> str:
    return path.relative_to(CASES_DIR).as_posix()


def parse_exit(data: str) -> int:
    text = data.strip()
    try:
        return int(text)
    except ValueError as exc:
        raise CaseError(f"exit is not an integer: {text!r}") from exc


def check_tree_path(name: str) -> str:
    prefix, _, rest = name.partition("/")
    root, _, relative = rest.partition("/")
    if root not in ROOTS or not relative:
        raise CaseError(f"{prefix}/ path must start with home/, xdg/ or cwd/: {name}")
    if ".." in Path(relative).parts or Path(relative).is_absolute():
        raise CaseError(f"{prefix}/ path escapes its root: {name}")
    return name


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_case(case: Case) -> Outcome:
    sandbox = Path(tempfile.mkdtemp(prefix="booping-e2e-"))
    try:
        return execute(case, sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def execute(case: Case, sandbox: Path) -> Outcome:
    roots = {root: sandbox / root for root in ROOTS}
    for directory in roots.values():
        directory.mkdir()

    for name, data in case.fixtures:
        target = tree_target(roots, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8")

    env = dict(os.environ)
    env["HOME"] = str(roots["home"])
    env["XDG_CONFIG_HOME"] = str(roots["xdg"])

    out_parts: list[str] = []
    err_parts: list[str] = []
    exit_code = 0
    early_exit: tuple[str, int] | None = None
    for index, line in enumerate(case.cmd):
        argv = shlex.split(line)
        if argv and argv[0] == "booping":
            argv[0] = str(BOOPING)
        completed = subprocess.run(
            argv,
            cwd=roots["cwd"],
            env=env,
            capture_output=True,
            text=True,
        )
        out_parts.append(completed.stdout)
        err_parts.append(completed.stderr)
        exit_code = completed.returncode
        if index < len(case.cmd) - 1 and exit_code != 0:
            early_exit = (line, exit_code)
            break

    files = {name: read_optional(tree_target(roots, name)) for name, _ in case.expected}
    normalize = normalizer(roots)
    return Outcome(
        stdout=normalize("".join(out_parts)),
        stderr=normalize("".join(err_parts)),
        exit_code=exit_code,
        files={name: None if body is None else normalize(body) for name, body in files.items()},
        early_exit=early_exit,
    )


def tree_target(roots: dict[str, Path], name: str) -> Path:
    _, _, rest = name.partition("/")
    root, _, relative = rest.partition("/")
    return roots[root] / relative


def read_optional(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.is_file() else None


def normalizer(roots: dict[str, Path]) -> Callable[[str], str]:
    replacements: list[tuple[str, str]] = []
    for root, directory in roots.items():
        for form in (directory, directory.resolve()):
            replacements.append((str(form), TOKENS[root]))
    # Longest first so a nested root can never be shadowed by its parent.
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)

    def normalize(text: str) -> str:
        for literal, token in replacements:
            text = text.replace(literal, token)
        return text

    return normalize


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

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
        mismatches.append(
            Mismatch("cmd", f"{line} exits 0\n", f"{line} exits {code}\n")
        )
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


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def updated_archive(case: Case, outcome: Outcome) -> _txtar.Archive:
    """The case with its assertions taken from the run; `cmd` and `fixtures/` kept.

    Sections already present keep their position; new ones are appended, so a
    second update over the same run is byte-identical.
    """
    fresh: dict[str, str] = {"exit": f"{outcome.exit_code}\n", "stdout": outcome.stdout}
    if outcome.stderr or case.stderr is not None:
        fresh["stderr"] = outcome.stderr
    for name, previous in case.expected:
        actual = outcome.files[name]
        fresh[name] = previous if actual is None else actual

    files: list[tuple[str, str]] = []
    for name, data in case.archive.files:
        files.append((name, fresh.pop(name, data)))
    files.extend(fresh.items())
    return _txtar.Archive(comment=case.archive.comment, files=files)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def select(patterns: list[str]) -> list[Path]:
    cases = sorted(CASES_DIR.rglob("*.txtar"))
    if not patterns:
        return cases
    selected: list[Path] = []
    for pattern in patterns:
        matched = [path for path in cases if pattern in case_name(path)]
        if not matched:
            print(f"no case matched pattern: {pattern}", file=sys.stderr)
            sys.exit(2)
        selected.extend(path for path in matched if path not in selected)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the booping contract corpus.")
    parser.add_argument(
        "--update",
        action="store_true",
        help="Rewrite the selected cases' assertions from the actual run",
    )
    parser.add_argument(
        "patterns",
        nargs="*",
        metavar="pattern",
        help="Substring matched against a case path relative to cases/",
    )
    args = parser.parse_args()

    cases: list[Case] = []
    for path in select(args.patterns):
        try:
            cases.append(load_case(path))
        except CaseError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            return 2

    if args.update:
        for case in cases:
            outcome = run_case(case)
            text = _txtar.serialize(updated_archive(case, outcome))
            if text != case.path.read_text(encoding="utf-8"):
                case.path.write_text(text, encoding="utf-8")
                print(f"updated {case.name}")
        return 0

    failed = 0
    for case in cases:
        mismatches = compare(case, run_case(case))
        if not mismatches:
            print(f"PASS {case.name}")
            continue
        failed += 1
        print(f"FAIL {case.name}")
        for mismatch in mismatches:
            print(report(mismatch))
    print(f"{len(cases) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
