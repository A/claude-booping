"""Standalone e2e contract-corpus runner — executes txtar cases against bin/booping."""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Support `python e2e/run.py` invocation (e2e/ is not on sys.path by default)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from e2e._txtar import Archive, parse, serialize

E2E_DIR = Path(__file__).resolve().parent
CASES_DIR = E2E_DIR / "cases"
PLUGIN_ROOT = E2E_DIR.parents[1]
BOOPING_BIN = PLUGIN_ROOT / "bin" / "booping"

VALID_SECTIONS = {"cmd", "exit", "stdout", "stderr"}
VALID_PREFIXES = ("fixtures/", "expected/")


def _valid_section(name: str) -> bool:
    if name in VALID_SECTIONS:
        return True
    return name.startswith("fixtures/") or name.startswith("expected/")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="E2E contract corpus runner")
    ap.add_argument(
        "--update", action="store_true",
        help="Rewrite expected sections from actual output",
    )
    ap.add_argument(
        "patterns", nargs="*",
        help="Substring filters on case paths (relative to cases/)",
    )
    return ap.parse_args(argv)


def discover(patterns: list[str]) -> list[Path]:
    """Find .txtar files matching all substring patterns (relative to cases/)."""
    if not CASES_DIR.exists():
        return []
    matches: list[Path] = []
    for case_path in sorted(CASES_DIR.rglob("*.txtar")):
        rel = case_path.relative_to(CASES_DIR).as_posix()
        if all(pat in rel for pat in patterns):
            matches.append(case_path)
    return matches


def build_sandbox(case_dir: Path, archive: Archive) -> dict[str, Path]:
    """Create tmp sandbox, materialize fixtures, return directory mapping."""
    sandbox = Path(tempfile.mkdtemp())
    dirs: dict[str, Path] = {
        "home": sandbox / "home",
        "xdg": sandbox / "xdg",
        "cwd": sandbox / "cwd",
    }
    for d in dirs.values():
        d.mkdir()

    for name, content in archive.files:
        if not name.startswith("fixtures/"):
            continue
        rel = name[len("fixtures/"):]
        prefix = rel.split("/", 1)[0]
        if prefix not in ("home", "xdg", "cwd"):
            continue
        file_path = dirs[prefix] / rel[len(prefix) + 1:]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    return dirs


def resolve_cmd(line: str) -> list[str]:
    """Resolve 'booping' to the repo-absolute bin/booping path."""
    parts = line.split()
    if parts and parts[0] == "booping":
        parts[0] = str(BOOPING_BIN)
    return parts


def run_commands(
    cmds: list[str], env: dict[str, str], cwd: Path,
) -> list[tuple[int, str, str]]:
    """Execute each command line, return list of (exit_code, stdout, stderr)."""
    results: list[tuple[int, str, str]] = []
    for line in cmds:
        if not line.strip():
            continue
        argv = resolve_cmd(line)
        cp = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd)
        results.append((cp.returncode, cp.stdout, cp.stderr))
    return results


def normalize(output: str, cwd: Path, home: Path, xdg: Path) -> str:
    """Replace sandbox paths with tokens, longest first to avoid partial matches."""
    replacements = sorted(
        [(str(cwd), "{CWD}"), (str(home), "{HOME}"), (str(xdg), "{XDG}")],
        key=lambda x: len(x[0]),
        reverse=True,
    )
    for old, new in replacements:
        output = output.replace(old, new)
    return output


def lines_match(expected_line: str, actual_line: str) -> bool:
    """Compare a single line, supporting [..] as inline wildcard."""
    if "[..]" not in expected_line:
        return expected_line == actual_line
    parts = expected_line.split("[..]")
    pattern = ".*?".join(re.escape(p) for p in parts)
    return re.fullmatch(pattern, actual_line) is not None


def compare_text(label: str, expected: str, actual: str) -> list[str]:
    """Return labeled unified diff if texts differ, else empty list."""
    if expected == actual:
        return []

    exp_bare = expected.splitlines() if expected else []
    act_bare = actual.splitlines() if actual else []

    diff_lines = list(
        difflib.unified_diff(exp_bare, act_bare, fromfile="expected", tofile="actual", lineterm="")
    )
    if not diff_lines:
        return []

    output: list[str] = [f"--- {label} mismatch ---"]
    output.extend(diff_lines)
    output.append("")
    return output


