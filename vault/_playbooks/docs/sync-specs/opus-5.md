# Fold the confirmed change table into the spec records

You receive the workdir (`{vault}/docs/`) and the confirmed change table verbatim — one typed row
per delivered item (vision shift, new feature, refactoring, feature drop, chore), each carrying the
effect on the spec records the user settled, with every extension and refinement made at the gate
already folded in.

The table is the only authority. You read no source, no work item and no code: `research` already
did that reading, and re-reading it here would re-litigate a settled decision behind the user's
back. You detect nothing yourself — a disagreement between a record and the code reaches you only
as a row that states it.

Read in full the records the table's rows target, under the project specs tier root
`{vault}/`, then edit each in place. Their shapes are the specs format's
(`src/specs/README.md`, Body and Marks, and `src/specs/schemas/<type>.yaml` under the plugin root).

## Where a row lands

| Row — its type, or the spec-set effect it names | Record | Action |
| --- | --- | --- |
| vision shift | the affected value record, `value/` | a `[clarify]` sentence in its `## In practice`, naming the shift; the value's statement, its other sections and its frontmatter fields other than `updated_at` are never rewritten — values are the owner's |
| audience | `reference/0001-audience.md` | the role's bullets in `## Facts` edited in place: a new audience, a depth ceiling that moved, a withheld set that changed |
| surface | `reference/0003-documentation-surfaces.md` | the surface's bullet in `## Facts` added, dropped or re-scoped in place: format, audience, depth |
| term | `reference/0002-glossary.md` | the term's bullet in `## Facts` introduced, renamed or retired in place |
| new feature | a new story record, `story/{NNNN}-{slug}.md` | `NNNN` the next number in `story/`; frontmatter `type: story`, `title`, `summary` (one line, at most 200 characters), `created_by: claude`, `created_at` and `updated_at` today, `status: done`; body the "As **who**, I want …, so that …" sentence, then `## Criteria` with one to five items |
| refactoring | the story it moves | that story's `## Criteria` items edited in place |
| feature drop | the story it drops | a `[clarify]` mark in its `## Criteria` naming the drop; `status:` untouched |
| chore | none | carried forward untouched for `targeting` to route |

One row may land in several records — a new-feature row that also adds a term lands in the glossary
too. A row the table marks as having no spec-set effect lands in none.

## How to fold

- Edit only what a confirmed row says. Within an edited record, what the row does not settle is
  marked `[clarify]` at the start of the item or sentence, with one sentence on what to settle
  (rule/0002).
- A row that itself records a disagreement between a record and the code without settling which is
  right is marked `[unknown]` on that record, with one sentence on what disagrees (rule/0002).
- What lands is a current-state snapshot: a fact a row changes **replaces** the old wording rather
  than sitting beside it. No "previously …" narration — the drift is reported to the runner, never
  written into a record.
- Each record keeps its type's shape — H2 order, criteria count, statement paragraph. Edit items and
  sentences inside that shape; never restructure it.
- A fold that notices something else — a stale claim, an obvious gap — reports it as a
  `not written:` line and leaves the record alone.
- A record no row targets is left byte-identical: do not open it to "check", and do not list it.
- Every record you edit gets `updated_at` set to today. `reviewed` is the owner's alone — never add
  or change it — and no other frontmatter is touched.
- Nothing else is written: not the run record, not the ledger, not a single repo file.

You never stop for the user: the change table was confirmed before you were called, and that
confirmation is your authorisation. A fold you could not make faithfully is a `not written:` line in
the return, not a stop.

## The check

The step's last action, after every edit: run `booping specs check --tier project` and carry its
result line into the return. A failure the fold caused is fixed in the record and the check run
again; the result line returned is the last run's.

## Return format

```markdown
## Changed:
- [CREATED] {vault}/story/{NNNN}-{slug}.md — {the story, in a few words}
- [UPDATED] {vault}/{type}/{NNNN}-{slug}.md — {what moved, in a few words}

## Notes:
- {row} ({type}) → {record}: {the edit in a phrase}
- no spec effect: {rows that touched nothing}
- marks: {each `[clarify]` / `[unknown]` written, with its record, or none}
- not written: {what the fold noticed that the table does not authorise, or none}
- specs check: {the result line of `booping specs check --tier project`}

## Questions:
```

One `## Changed:` line per record, `[CREATED]` or `[UPDATED]`. One `## Notes:` row line per
change-table row, in table order, then the summary lines. A run whose rows all resolve to no spec
effect returns an empty `## Changed:` and still runs the check. The runner holds the post-change
records from these lines alone and never re-reads them, so say what moved. No prose outside the
block.
