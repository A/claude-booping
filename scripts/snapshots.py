#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Playbook report snapshots: render, check for drift, accept a new baseline.

render: --fixture renders against playbooks/_fixtures/vault (hermetic, the vault's own
config declares `macro_stubs:`) into <dest>/<name>/_reports/output.md and fails on a STOP
notice; without it, the attached project's own vault with macros executed for real into
<dest>/<name>/_reports/local.md (gitignored), where STOP notices print rather than fail.
A trailing argument narrows to one playbook; --dest <dir> moves the destination root
(default `playbooks`).

Project-local playbooks — `{vault}/_playbooks/<name>/` of this repo's own vault — join the
--fixture set when they commit a `_reports/output.md` (opt-in: a local playbook without one
is not snapshotted). The fixture vault cannot discover them, so they render against a temp
copy of the repo vault's non-ignored files, made hermetic: a marker at the latest shipped
migration (the repo's own watermark may lag) and the fixture vault's `macro_stubs:`. Under
the default destination their reports land back beside them; under --dest, as
<dest>/<name>/ like the core ones (playbook names are unique across roots).

check: writes nothing under playbooks/ — renders into a temp dir, then diffs against the
baselines.

accept: takes the fresh render as the new baseline, rewriting the committed reports.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = "playbooks"
FIXTURE = "playbooks/_fixtures/vault"
REPORT = "_reports/output.md"
_MIGRATION_ID = re.compile(r"^id:\s*(\d+)\s*$", re.MULTILINE)

# `uv run` exports VIRTUAL_ENV for this script's own env; leaving it set makes the nested
# `uv run --project booping-python` inside bin/booping warn on every invocation.
CHILD_ENV = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}


@dataclass(frozen=True)
class Target:
    name: str
    # Repo-relative directory the committed report sits under: playbooks/<name> or
    # {vault}/_playbooks/<name>.
    home: str
    local: bool


def repo_vault() -> str:
    # The marker is per checkout and git-ignored (absent in CI): fall back to the in-repo vault.
    path = ROOT / ".booping"
    marker = (yaml.safe_load(path.read_text()) or {}) if path.is_file() else {}
    return str(marker.get("vault_path") or "vault")


def local_targets(target: str) -> list[Target]:
    vault = repo_vault()
    return [
        Target(report.parent.parent.name, f"{vault}/_playbooks/{report.parent.parent.name}", True)
        for report in sorted(ROOT.glob(f"{vault}/_playbooks/{target}/{REPORT}"))
        if (report.parent.parent / "playbook.md").is_file()
    ]


def targets(target: str, fixture: bool) -> list[Target]:
    core = [
        Target(m.parent.name, f"playbooks/{m.parent.name}", False)
        for m in sorted(ROOT.glob(f"playbooks/{target}/playbook.md"))
    ]
    local = local_targets(target) if fixture else []
    # Mirrors the shell glob: an unmatched pattern stays literal and fails downstream.
    return core + local or [Target(target, f"playbooks/{target}", False)]


def latest_migration() -> int:
    ids = [
        int(m.group(1))
        for path in ROOT.glob("migrations/*/migration.md")
        if (m := _MIGRATION_ID.search(path.read_text()))
    ]
    return max(ids, default=0)


def hermetic_vault(dest: Path) -> Path:
    """A copy of the repo vault's non-ignored files, current on migrations and stub-pinned."""
    vault = repo_vault()
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", vault],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for rel in filter(None, listed.split("\0")):
        source = ROOT / rel
        if not source.is_file():
            continue
        copy = dest / Path(rel).relative_to(vault)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, copy)
    marker_path = ROOT / ".booping"
    marker = (yaml.safe_load(marker_path.read_text()) or {}) if marker_path.is_file() else {}
    (dest / ".booping").write_text(
        yaml.safe_dump(
            {"project_name": marker.get("project_name") or ROOT.name, "latest_migration": latest_migration()}
        )
    )
    config_path = dest / "config.yaml"
    config = (yaml.safe_load(config_path.read_text()) if config_path.is_file() else None) or {}
    stubs = (yaml.safe_load((ROOT / FIXTURE / "config.yaml").read_text()) or {}).get(
        "macro_stubs", {}
    )
    config["macro_stubs"] = {**config.get("macro_stubs", {}), **stubs}
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
    return dest


def out_rel(dest: str, item: Target, fixture: bool) -> str:
    base = item.home if dest == DEFAULT_DEST else f"{dest}/{item.name}"
    return f"{base}/_reports/{'output.md' if fixture else 'local.md'}"


def render(fixture: bool, dest: str, target: str, quiet: bool = False) -> int:
    out_sink = subprocess.DEVNULL if quiet else None
    failed: list[str] = []
    items = targets(target, fixture)
    with tempfile.TemporaryDirectory() as scratch:
        local_vault = (
            hermetic_vault(Path(scratch) / "vault") if any(i.local for i in items) else None
        )
        for item in items:
            code = _render_one(item, fixture, dest, local_vault, out_sink, quiet, failed)
            if code:
                return code
    for name in failed:
        print(f"STOP notice in report: {name}", file=sys.stderr)
    return 1 if failed else 0


def _render_one(
    item: Target,
    fixture: bool,
    dest: str,
    local_vault: Path | None,
    out_sink: int | None,
    quiet: bool,
    failed: list[str],
) -> int:
    name = item.name
    rel_out = out_rel(dest, item, fixture)
    abs_out = Path(rel_out)
    if not abs_out.is_absolute():
        abs_out = ROOT / rel_out
    abs_out.parent.mkdir(parents=True, exist_ok=True)
    if not quiet:
        print(rel_out)
    argv = ["bin/booping", "render-playbook", name]
    if fixture:
        argv += ["--project", str(local_vault) if item.local else FIXTURE]
    argv += ["--output", rel_out]
    code = subprocess.call(argv, cwd=ROOT, stdout=out_sink, env=CHILD_ENV)
    if code:
        return code
    stops = [line for line in abs_out.read_text().splitlines() if line.startswith("**STOP")]
    if fixture:
        if stops:
            failed.append(name)
    elif not quiet:
        for line in stops:
            print(line)
    return 0


def check() -> int:
    tmp = tempfile.mkdtemp()
    try:
        code = render(fixture=True, dest=tmp, target="*", quiet=True)
        if code:
            return code
        drifted: list[str] = []
        homes = {item.name: item.home for item in targets("*", fixture=True)}
        for rendered in sorted(Path(tmp).glob(f"*/{REPORT}")):
            name = rendered.parent.parent.name
            committed = f"{homes.get(name, f'playbooks/{name}')}/{REPORT}"
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
        return render(fixture=True, dest=DEFAULT_DEST, target=rest[0] if rest else "*")
    if mode == "render":
        fixture = False
        dest = DEFAULT_DEST
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
