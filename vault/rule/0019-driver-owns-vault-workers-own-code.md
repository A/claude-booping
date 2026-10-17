---
type: rule
title: The driver owns the vault and git; workers touch only repo code
summary: The driver owns the vault, run state and commits; workers edit only repo code, never git history; a small fix goes to the session already holding its context.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
sources: [CLAUDE.md, docs/development_quality_checks.md]
---

## Rule

The driver of a playbook run owns every vault read and write, the run state and the
repo commits. A worker agent, of any harness, touches only the repo's code — or, after the user explicitly confirms it for the
plan, code outside the repo ([adr/0012](../adr/0012-driver-owns-the-vault.md)): it runs
its milestone's Verify and leaves the work uncommitted, never touching git history.
The other way round, the driver does not patch code itself — a failing check is
handed to a worker to fix.

## Follows from

- [adr/0012](../adr/0012-driver-owns-the-vault.md) — the driver does every vault read and write; workers touch only repo code.
- [adr/0013](../adr/0013-runner-owns-the-commit.md) — the runner validates the tree against the DoD and makes the commit; workers never commit.
- [value/0002](../value/0002-minimal-effective-context.md) — a worker gets only what it needs.
- [value/0003](../value/0003-single-source.md) — each fact, decision and piece of structured data lives in one place and is referenced or rendered from there.
- [Development quality checks](../../docs/development_quality_checks.md) — a
  quality failure is delegated to a worker, not patched in the orchestrator.

## Exceptions

A small fix goes to the session that already holds its whole context instead of a fresh worker: at most `core.sprint.inline_fix_sp` SP on the sprint scale (`core.sprint.scale`), every file it touches already read in that session, nothing left to find out — no file still to read, no research, no open question (owner, 2026-10-17). Anything larger, or with an unknown, goes to a worker.

- **develop** — the driver applies such a fix itself.
- **code-review** — a finding accepted at the verdict is applied by the reviewer that found it, resumed by its id, never respawned; when it cannot be resumed, the fix goes to a worker, not to the driver. Accepted at the verdict means by the user in a supervised run, or settled by the driver in an autonomous one and logged to `defaults.md`.
- **project-manager** — no exception: its driver delegates every code change, keeping its long-lived context clean.

In an autonomous run, the driver commits such fixes separately from the workers' work, and they pass the same check as a worker's fix; a red check reverts the fix and hands it to a worker.
