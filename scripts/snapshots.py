#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Playbook report snapshots: render, check for drift, accept a new baseline.

render: --fixture renders against playbooks/_fixtures/vault (hermetic, the vault's own
config declares `macro_stubs:`) into <dest>/<name>/_reports/output.md and fails on a STOP
notice; without it, the attached project's own vault with macros executed for real into
<dest>/<name>/_reports/local.md (gitignored), where STOP notices print rather than fail.
A trailing argument narrows to one playbook; --dest <dir> moves the destination root
(default `playbooks`).

check: writes nothing under playbooks/ — renders into a temp dir, then diffs against the
baselines.

accept: takes the fresh render as the new baseline, rewriting the committed reports.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `uv run` exports VIRTUAL_ENV for this script's own env; leaving it set makes the nested
# `uv run --project booping-python` inside bin/booping warn on every invocation.
CHILD_ENV = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}


def manifests(target: str) -> list[Path]:
    matches = sorted(ROOT.glob(f"playbooks/{target}/playbook.md"))
    # Mirrors the shell glob: an unmatched pattern stays literal and fails downstream.
    return matches or [ROOT / "playbooks" / target / "playbook.md"]


def render(fixture: bool, dest: str, target: str, quiet: bool = False) -> int:
    out_sink = subprocess.DEVNULL if quiet else None
    failed: list[str] = []
    for manifest in manifests(target):
        name = manifest.parent.name
        rel_out = f"{dest}/{name}/_reports/{'output.md' if fixture else 'local.md'}"
        abs_out = Path(rel_out)
        if not abs_out.is_absolute():
            abs_out = ROOT / rel_out
        abs_out.parent.mkdir(parents=True, exist_ok=True)
        if not quiet:
            print(rel_out)
        argv = ["bin/booping", "render-playbook", name]
        if fixture:
            argv += ["--project", "playbooks/_fixtures/vault"]
        argv += ["--output", rel_out]
        code = subprocess.call(argv, cwd=ROOT, stdout=out_sink, env=CHILD_ENV)
        if code:
            return code
        stops = [
            line for line in abs_out.read_text().splitlines() if line.startswith("**STOP")
        ]
        if fixture:
            if stops:
                failed.append(name)
        elif not quiet:
            for line in stops:
                print(line)
    for name in failed:
        print(f"STOP notice in report: {name}", file=sys.stderr)
    return 1 if failed else 0


def check() -> int:
    tmp = tempfile.mkdtemp()
    try:
        code = render(fixture=True, dest=tmp, target="*", quiet=True)
        if code:
            return code
        drifted: list[str] = []
        for rendered in sorted(Path(tmp).glob("*/_reports/output.md")):
            name = rendered.parent.parent.name
            committed = f"playbooks/{name}/_reports/output.md"
            if not (ROOT / committed).is_file():
                print(f"missing snapshot: {committed}", file=sys.stderr)
                drifted.append(name)
                continue
            diff = subprocess.call(
                [
                    "diff",
                    "--color",
                    "-u",
                    "--label",
                    committed,
                    "--label",
                    f"{committed} (rendered)",
                    committed,
                    str(rendered),
                ],
                cwd=ROOT,
            )
            if diff:
                drifted.append(name)
        if drifted:
            print(f"snapshot drift: {' '.join(drifted)}", file=sys.stderr)
            print(
                "run 'just snapshots-accept' to take the rendered output as the baseline",
                file=sys.stderr,
            )
            return 1
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: snapshots.py {render|check|accept} [args…]", file=sys.stderr)
        return 2
    mode, rest = argv[0], argv[1:]
    if mode == "check":
        return check()
    if mode == "accept":
        return render(fixture=True, dest="playbooks", target=rest[0] if rest else "*")
    if mode == "render":
        fixture = False
        dest = "playbooks"
        target = "*"
        i = 0
        while i < len(rest):
            arg = rest[i]
            if arg == "--fixture":
                fixture = True
            elif arg == "--dest":
                i += 1
                dest = rest[i]
            elif arg.startswith("--dest="):
                dest = arg[len("--dest=") :]
            else:
                target = arg
            i += 1
        return render(fixture=fixture, dest=dest, target=target)
    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
