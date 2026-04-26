# Development quality checks

How the orchestrator handles per-project quality tooling (lint, typecheck, formatter, tests) during a sprint. Distinct from each milestone's plan-authored `Verify` command — that one targets the milestone's own DoD; this one covers whatever the project itself already enforces on its code.

## Detect

At Phase 0, inspect the attached repo to classify quality tooling into two buckets:

- **Hook-enforced (automatic)** — tools wired to run on commit/push via `.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`, `.git/hooks/`, or a CI gate that blocks merges. These fire naturally when the skill commits in Phase 3 — do NOT re-run them manually.
- **Configured but manual** — tools installed and configured in the repo but not wired to a hook. Typical signals: `package.json` scripts, `pyproject.toml` / `ruff.toml` / `pyright` config, `Justfile` / `Makefile` targets, `.eslintrc`, `tsconfig.json`, `cargo.toml` dev-dependencies, etc.

If the repo `CLAUDE.md` names the canonical commands for either bucket, trust it and skip discovery.

## Decide

Produce one list of manual quality commands to run per milestone. Hook-enforced tools are excluded from that list — they fire at commit time on their own. If the project has no configured quality tooling at all, note it in the Phase 1 scope summary and fall back to the plan's own Verify command alone.

## Run

Execute the decided manual commands after the milestone's plan-authored Verify command. A failure here blocks the commit the same way a plan-Verify failure does — delegate the fix to a worker agent, do not patch in the orchestrator.

## Project-local override

If `~/Claude/{project}/_booping/skill_develop.md` (or an equivalent extension) lists explicit quality commands, use those verbatim and skip detection.
