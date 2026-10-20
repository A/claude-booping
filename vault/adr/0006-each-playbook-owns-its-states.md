---
type: adr
title: Each playbook owns its state machine; no shared lifecycle
summary: Every artifact moves only through its own playbook's states machine, written solely by playbook-transition; playbooks hand off at a status, not through a shared lifecycle.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
rules: [rule/0023, rule/0025]
values: [value/0003, value/0007]
sources: [playbooks/groom/_specs/DECISIONS.md, playbooks/develop/_specs/DECISIONS.md, playbooks/develop/_specs/index.md, CHANGELOG.md, CLAUDE.md]
---

## Context

Plans had one lifecycle in core config (`plan.statuses`, superstates, post hooks)
driven by a plan-only `transition` command, while playbooks drove their own
machines through `playbook-transition`. When groom became a playbook, its machine
was designed as its own subset of the plan lifecycle joined to develop's at the
edges — "two different subsets of one machine, not one shared monolithic machine".
Develop first wrote the shared lifecycle names straight onto `status:`. A later fix
showed the cost of shared names: develop's entry status `awaiting-plan-review`
matched no real plan, because in groom it is a superstate that is never written to
a file.

## Decision

The shared plan-lifecycle vocabulary is gone. Each playbook declares named machines
in its `playbook.yaml` `states:` block; those blocks are the authoritative status
sets. Playbooks hand off at a status the next one accepts as entry — groom ends at
`ready-for-dev`, develop starts there or at `awaiting-approval`, where handing the
plan to develop is the approval. `booping playbook-transition` is the only writer
of run state and its printed mutation report is authoritative — never re-read to
verify; `booping playbook-state` is the read-only frontier used to resume.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Per-playbook machines](#per-playbook-machines) | accepted | medium | low | Each playbook owns and documents its statuses |
| [One lifecycle in core config](#one-lifecycle-in-core-config) | rejected | medium | medium | A second dispatcher; plan domain in core |
| [One monolithic machine shared by playbooks](#one-monolithic-machine-shared-by-playbooks) | rejected | high | medium | Rejected at the groom port |

### Per-playbook machines

Each playbook's `states:` block is its own machine over its own artifact.

- **Pros:** one dispatcher for every machine; a playbook's statuses are read in one
  file; user playbooks work the same way.
- **Cons:** hand-off statuses must agree between two files; the README's Statuses
  section is hand-maintained narrative over them.
- **Complexity:** medium.
- **Reversibility:** low.

### One lifecycle in core config

Plan statuses and hooks stay in `src/config.yaml` with their own transition command.

- **Pros:** one place lists every plan status.
- **Cons:** two dispatchers with duplicated idempotency, hooks and reporting; plan
  hooks unreachable from playbook machines.
- **Complexity:** medium.
- **Reversibility:** medium.

### One monolithic machine shared by playbooks

Groom and develop drive one machine covering the whole plan lifecycle.

- **Pros:** the hand-off is inside one machine.
- **Cons:** not named in the source beyond its rejection at the groom port.
- **Complexity:** high.
- **Reversibility:** medium.

## Consequences

- A status a playbook reads from another must be one the other actually writes, not
  a superstate.
- Hooks run after `status:` is written, so a failing hook leaves the artifact
  advanced; hooks that talk to the outside absorb their failures
  ([adr/0019](0019-tracker-is-a-best-effort-mirror.md)).
