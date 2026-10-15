---
type: rule
title: The driver owns the vault and git; workers touch only repo code
summary: The playbook driver does every vault read and write and every commit; a worker agent edits only repo code, never git history, and the driver delegates code fixes instead of patching.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
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

- [CLAUDE.md, Principles and Lifecycle](../../CLAUDE.md) — the source states the split without
  naming a reason.
- [Development quality checks](../../docs/development_quality_checks.md) — a
  quality failure is delegated to a worker, not patched in the orchestrator.
