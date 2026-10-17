---
type: adr
title: Milestone shape is an mdcheck schema
summary: Groom checks each milestone file with mdcheck against a schema in the groom playbook; `booping plan check` and its code go, and mdcheck becomes a required dependency.
created_by: owner
created_at: 2026-10-18
updated_at: 2026-10-18
status: accepted
values: [value/0015, value/0012]
rules: [rule/0025]
issues: []
sources: [vault/adr/0030-groom-drafts-the-whole-plan-in-one-pass.md]
---

## Context

The model misses milestone-shape rules even when told (adr/0030), so groom's gate needs a check that
code runs. `booping plan check` did it in 143 lines of its own: one Verify command, a path in Tasks,
at least as many DoD checkboxes as tasks, `sp` below `core.sprint.redecompose_threshold`. mdcheck
already checks every specs record against a schema. A schema with the same four rules, run over the
218 milestones in this vault, reported every finding `plan check` reported except the
checkbox-to-task comparison, which mdcheck cannot express; it also flagged 59 fenced Verify blocks,
which `plan check` accepted alongside a single inline code span. Building nothing means prose rules,
which adr/0030 measured missing.

## Decision

The milestone contract is `playbooks/groom/_schemas/milestone.yaml`, and groom runs
`mdcheck <schema> {plan-dir}/milestones/*/M*.md` directly. The contract narrows to what the schema can
state: Verify is one inline code span as its first paragraph, DoD holds at least one checkbox, `sp` is
1–4. `booping plan check` and its code are removed. mdcheck becomes a required dependency of every
install, not only of projects with specs.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [mdcheck schema run directly](#mdcheck-schema-run-directly) | accepted | low | high | Reuses the checker specs already depend on |
| [A booping check wrapper](#a-booping-check-wrapper) | rejected | medium | high | A command with no reader beyond what mdcheck prints |
| [Keep plan check](#keep-plan-check) | rejected | low | high | 143 lines for what a schema states |

### mdcheck schema run directly

The decision above.

- **Pros:** no booping code; one checker and one rule language for records and milestones; findings
  carry line numbers.
- **Cons:** a required install step for every user; the DoD-to-task comparison and the
  config-driven `sp` threshold are lost; fenced Verify blocks become findings.
- **Complexity:** low.
- **Reversibility:** high.

### A booping check wrapper

`booping check <path>` picks the schema by the file's type and runs mdcheck, folding `specs check` in.

- **Pros:** one command for every structural check; could read the threshold from config.
- **Cons:** new code whose only reader is the model reading mdcheck's own findings.
- **Complexity:** medium.
- **Reversibility:** high.

### Keep plan check

The command as it was.

- **Pros:** the exact checks, no new dependency.
- **Cons:** its own parser for sections, fences and lists, beside a checker that already does it.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Groom's draft-plan, present and gate text name the mdcheck call; the install guide lists mdcheck as
  required.
- Plans written before 2026-10-18 with fenced Verify blocks fail the schema; they are history and are
  not re-checked.
