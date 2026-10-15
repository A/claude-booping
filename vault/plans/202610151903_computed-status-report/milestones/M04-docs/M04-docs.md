---
id: "04"
title: "CLAUDE.md and documentation on booping status"
sp: 2
status: in-progress
plan: "plans/202610151903_computed-status-report/index.md"
---

# M04: CLAUDE.md and documentation on booping status

A reader of `CLAUDE.md` or the docs site finds `booping status` and `core.status`.

**Scope**: `CLAUDE.md` — the `bin/booping <subcommand>` line under `## Commands` gains `status` after `items (…)`; `## Config` gains one bullet: `core.status` — the status report's query specs (`active_plans`, `unreviewed_plans`), directly under `core` because the CLI and the project-manager share it. `documentation/project_config.md` — a `### core.status` subsection under `## Shared keys, directly under core` naming both specs and that `booping status` reads them plus `core.retro_playbook.queries.candidates`; if its `## Snapshot: src/config.yaml` section is a verbatim copy of `src/config.yaml`, update it to match. `documentation/quick_start.md` section 4 — one sentence after the `booping query --config core.plans` example: `bin/booping status` prints the short project status (items, ideas, plans, records, marks), `bin/booping status plans` the plan tables. `documentation/vault.md` — under `## plans/`, one sentence pointing to `booping status plans`. Audience filter (rule/0008): what a user types and sees — the command, its sections, the config key; no module names, no internal helpers, no plan history.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | CLAUDE.md lines, project_config, quick_start, vault docs. | `CLAUDE.md`, `documentation/project_config.md`, `documentation/quick_start.md`, `documentation/vault.md` | 2 | pending |

## Definition of Done

### Task 4.1

- [ ] `grep -n "status" CLAUDE.md` shows `status` in the subcommand list and the `core.status` bullet.
- [ ] `grep -n "core.status" documentation/project_config.md` shows the subsection.
- [ ] `just docs` builds without warnings.

Return: the list of changed files, nothing else.

## References

- `documentation/project_config.md` `### core.autonomy` — subsection shape.
- `CLAUDE.md` `## Config` `core.tracker` bullet — bullet shape.

## Verify

`just docs`
