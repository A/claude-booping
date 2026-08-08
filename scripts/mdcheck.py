#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Structural checks over the rendered reports.

Shared rules run over every report; a playbook may add playbooks/<name>/_reports/rules.yaml
beside its report for its own sections and tables.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

findings: list[str] = []
errored: list[str] = []
seen_error: set[str] = set()


def run(rules: str, report: str) -> None:
    status = subprocess.call(["mdcheck", rules, report], cwd=ROOT)
    if status == 0:
        return
    if status == 1:
        findings.append(f"{report} ({rules})")
    elif rules not in seen_error:
        seen_error.add(rules)
        errored.append(f"{rules}: mdcheck exit {status}")


def main() -> int:
    if shutil.which("mdcheck") is None:
        print(
            "mdcheck: binary not found on PATH — cargo install markdown-checker",
            file=sys.stderr,
        )
        return 127
    for report in sorted(ROOT.glob("playbooks/*/_reports/output.md")):
        rel = str(report.relative_to(ROOT))
        run("playbooks/_lib/report.rules.yaml", rel)
        rules = report.parent / "rules.yaml"
        if rules.is_file():
            run(str(rules.relative_to(ROOT)), rel)
    for line in errored:
        print(f"mdcheck rule-file or internal error — {line}", file=sys.stderr)
    for line in findings:
        print(f"mdcheck findings: {line}", file=sys.stderr)
    if errored:
        return 2
    if findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
