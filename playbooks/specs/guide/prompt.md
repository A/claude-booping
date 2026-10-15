---
summary: Act on the user's specs request from the dialogue.
review_gate: null
---

Act on the user's request; the scenarios below orient, never restrict — never ask which one to run.
Flags and their allowed values come from `booping specs open-items {verb} --help`.

## Init

No project tier yet (the preamble lists none, or `booping specs ls` finds no specs): offer to
create it. Once the user agrees, run `booping specs init --tier project`, then walk the user
through [the alignment guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-alignment.md).

## Alignment

The user refines the project's values: read the `value` records, then follow the alignment
guide's order — values first, then the boundaries that follow from them. Next:
`booping specs check` after each record written.

## Auto-review

Read the values, rules and ADRs. A contradiction the records settle becomes a `conflict` record; one
the user must settle becomes an item. Next: `booping specs open-items add --direction conflict`.

## Record

A decision → an ADR, only for one choice with a real alternative and a reason the code cannot
show. An idea → an idea record. A constraint on how the model works → a rule with `targets` and
`brief`. Next: an ADR with a `Confirmation:` line → `booping specs open-items add --record adr/NNNN`;
anything else → `booping specs check`.

## Sync specs and code

Compare the records with the code; each gap becomes one item with the direction it runs:
`booping specs open-items add --source sync`. Next: `booping specs open-items scan` for the marks
and check findings.

## Retro to rules

A retrospective awaits learning → hand it to learn. A lesson from this dialogue → a rule record,
written directly. Next: `/playbook learn`, or `booping specs check` after the rule.

## Open items

Show `booping specs open-items list`; the user picks. An item needing no work →
`booping specs open-items close {ids} --dropped --reason "…"`; a planned item whose plan was
cancelled outside develop → `booping specs open-items reopen --plan {plan}`. Next:
`/playbook groom` naming the picked ids — groom links them to the plan.
