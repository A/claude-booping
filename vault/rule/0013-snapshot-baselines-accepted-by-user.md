---
type: rule
title: Snapshot baselines are accepted by the user, never by a run
summary: A run never runs just snapshots-accept or writes the committed playbook reports; it leaves the drift uncommitted and names it in its final report for the user to accept.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
sources: [CLAUDE.md]
targets: [develop]
brief: "Never run just snapshots-accept or write playbooks/*/_reports/output.md. At wrap-up run just snapshots; on drift, do not stop: leave the reports uncommitted and name each drifted playbook with `just snapshots-accept {playbook}` in the final report."
---

## Rule

The committed playbook reports (`playbooks/*/_reports/output.md`) are the user's review gate over playbook sources. Neither the orchestrator nor a worker runs `just snapshots-accept` or writes a report. When a sprint touches playbook sources (manifests, step `prompt.md`, shared partials, `src/templates/`), wrap-up runs the read-only `just snapshots` and does not stop on drift: the run commits the sources, leaves the reports as they are, and its final report names each drifted playbook with the `just snapshots-accept {playbook}` command. The user reviews and accepts the drift later, in a commit of their own. Until then `just ci` fails at its snapshots step, so a run's CI gate treats a failure that is snapshot drift alone as passed and reports it; any other failure still fails the gate (owner, 2026-10-17; develop's only stop stays the branch, adr/0015). No drift, nothing to report.

## Follows from

- [Adjustable control](../value/0009-adjustable-control.md) — a change to what playbooks say
  stays visible to the human instead of passing the gate silently.
- [Proven to work](../value/0010-proven-to-work.md) — the baseline holds the rendered behaviour;
  accepting it from inside a run empties the check.
- [Plans run to the end](../value/0007-plans-run-to-the-end.md) — drift is reported, never a stop.

