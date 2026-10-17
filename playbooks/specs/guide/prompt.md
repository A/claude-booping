---
summary: Act on the user's specs request from the dialogue.
review_gate: null
---

Act on the user's request; the scenarios below orient, never restrict — never ask which one to run.
Flags and their allowed values come from `booping items {verb} --help`.

## Handed over

Another playbook hands over a piece of spec material or a question instead of a dialogue. Material:
write it into the record it belongs to, new or existing — a value, or anything dropping or weakening
a rule, as an owner draft; anything else per the autonomy mode. A question: answer it from the records.
Reply in at most five lines: the refs written or found, one line each, then what needs the owner.

## Init

No project tier yet (the preamble lists none, or `booping specs ls` finds no specs): offer to
create it. Once the user agrees, run `booping specs init --tier project`, then walk the user
through [the alignment guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-alignment.md).

## Import

The user brings specs written elsewhere: convert them per [the import guide](${CLAUDE_PLUGIN_ROOT}/docs/specs-import.md) —
English structural headings, area files split into `value` records. Next: `booping specs check`.

## Alignment

The user refines the project's values: read the `value` records, then follow the alignment
guide's order — values first, then the boundaries that follow from them. Next:
`booping specs check` after each record written.

## Auto-review

Read every record type in every tier the project reaches — values, rules, ADRs, conflicts, stories,
ideas, references, runbooks; stale records hide outside the first three. A fix that only makes a
record say what is already decided or true: apply it and report it. A contradiction the records
settle becomes a `conflict` record. Every finding the user must settle becomes an open item at once —
`booping items add --direction conflict|clarify`, the question in its body, then
`booping playbook-transition specs clarify --state open_item --target {vault}/open-items/OI-NNNN.md`;
the user's answer goes into the body and `… specs open …` moves it back. Next: propose Sync specs and
code; do not run it.

## Site review

The user pastes the specs site's Outbox block (`## {ref} — {title}` groups). Per record, check each
comment against the record first: apply it, or skip it when the record already says so. A
`{ref} — reviewed {date}` line sets `reviewed: {date}` — the only case you set `reviewed`, never on
your own initiative. Next: `booping specs check`.

## Record

A decision → an ADR, only for one choice with a real alternative and a reason the code cannot
show. An idea → an idea record. A constraint on how the model works → a rule with `targets` and
`brief`. Next: an ADR with a `Confirmation:` line → `booping items add --record adr/NNNN`;
anything else → `booping specs check`.

## Sync specs and code

Compare the records with the code; each gap becomes one item with the direction it runs:
`booping items add --source sync`. Next: `booping items scan` for the marks
and check findings.

## Retro to rules

A retrospective awaits learning → hand it to learn. A lesson from this dialogue → a rule record,
written directly. Next: `/playbook learn`, or `booping specs check` after the rule.

## Open items

Show `booping items list`; the user picks. An item needing no work →
`booping items close {ids} --dropped --reason "…"`; a planned item whose plan was
cancelled outside develop → `booping items reopen --plan {plan}`.
Supervised: next is `/playbook groom` naming the picked ids — groom links them to the plan and stops at its plan review.
Autonomous: run `/playbook groom` naming the picked ids — none picked, every `open` item — then `/playbook develop` on the plan it readies, in this session, without stopping; a groom that splits develops the first plan and reports the parked stubs.
