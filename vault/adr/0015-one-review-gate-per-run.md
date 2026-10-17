---
type: adr
title: A playbook run stops for review at one gate
summary: Core playbooks take user decisions in-step and stop for approval once — groom at present, retro at synthesize, migrate before applying, develop only to confirm the branch.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
values: [value/0008, value/0007, value/0012]
rules: [rule/0003, booping:rule/0004]
sources: [playbooks/groom/_specs/DECISIONS.md, playbooks/develop/_specs/DECISIONS.md, playbooks/code-review/_specs/DECISIONS.md, playbooks/migrate/_specs/DECISIONS.md, playbooks/setup/_specs/DECISIONS.md, CHANGELOG.md]
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/20260802-groom-skill-vs-playbook-metrics.md
---

## Context

The first groom playbook had four confirm points, each a status:
`awaiting-framing-confirm`, `awaiting-design-confirm`,
`awaiting-decomposition-confirm` and the approval. The skill-versus-playbook
measurements put the playbook's remaining cost in call count — transitions and gate
round-trips. The old groom skill had one approval near the end.

## Decision

Each core playbook stops for review once; other user decisions are taken in-step, in prose ([booping:rule/0032](../../specs/rule/0032-approval-asked-in-prose.md)), without a status of their own.

- **groom** — intake posts a framing brief and the user's answers to its scope
  questions are the confirmation; design is aligned in conversation while drafting;
  `present` is the single approval gate, over a human-targeted summary and the full
  plan.
- **develop** — the only stop is confirming the sprint branch name; handing a plan to
  develop is its approval, and verify's guardrails decide the exit with no user gate.
- **code-review** — no gate; the human's verdict on the findings is the approval.
- **retro** — the draft's approval at `synthesize`.
- **migrate** — one gate over the whole pending set, not one per migration.
- **setup** — no gate; every decision is asked in-step.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [One gate per run](#one-gate-per-run) | accepted | low | high | Fewer round-trips; in-step questions remain |
| [A confirm status per phase](#a-confirm-status-per-phase) | rejected | medium | high | Groom's first shape; removed |

### One gate per run

A run asks in-step and stops once.

- **Pros:** fewer transitions and round-trips; the user reviews the finished
  artifact rather than each intermediate.
- **Cons:** a wrong framing is caught by the user's answers to intake, not by a
  persisted confirmation.
- **Complexity:** low.
- **Reversibility:** high.

### A confirm status per phase

Framing, design and decomposition each end in an `awaiting-*-confirm` status.

- **Pros:** each intermediate is confirmed and the confirmation survives a session.
- **Cons:** more calls and user waits per run.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- Groom's compact checkpoint is the framing brief posted in chat at intake, in line
  with [rule/0003](../rule/0003-compact-artefact-first.md).
- Questions a run cannot settle park it in `awaiting-clarification` rather than
  adding a gate.
