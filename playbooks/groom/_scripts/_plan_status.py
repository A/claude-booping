#!/usr/bin/env python3
"""Shared implementation for the plan-<status> hook scripts.

Invoked with the target lifecycle status as argv[1]. Environment (set by
`booping playbook-transition`): BOOPING_WORKDIR = {vault}/plans/{slug}.

Stamps `plan_status:` on the run's `index.md` (the run machine owns `status:`,
so the lifecycle mirror lives under its own key) and commits it. Self-contained:
the vault carries no `.booping` marker, so nothing here shells back into
`booping`, and nothing outside the standard library is imported.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def stamp_status(plan: Path, status: str) -> None:
    text = plan.read_text()
    if not text.startswith("---\n"):
        sys.exit(f"plan has no frontmatter: {plan}")
    head, sep, body = text.partition("\n---\n")
    if re.search(r"^plan_status:.*$", head, re.MULTILINE):
        head = re.sub(
            r"^plan_status:.*$", f"plan_status: {status}", head, count=1, flags=re.MULTILINE
        )
    else:
        head += f"\nplan_status: {status}"
    plan.write_text(head + sep + body)


def main() -> None:
    status = sys.argv[1]
    workdir = Path(os.environ.get("BOOPING_WORKDIR", ".")).resolve()
    slug = workdir.name
    vault = workdir.parent.parent
    plan = workdir / "index.md"
    if not plan.is_file():
        sys.exit(f"plan not found: {plan}")

    stamp_status(plan, status)
    print(f"plan-status: plans/{slug}/index.md → {status}")

    if (vault / ".git").exists():
        subprocess.run(
            ["git", "-C", str(vault), "add", f"plans/{slug}/index.md"], check=True
        )
        result = subprocess.run(
            ["git", "-C", str(vault), "commit", "-q", "-m", f"groom: {slug} → {status}"],
        )
        print("vault-commit: ok" if result.returncode == 0 else "vault-commit: nothing to commit")


if __name__ == "__main__":
    main()