def get_section(archive: Archive, name: str) -> str | None:
    for n, content in archive.files:
        if n == name:
            return content
    return None


def _line_compare(expected_lines: list[str], actual_lines: list[str]) -> bool:
    if len(expected_lines) != len(actual_lines):
        return False
    for exp, act in zip(expected_lines, actual_lines):
        if not lines_match(exp, act):
            return False
    return True


class CaseResult:
    """Result of running a single case."""

    def __init__(self) -> None:
        self.pass_ = False
        self.issues: list[str] = []
        self.actual: dict[str, str] = {}
        self.expected_files: list[tuple[str, str]] = []
        self.error: str | None = None


def run_case(case_path: Path, dirs: dict[str, Path]) -> CaseResult:
    result = CaseResult()
    raw = case_path.read_text()
    archive = parse(raw)

    # Validate sections
    for name, _ in archive.files:
        if not _valid_section(name):
            result.error = f"unknown section: {name!r}"
            return result

    cmd_content = get_section(archive, "cmd")
    if cmd_content is None:
        result.error = "missing required section: 'cmd'"
        return result

    cmd_lines = [line for line in cmd_content.splitlines() if line.strip()]
    if not cmd_lines:
        result.error = "cmd section is empty"
        return result

    # Run commands
    env = dict(os.environ)
    env["HOME"] = str(dirs["home"])
    env["XDG_CONFIG_HOME"] = str(dirs["xdg"])

    results = run_commands(cmd_lines, env, dirs["cwd"])

    actual_stdout = ""
    actual_stderr = ""
    for exit_code, stdout, stderr in results:
        actual_stdout += stdout
        actual_stderr += stderr

    last_exit = results[-1][0] if results else 0
    result.actual = {
        "exit": str(last_exit),
        "stdout": normalize(actual_stdout, dirs["cwd"], dirs["home"], dirs["xdg"]),
        "stderr": normalize(actual_stderr, dirs["cwd"], dirs["home"], dirs["xdg"]),
    }

    # Multi-command semantics: non-final lines must exit 0
    for i, (exit_code, _, _) in enumerate(results):
        if i < len(results) - 1 and exit_code != 0:
            result.error = (
                f"cmd line {i + 1} exited {exit_code}"
                " (non-final commands must exit 0)"
            )
            return result

    # Compare against expected
    issues: list[str] = []

    # Exit code
    expected_exit = get_section(archive, "exit")
    if expected_exit is not None:
        expected_exit = expected_exit.strip()
        if result.actual["exit"] != expected_exit:
            issues.extend(compare_text("exit", expected_exit + "\n", result.actual["exit"] + "\n"))

    # Stdout
    expected_stdout = get_section(archive, "stdout")
    if expected_stdout is not None:
        exp_lines = expected_stdout.rstrip("\n").splitlines() if expected_stdout.strip() else []
        act_stdout = result.actual["stdout"]
        act_lines = act_stdout.rstrip("\n").splitlines() if act_stdout.strip() else []
        if not _line_compare(exp_lines, act_lines):
            issues.extend(compare_text("stdout", expected_stdout, act_stdout))

    # Stderr
    expected_stderr = get_section(archive, "stderr")
    if expected_stderr is not None:
        exp_lines = expected_stderr.rstrip("\n").splitlines() if expected_stderr.strip() else []
        act_stderr = result.actual["stderr"]
        act_lines = act_stderr.rstrip("\n").splitlines() if act_stderr.strip() else []
        if not _line_compare(exp_lines, act_lines):
            issues.extend(compare_text("stderr", expected_stderr, act_stderr))

    # Expected files
    exp_file_sections: list[tuple[str, str]] = []
    for sec_name, expected_content in archive.files:
        if not sec_name.startswith("expected/"):
            continue
        exp_file_sections.append((sec_name, expected_content))

    for sec_name, expected_content in exp_file_sections:
        rel = sec_name[len("expected/"):]
        prefix = rel.split("/", 1)[0]
        if prefix not in ("home", "xdg", "cwd"):
            continue
        file_path = dirs[prefix] / rel[len(prefix) + 1:]
        if not file_path.exists():
            issues.append(f"--- expected file missing: {sec_name} ---")
            issues.append("")
            continue

        actual_content = file_path.read_text()
        actual_normalized = normalize(actual_content, dirs["cwd"], dirs["home"], dirs["xdg"])

        exp_lines = expected_content.rstrip("\n").splitlines() if expected_content.strip() else []
        act_lines = actual_normalized.rstrip("\n").splitlines() if actual_normalized.strip() else []

        if not _line_compare(exp_lines, act_lines):
            issues.extend(compare_text(f"expected/{rel}", expected_content, actual_normalized))

    result.pass_ = len(issues) == 0
    result.issues = issues
    result.expected_files = exp_file_sections
    return result


