#!/usr/bin/env python3
"""Shared implementation for the plan-<status> hook scripts.

Invoked with the target lifecycle status as argv[1]. Environment (set by
`booping playbook-transition`): BOOPING_WORKDIR = {vault}/_runs/groom/{slug}.

Stamps `status:` on the run's plan, re-renders the vault's sprints.md from
plan frontmatter, and commits both. Self-contained: the vault may have no
repo checkout nearby, so nothing here shells back into `booping`.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip("\"'")
    return fm


def stamp_status(plan: Path, status: str) -> None:
    text = plan.read_text()
    if not text.startswith("---\n"):
        sys.exit(f"plan has no frontmatter: {plan}")
    head, sep, body = text.partition("\n---\n")
    if re.search(r"^status:.*$", head, re.MULTILINE):
        head = re.sub(r"^status:.*$", f"status: {status}", head, count=1, flags=re.MULTILINE)
    else:
        head += f"\nstatus: {status}"
    plan.write_text(head + sep + body)


def render_sprints(vault: Path) -> int:
    rows = []
    for path in sorted(vault.glob("plans/*.md")):
        fm = read_frontmatter(path)
        rows.append((path.stem, fm.get("title", path.stem), fm.get("type", ""), fm.get("status", ""), fm.get("sp", "")))
    lines = [
        "# Sprints",
        "",
        "| Plan | Title | Type | Status | SP |",
        "| --- | --- | --- | --- | --- |",
    ]
    for stem, title, type_, status, sp in rows:
        lines.append(f"| [[plans/{stem}]] | {title} | {type_} | {status} | {sp} |")
    (vault / "sprints.md").write_text("\n".join(lines) + "\n")
    return len(rows)


def main() -> None:
    status = sys.argv[1]
    workdir = Path(os.environ.get("BOOPING_WORKDIR", ".")).resolve()
    slug = workdir.name
    vault = workdir.parent.parent.parent
    plan = vault / "plans" / f"{slug}.md"
    if not plan.is_file():
        sys.exit(f"plan not found: {plan}")

    stamp_status(plan, status)
    count = render_sprints(vault)
    print(f"plan-status: {plan.name} → {status}; sprints.md: {count} plans")

    if (vault / ".git").exists():
        subprocess.run(["git", "-C", str(vault), "add", f"plans/{plan.name}", "sprints.md"], check=True)
        result = subprocess.run(
            ["git", "-C", str(vault), "commit", "-q", "-m", f"groom: {slug} → {status}"],
        )
        print("vault-commit: ok" if result.returncode == 0 else "vault-commit: nothing to commit")


if __name__ == "__main__":
    main()
