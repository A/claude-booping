---
type: rule
title: Snapshot baselines are accepted by the user, never by a run
summary: A run never runs just snapshots-accept or writes the committed playbook reports; drift is shown to the user, who reviews and accepts it before the commit.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [develop]
brief: "Never run just snapshots-accept or write playbooks/*/_reports/output.md. At wrap-up run just snapshots; on drift, show it and ask the user to accept before the closing commit."
sources: [vault/_lessons/0013_snapshot-baselines-are-the-users-review-gate.md, CLAUDE.md]
---

## Rule

The committed playbook reports (`playbooks/*/_reports/output.md`) are the user's
review gate over playbook sources. Neither the orchestrator nor a worker runs
`just snapshots-accept` or writes a report. When a sprint touches playbook sources
(manifests, step `prompt.md`, shared partials, `src/templates/`), wrap-up runs the
read-only `just snapshots`, shows the drift to the user and asks them to review
and accept it before the closing commit; the source and its report are then
committed together. No drift, nothing to ask.

## Follows from

- [Adjustable control](../value/0009-adjustable-control.md) — a change to what playbooks say
  stays visible to the human instead of passing the gate silently.
- [Proven to work](../value/0010-proven-to-work.md) — the baseline holds the rendered behaviour;
  accepting it from inside a run empties the check.

