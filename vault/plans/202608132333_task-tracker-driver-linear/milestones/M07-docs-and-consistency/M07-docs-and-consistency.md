---
id: "07"
title: "Docs, CLAUDE.md and report consistency sweep"
sp: 2
status: pending
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M07: Docs, CLAUDE.md and report consistency sweep

Every surface that describes booping matches what the sprint shipped — no stale command list, no unlisted status, no rule file lagging a renamed section.

**Scope**: `CLAUDE.md`, `README.md`, `documentation/project_config.md`, `documentation/playbook.md`, `booping-tracker/README.md`, and the report rule files under `playbooks/*/_reports/`. Committed reports themselves are regenerated but accepted by the user, never by the sprint.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Update the plugin-internal surfaces: `CLAUDE.md`'s Commands (the `bin/booping-tracker` entry point, `just` targets now spanning two projects), Layout (`booping-tracker/` and its corpus), Config (`core.tracker`, the `api_key_env` convention, and that no config value is env-interpolated), Playbooks (the two tracker hook scripts, driver-conditional injection) and Lifecycle (groom's `awaiting-clarification`, `clarifications.md`, `return_to`); `README.md`'s hand-maintained Statuses narrative for groom's new status; `documentation/project_config.md` for the `core.tracker` reference; `documentation/playbook.md` where hook scripts and run state are described. | `CLAUDE.md`, `README.md`, `documentation/project_config.md`, `documentation/playbook.md` | 1 | pending |
| 7.2 | Write `booping-tracker/README.md` — the verb surface, the config it reads, the env var it needs and the exit-code contract — and reconcile the two existing report rule files with whatever headings the sprint's partials added — `playbooks/groom/_reports/rules.yaml` already pins the groom report's exact ordered H2 list, and `playbooks/_lib/report.rules.yaml` holds the rules shared by every report; neither file is created here, both are edited. | `booping-tracker/README.md`, `playbooks/groom/_reports/rules.yaml`, `playbooks/_lib/report.rules.yaml` | 1 | pending |

Tests: `just mdcheck` is the test for the rule files; the documentation surfaces are verified by reading them against the shipped behaviour, with no doc claiming a flag or key that does not exist.

## Definition of Done

### Task 7.1

- [ ] Every `CLAUDE.md` section named in the plan's CLAUDE.md-impact list is updated, and no section describes a command, key or status that the sprint did not ship.
- [ ] `README.md`'s Statuses narrative names `awaiting-clarification` and how a parked run resumes.
- [ ] The documentation site pages are audience-scoped: user-facing pages describe the driver and the Linear flow, not `booping-tracker`'s internal module layout.
- [ ] No surface documents the retired assumption that a playbook run always has a live conversation.

### Task 7.2

- [ ] `booping-tracker/README.md` lists every verb with its flags and the four exit codes, matching `--help` exactly.
- [ ] `just mdcheck` passes against the regenerated reports.
- [ ] Any drift in `playbooks/*/_reports/output.md` is reported to the user for acceptance; the sprint never runs `just snapshots-accept`.

## Verify

```
just mdcheck
just snapshots
bin/booping-tracker --help
```

Expected: `mdcheck` passes; `snapshots` reports only the drift the sprint intended, listed for the user to accept; the help output matches `booping-tracker/README.md` verb for verb.
