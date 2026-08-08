---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# record

## Contract

- **Needs** —
  - what this run landed and where — one line per destination document the update loop touched,
    naming the change ids it carried and how it left the loop (verified, verified with
    corrections, or dropped with the reason it was dropped), plus the history entry the run
    seeded or appended and the change ids behind its bullets. The document texts themselves are
    not needed and must not be re-read: the outcome lines are the whole input, and a destination
    whose content matters is the loop's business, not this step's
  - which delivered work items the run's coverage accounts for — each in-scope item's identity
    and the change ids it produced, so an item can be checked change by change: an item counts as
    documented only when every change it produced either landed in a destination or was
    deliberately not targeted with a recorded reason
  - the unresolved verification findings the run collected — their count alone, to state that
    they stay open; the findings themselves already sit on the record and are never restated
- **Value** — the run's closing act, and the only writer of the fact that a work item is now
  documented. Two audiences read what it writes. A **later run** reads the ledger rows the
  `close-documented` hook derives from the `documented:` list — that list is the sole reason a
  finished item stops appearing in the next `survey`'s undocumented set, so an item listed here
  in error is an item that is never documented again. A **human** opening the record months
  later reads the landed table as the answer to *what did that run actually do*: destination,
  changes, outcome, in one place, without opening five documents. The accounting rule is what
  makes both safe — **a dropped destination withholds its item**. When a change's only
  destination left the loop dropped, the change is unaccounted, its item stays off the
  `documented:` list, and the next run resurfaces it; listing it anyway would bury the work the
  loop declined to do. A chore that no surface documents is the opposite case: `targeting`
  recorded why nothing needs it, so the change is accounted and its item may be listed. The step
  writes no ledger row itself — `close-documented` on the `recording → done` edge is the ledger's
  single writer, and this step's `documented:` list is the input it reads. Nothing here is
  re-derived: every fact is a line the runner already holds from the loop's and `changelog`'s
  returns, so the step composes and never investigates.
- **Output files** —
  - `[UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md` — the run record, closed
    - a `## Landed` section appended at the end: one row per destination the loop touched plus
      one for the history file, columns Destination / Changes / Outcome, in the targeting plan's
      row order with the history row last; a dropped row keeps its reason in the Outcome cell
      rather than disappearing
    - one closing line under the table: how many in-scope items are documented out of how many,
      which item is withheld and on which change, and how many verification findings stay open
    - frontmatter gains `documented:` — a list of the work items now documented, each written the
      way the survey and the ledger identify it, one entry per item and none for a withheld one.
      A run that documents nothing writes `documented: []`; the key is always present, since the
      hook reads it
    - every other frontmatter key is left untouched — `status:` is `playbook-transition`'s,
      `started:`, `commit:`, the `*_reviewed_at` stamps and `completed:` are their own edges'
    - every earlier section is left exactly as found: `## Scope`, `## Changes`, the targeting plan
      with its progress column, and `## Verification findings` are not reworded, re-scoped or
      tidied
  - nothing else — `_specs/documented.md` is the `close-documented` hook's file and is never
    opened here, the spec set is not touched, no destination document is reopened, and
    `CHANGELOG.md` belongs to the step before this one
- **Harness return** — the standard block. `## Changed:` names the run record alone, annotated
  with the destination count and the size of the `documented:` list. `## Notes:` carries one line
  per landed row, then one per item listed documented with the change ids that account for it,
  then one per item withheld naming the unaccounted change and why, then the open-findings line.
  The runner closes the run from those lines: the `recording → done` gate checks the
  `documented:` list against the covered items and the landed table against the destinations
  written, and both are readable in the return without opening the record.
- **Review gate** —
  - none — the table restates outcomes the loop already produced and a list the accounting rule
    determines, so there is nothing left for a user to settle
  - the `recording → done` gate is the machine's, checked by the runner against this return; a
    withheld item is a correct outcome, not a blocker, and is reported rather than asked about
- **Delegation** — detached: `detached: "opus:low"` (the decomposition's `opus-5:low`; `opus` is
  the tier the `detached:` grammar accepts). Low effort is the point: the inputs are already
  compressed lines, the only judgement is applying the accounting rule change by change, and the
  work is composing a table and a list. It is detached rather than inline so the run record's
  earlier sections — change table, targeting plan, findings — are re-read by the agent that
  appends to them and not by the runner, whose context at the end of a run is the most expensive
  in the playbook. The agent's bootstrap needs the run record path, the per-destination outcome
  lines, the `changelog` return line, and the in-scope items with their change ids; it needs no
  repo access at all.

## Example artifact

The frontmatter key and the `## Landed` section written to
`{vault}/docs/202608081352-retro-and-code-review-track-splits.md` — five destinations from the
targeting plan, one of them dropped, plus the history entry:

````markdown
---
title: Retro and code-review track splits
status: recording
documented:
  - plans/202608071455_retro-status-track-split/index.md
  - plans/202608072133_learn-targets-consolidation/index.md
  - plans/202608081156_code-review-track-split/index.md
---

## Landed

| Destination | Changes | Outcome |
| --- | --- | --- |
| `README.md` | C1, C4 | verified — 2 corrections (1 fact, 1 depth) |
| `documentation/playbook.md` | C1, C2 | verified — clean |
| `documentation/vault.md` | C2 | verified — 1 correction (legacy) |
| `documentation/project_config.md` | C5 | dropped — the file's query section is being rewritten by an open plan; the row is left for the next run |
| `CLAUDE.md` | C1, C4 | verified — 1 unresolved finding |
| `CHANGELOG.md` | C1, C4, C5 | appended — 3 bullets under `## Unreleased` |

3 of 4 in-scope items documented. `plans/20260805-12-35_frontmatter-query/index.md` is withheld:
C5 reached the history but no documentation surface, its only destination having been dropped, so
the next run surfaces the item again. C3 (chore) needed no destination and holds nothing back.
1 verification finding stays open on this record.
````

A run in which every row was verified writes the same section with no dropped row and lists every
in-scope item. A run whose targeting plan was empty — an all-chore table closed at the targeting
gate — still writes the heading, a table holding the history row alone, and a closing line saying
which items are documented on the strength of their not-targeted reasons.

## Return Format

````markdown
## Changed:
- [UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md — `## Landed`, {n} destinations, `documented:` {m} items

## Notes:
- landed: {destination} — {change ids} — {outcome}
- documented: {work item} — {the change ids that account for it}
- not documented: {work item} — {unaccounted change id} ({why it is unaccounted})
- open findings: {n} unresolved, left on the record | none

## Questions:
````

One `## Notes:` landed line per table row in table order, the history row last; then one
`documented:` line per listed item, then one `not documented:` line per withheld item, then the
findings line. A run that documents nothing keeps the `documented:` lines empty and still returns
its landed and findings lines.
