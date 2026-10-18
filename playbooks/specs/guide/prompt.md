---
summary: Act on the user's specs request from the dialogue.
review_gate: null
---

Act on the user's request; the scenarios below orient, never restrict — never ask which one to run.
An open item is filed with `booping create core.specs.open_items.template {vault}/open-items --set title=… --set source=… [--set direction=…] [--set record=…] [--set body=…]`;
`direction` is one of `code-to-spec`, `spec-to-code`, `conflict`, `clarify`.

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
filed with `--set source=manual --set direction=conflict|clarify`, the question in its body, then
`booping transition {vault}/open-items/OI-NNNN.md clarify`;
the user's answer goes into the body and `… open` moves it back. Next: propose Sync specs and
code; do not run it.

## Site review

The user pastes the specs site's Outbox block (`## {ref} — {title}` groups). Per record, check each
comment against the record first: apply it, or skip it when the record already says so. A
`{ref} — accepted {date}` line sets `review: accepted` and `review_evidence: "site review — {date}"`.
Next: `booping specs check`.

## Record

A decision → an ADR, only for one choice with a real alternative and a reason the code cannot
show. An idea → an idea record. A constraint on how the model works → a rule with `targets` and
`brief`.

An ADR is drafted `status: proposed`, then:

1. Score it: spawn `booping:adr-scorer` with a prompt that pastes the ADR file's text and the text
   of [the rubric](${CLAUDE_PLUGIN_ROOT}/playbooks/specs/guide/adr-rubric.md) — the text itself,
   never a path. A score ≤ 1 → redraft the alternatives from its findings and score again, at
   most two rounds; then the brief carries the score as it stands.
2. Show the brief, exactly this shape:

   ```
   **ADR {NNNN} — {title}** · {status} · оценка альтернатив {score}/3{; findings if < 3}

   | | вариант | почему |
   |---|---|---|
   | ✔ | {chosen option} | {its reason} |
   | ✘ | {rejected option} | {why rejected} |

   Ключевые моменты:
   1. {each point of the chosen decision a reader must see to object to it}

   Задевает: {ADR/value refs and how — "разворачивает ADR N" for a reversal}
   Решил сам: {each call you made alone, or "ничего"}

   Если что-то не так — скажи, поправлю; если всё ок — продолжаю.
   ```

3. The user's answer sets the level, with its evidence (the format guide's `review_evidence`):
   - no objection → `status: accepted`, `review: shown`, evidence the date and where it was shown;
   - an explicit yes → `status: accepted`, `review: accepted`, evidence the user's words quoted, the date and where;
   - a discussion that ends in agreement → `status: accepted`, `review: discussed`, evidence the user's words quoted, the date, where and the gist;
   - an objection → back to the draft, then score and brief again.

Autonomous: log the brief as an agent decision instead of showing it, then set `status: accepted`
with no `review` key.

Next: an ADR with a `Confirmation:` line → file an item with `--set source=adr --set record=adr/NNNN
--set direction=spec-to-code --set title="{the Confirmation: line}"`;
anything else → `booping specs check`.

## Sync specs and code

Compare the records with the code; each gap becomes one item with the direction it runs:
filed with `--set source=sync --set direction=…`. Next: `booping specs scan` for the marks
and check findings.

## Retro to rules

A retrospective awaits learning → hand it to learn. A lesson from this dialogue → a rule record,
written directly. Next: `/playbook learn`, or `booping specs check` after the rule.

## Open items

Show `booping query --config core.specs.open_items.index --where status:in=open,planned`; the user picks. An item
needing no work → `booping set {item} reason="…"` then `booping transition {item} dropped`; a planned
item whose plan was cancelled outside develop → `booping transition {item} open`.
Supervised: next is `/playbook groom` naming the picked ids — groom links them to the plan and stops at its plan review.
Autonomous: run `/playbook groom` naming the picked ids — none picked, every `open` item — then `/playbook develop` on the plan it readies, in this session, without stopping; a groom that splits develops the first plan and reports the parked stubs.
