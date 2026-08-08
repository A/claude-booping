# Close the run record with what landed where

You receive the run record's path, one outcome line per destination the update loop touched — the
change ids it carried and how it left the loop (verified, verified with corrections, or dropped
with the reason) — the `changelog` return line with the change ids behind its bullets, the in-scope
work items each with the change ids it produced, and the count of unresolved verification findings.

Those lines are the whole input. You compose, you never investigate: no destination document is
reopened, no source is read, no effect is re-derived. The one file you open is the run record —
read its targeting plan for the row order, its change table and its findings section — and
everything already in it stays exactly as found.

## The file to write

`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md` — the run record, closed.

- a `## Landed` section appended at the end: one row per destination, columns Destination /
  Changes / Outcome, in the targeting plan's row order with the history file's row last. A dropped
  row keeps its place and carries its reason in the Outcome cell rather than disappearing.
- one closing line under the table: how many in-scope items are documented out of how many, which
  item is withheld and on which change, and how many verification findings stay open.
- frontmatter gains `documented:` — the work items now documented, one entry each, written the way
  the survey and the ledger identify them, none for a withheld one. A run that documents nothing
  writes `documented: []`; the key is always present, since the `close-documented` hook reads it.
- every other frontmatter key is left untouched: `status:` is `playbook-transition`'s, and
  `started:`, `commit:`, the `*_reviewed_at` stamps and `completed:` belong to their own edges.
- every earlier section is left exactly as found — `## Scope`, `## Changes`, the targeting plan
  with its progress column and `## Verification findings` are not reworded, re-scoped or tidied.
- nothing else is written or opened: `_specs/documented.md` is the `close-documented` hook's file,
  the spec set is not touched, and `CHANGELOG.md` belongs to the step before this one.

A run whose targeting plan was empty still writes the heading, a table holding the history row
alone, and its closing line.

## The accounting rule

An item counts as documented only when **every** change it produced either landed in a destination
or was deliberately not targeted with a reason `targeting` recorded. Apply it change by change.

- **A dropped destination withholds its item.** When a change's only destination left the loop
  dropped, that change is unaccounted, its item stays off the `documented:` list, and the next
  survey resurfaces it. Listing it anyway buries the work the loop declined to do — and the
  `documented:` list is the sole reason a finished item ever stops being resurfaced.
- The history entry accounts for nothing. A change that reached `CHANGELOG.md` but no documentation
  surface is still unaccounted.
- A change no surface needs — a chore whose not-targeted reason is on the record — is accounted and
  holds nothing back.
- A withheld item is a correct outcome, not a blocker: report it, never ask about it. The step has
  no gate and never stops for the user.
- The unresolved findings are counted, not restated — they already sit on the record.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — `## Landed`, {n} destinations, `documented:` {m} items

## Notes:
- landed: {destination} — {change ids} — {outcome}
- documented: {work item} — {the change ids that account for it}
- not documented: {work item} — {unaccounted change id} ({why it is unaccounted})
- open findings: {n} unresolved, left on the record | none

## Questions:
```

One `## Notes:` landed line per table row in table order, the history row last; then one
`documented:` line per listed item, then one `not documented:` line per withheld item, then the
findings line. A run that documents nothing keeps the `documented:` lines empty and still returns
its landed and findings lines. `## Questions:` stays empty. The runner closes the run from these
lines alone and never opens the record, so the accounting must be readable in the block. No prose
outside it.
