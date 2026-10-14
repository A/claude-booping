---
type: adr
title: Run-state persistence is an authored tier, and confirmation is a status
summary: A playbook's state machine is authored at one of three tiers — ephemeral, minimal, rich — never derived from the graph; a confirmation that must persist is a status transition, not a flag.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0007, value/0009, value/0012]
sources: [vault/notes/20260731-playbook-authoring-state-machines-design.md, playbooks/playbook-authoring/_specs/DECISIONS.md, playbooks/migrate/_specs/DECISIONS.md]
---

## Context

Playbooks gained opt-in `states:`. Authoring needed a way to decide whether a
playbook gets a machine and how much of one. Confirmations had been `confirmed:`
flags flipped in a file — a hand-rolled two-state machine enforced only by prose.
Two machine roles appeared: a procedure tracker that lets a run resume, and an
artifact lifecycle whose statuses are hand-off points other playbooks gate on.

## Criteria

- An interrupted run resumes where it stopped when a session boundary is likely.
- A confirmation that gates a hand-off is enforced mechanically.
- A short single-session run pays nothing for tracking.

## Decision

Every playbook has a state machine; the authoring question is whether it is
persisted, at one of three tiers: **ephemeral** (no `states:`; gates are the
transitions and the conversation is the storage), **minimal** (the confirmation
chain only) or **rich** (superstates, script hooks, per-instance machines, a
hand-off contract). The tier is authored: `decompose` records a verdict with its
reason, the `states` step acts on it, and the user can override it at that gate.
The strongest reason for a rich machine is an artifact other playbooks gate on;
against a machine are a short single-session run, conversational gates, and an
artifact whose lifecycle already lives elsewhere. A confirmation that must persist
is an `awaiting-*` status whose exit transition requires explicit user confirmation
— silence never counts — and stamps `reviewed_at` on the reviewed file. Every
active phase gets an explicit in-progress status.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Authored tier](#authored-tier) | accepted | medium | medium | Judgment per playbook, confirmed by the user |
| [Machine derived from the graph](#machine-derived-from-the-graph) | rejected | medium | medium | A DAG is not a state machine |
| [Formal threshold rules](#formal-threshold-rules) | rejected | low | high | Over-mechanical for a judgment call |
| [Confirmed flags](#confirmed-flags) | rejected | low | high | Enforced only by prose |

### Authored tier

The author chooses ephemeral, minimal or rich from heuristics; the minimal tier is
a stamp-out pattern in the template.

- **Pros:** machines exist only where resume or a hand-off pays for them;
  confirmations become harness-enforced.
- **Cons:** each transition is a call; a judgment the user has to review.
- **Complexity:** medium.
- **Reversibility:** medium.

### Machine derived from the graph

A wave-by-wave state machine generated from `graph:`.

- **Pros:** no authoring step.
- **Cons:** the graph orders work; it does not name hand-off statuses or gates.
- **Complexity:** medium.
- **Reversibility:** medium.

### Formal threshold rules

Numeric rules pick the tier (inner depth above N and the like); raised in a
cross-review.

- **Pros:** reproducible.
- **Cons:** over-mechanical for a class of decision booping leaves to prose plus a
  user gate.
- **Complexity:** low.
- **Reversibility:** high.

### Confirmed flags

A `confirmed:` key the user or the runner flips in the artifact.

- **Pros:** no machine.
- **Cons:** nothing enforces it; the flag carries no history of who confirmed what.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Code-review was first authored ephemeral and later got a machine once its review
  became a persisted artifact with re-review.
- Migrate stays ephemeral: the recorded migration id advances per migration and is
  the only state, so a machine would duplicate a ledger the vault already owns.
- A reviewed subject that cannot carry frontmatter stamps
  `<subject>_reviewed_at` on the machine's artifact instead.
