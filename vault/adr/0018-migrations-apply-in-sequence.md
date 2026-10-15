---
type: adr
title: Migrations apply strictly in sequence, one commit each, after one gate
summary: Migrate asks once over the whole pending set, then applies each migration in id order through a fresh sub-agent, advancing the watermark and committing before the next; a failure stops the run.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0008, value/0002, value/0009]
sources: [playbooks/migrate/_specs/DECISIONS.md]
---

## Context

Each migration assumes the previous one landed. The user wanted each migration run
as an isolated, context-fresh unit whose whole instruction is that migration's
file, and wanted it revertable on its own. The playbook engine parallelises a
repeated subgraph's instances when every inner step is `detached:`, so the obvious
isolated shape would also run migrations concurrently. The user's ruling: "no
parallel migrations. One done - update .booping, commit everything, run next";
sequence outranks isolation where the two conflict.

## Decision

`survey` checks for uncommitted work, proposes committing both repo and vault and
commits on the user's confirmation — it never refuses to start — then shows the
pending set, rendered into the step body by the query, and asks once. The `apply`
subgraph repeats one runner-performed step per pending migration in ascending id
order, strictly one at a time. Its body spawns a fresh sub-agent briefed with the
migration's location, so no migration body enters the runner's context; the runner
then advances `latest_migration`, commits everything and continues. A migration
that cannot complete stops the run with its id, a diagnosis and a proposed remedy,
which may be a manual fix; there is no silent rollback and no skipping ahead. The
run is ephemeral: the watermark is the only state.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Runner step spawning a fresh agent](#runner-step-spawning-a-fresh-agent) | accepted | medium | high | Sequence and isolation both kept |
| [Detached instances](#detached-instances) | rejected | low | high | Instances could run in parallel |
| [Runner applies in its own context](#runner-applies-in-its-own-context) | rejected | low | high | Sequential but not isolated |
| [A gate per migration](#a-gate-per-migration) | rejected | low | high | One approval over the set instead |

### Runner step spawning a fresh agent

The inner step has no `detached:` key, so the engine runs instances in order; its
body delegates the work.

- **Pros:** strict order and halt-on-failure from the graph; each migration in a
  fresh context; the runner owns the watermark and commits.
- **Cons:** the step hand-rolls the bootstrap and return contract the framework
  gives detached steps; its eval suite was to pin that, and evals were skipped.
- **Complexity:** medium.
- **Reversibility:** high.

### Detached instances

The inner step is detached, so each instance runs in its own agent.

- **Pros:** isolation from the framework.
- **Cons:** the engine may run instances concurrently, breaking "N+1 never starts
  before N landed" and halt-on-failure.
- **Complexity:** low.
- **Reversibility:** high.

### Runner applies in its own context

The runner executes each migration's prompt itself.

- **Pros:** sequential with no delegation contract.
- **Cons:** every migration body enters the runner's context; no isolation.
- **Complexity:** low.
- **Reversibility:** high.

### A gate per migration

The user approves each migration before it runs.

- **Pros:** finer control.
- **Cons:** explicitly not wanted by the user; the reason is not named in the
  source.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- A resumed run re-renders its pending set from `latest_migration`; a break
  mid-migration is remedied by inspecting the working tree, which `survey` surfaces.
- The playbook shipped without eval suites, by the user's decision.
