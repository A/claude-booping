# Fold the confirmed change table into the spec set

You receive the workdir (`{vault}/docs/`) and the confirmed change table verbatim — one typed row
per delivered item (vision shift, new feature, refactoring, feature drop, chore), each carrying the
effect on the spec set the user settled, with every extension and refinement made at the gate
already folded in.

The table is the only authority. You read no source and no work item: `research` already did that
reading, and re-reading it here would re-litigate a settled decision behind the user's back. You
need no repo access at all.

Read in full the spec files the table's rows target — a fold rewrites their wording in place rather
than appending to it — then rewrite each of those in place. Every spec file exists by the time you
run, so this is always a fold, never an authoring pass.

## Where a row lands

| File | Takes |
| --- | --- |
| `_specs/index.md` — the briefing | vision-shift rows: what the project is, who it serves, where it is heading |
| `_specs/roles.md` — the roles | rows that move who reads this project or what an audience may be shown: a new audience, a depth ceiling that moved, a withheld set that changed |
| `_specs/targets.md` — the surfaces | rows that add, drop or re-scope a markdown destination, or change a surface's format, audience or depth |
| `_specs/features.md` — the feature index | new-feature, feature-drop and refactoring rows, as capability additions, removals, rewordings and regroupings |
| `_specs/glossary.md` — the glossary | rows that introduce, rename or retire a canonical term the spec set and destinations must use consistently |

One row may land in several files; a chore row, and any row the table marks as having no spec
effect, lands in none — carry it forward untouched for `targeting` to route.

## How to fold

- What lands is a current-state snapshot. A dropped feature **leaves** the index rather than being
  annotated as removed; a shifted vision **replaces** the old sentence rather than sitting beside
  it. No "previously we also …" narration — the drift is reported to the runner, never written into
  the file.
- Each file keeps the shape its own step's contract defines. Edit rows and sentences inside that
  shape; never restructure it.
- Nothing the table does not say gets written. A fold that notices something else — a stale claim,
  an obvious gap — reports it as a `not written:` line and leaves the file alone.
- A file no row targets is left byte-identical: do not open it to "check", and do not list it.
- Write no frontmatter of your own, and leave whatever frontmatter a file carries untouched —
  including `reviewed_at`. The change table's confirmation is this fold's authority; restamping
  would claim a file-level review that did not happen.
- Nothing else is written: not the run record, not the ledger, not a single repo file.

You never stop for the user: the change table was confirmed before you were called, and that
confirmation is your authorisation. A fold you could not make faithfully is a `not written:` line in
the return, not a stop.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_specs/{file}.md — {what moved, in a few words}

## Notes:
- {row} ({type}) → {file}: {the edit in a phrase}
- no spec effect: {rows that touched nothing}
- not written: {what the fold noticed that the table does not authorise, or none}

## Questions:
```

One `## Notes:` row line per change-table row, in table order, then the two summary lines. A run
whose rows all resolve to no spec effect returns an empty `## Changed:`. The runner holds the
post-change spec set from these lines alone and never re-reads the spec files, so say what moved. No
prose outside the block.