def update_case(
    case_path: Path,
    archive: Archive,
    dirs: dict[str, Path],
    result: CaseResult,
) -> str:
    """Rewrite expected sections from actual normalized output, return new text."""
    actual = result.actual
    new_files: list[tuple[str, str]] = []

    for name, content in archive.files:
        if name == "stdout":
            new_files.append(("stdout", actual["stdout"]))
        elif name == "stderr":
            new_files.append(("stderr", actual["stderr"]))
        elif name == "exit":
            new_files.append(("exit", actual["exit"]))
        elif name.startswith("expected/"):
            rel = name[len("expected/"):]
            prefix = rel.split("/", 1)[0]
            if prefix not in ("home", "xdg", "cwd"):
                new_files.append((name, content))
                continue
            file_path = dirs[prefix] / rel[len(prefix) + 1:]
            if file_path.exists():
                actual_content = normalize(
                    file_path.read_text(), dirs["cwd"], dirs["home"], dirs["xdg"],
                )
                new_files.append((name, actual_content))
            else:
                new_files.append((name, content))
        else:
            new_files.append((name, content))

    existing_names = {n for n, _ in new_files}
    if "exit" not in existing_names:
        new_files.append(("exit", actual["exit"]))
    if "stdout" not in existing_names:
        new_files.append(("stdout", actual["stdout"]))
    if "stderr" not in existing_names:
        new_files.append(("stderr", actual["stderr"]))

    # Write expected files that didn't exist
    for sec_name, _ in result.expected_files:
        if sec_name not in existing_names:
            rel = sec_name[len("expected/"):]
            prefix = rel.split("/", 1)[0]
            file_path = dirs[prefix] / rel[len(prefix) + 1:]
            if file_path.exists():
                actual_content = normalize(
                    file_path.read_text(), dirs["cwd"], dirs["home"], dirs["xdg"],
                )
                new_files.append((sec_name, actual_content))

    updated = Archive(comment=archive.comment, files=new_files)
    return serialize(updated)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cases = discover(args.patterns if args.patterns else [])

    if args.patterns and not cases:
        pat = " ".join(args.patterns)
        print(f"No cases matched pattern: {pat}", file=sys.stderr)
        return 2

    passed = 0
    failed = 0
    had_malformed = False

    for case_path in cases:
        rel = case_path.relative_to(CASES_DIR).as_posix()

        try:
            archive = parse(case_path.read_text())
        except Exception as e:
            print(f"FAIL {rel}")
            print(f"  malformed: {e}", file=sys.stderr)
            failed += 1
            had_malformed = True
            continue

        dirs = build_sandbox(case_path.parent, archive)
        try:
            result = run_case(case_path, dirs)

            if result.error is not None:
                print(f"FAIL {rel}")
                print(f"  {result.error}", file=sys.stderr)
                failed += 1
                had_malformed = True
                continue

            if args.update:
                updated = update_case(case_path, archive, dirs, result)
                case_path.write_text(updated)
                print(f"updated {rel}")
                passed += 1
                continue

            if result.pass_:
                print(f"PASS {rel}")
                passed += 1
            else:
                print(f"FAIL {rel}")
                for issue_text in result.issues:
                    print(f"  {issue_text}")
                failed += 1
        finally:
            shutil.rmtree(dirs["home"].parent, ignore_errors=True)

    print(f"{passed} passed, {failed} failed")

    if had_malformed:
        return 2
    if failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
