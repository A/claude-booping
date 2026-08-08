# Read the delivered items and build the typed change table

You receive the workdir (`{vault}/docs/`), the run record already on disk, the confirmed scope from
its `## Scope` section — the delivered items this run covers — and the spec set: the briefing
(`_specs/index.md`), the roles (`_specs/roles.md`), the surfaces (`_specs/targets.md`) and the
feature index (`_specs/features.md`). On a re-entry from the change gate you also receive the items
the user added; only those are read again.

This is the run's one expensive read, paid once and compressed. You read no work item yourself: each
is read in its own sub-agent, and what comes back to you is a row, never the item's text.

## The fan-out

Read the four spec files yourself, then spawn one sub-agent per in-scope item — the researcher agent
`config.core.research_agent` names — all in a single message so they run in parallel. Each brief
carries:

- the one item's path, and nothing pointing past it: no sibling item, no commit range, no repo
  history — a sub-agent that wanders re-reads what another one already owns
- the spec-set facts its row must be tied to: the briefing's vision in a line, the role names, the
  surface paths, the capability and group names of the feature index
- the fixed question — what changed for someone who uses this project, of which type, against which
  spec file — plus the row shape below and the instruction to return the row or rows alone

## The rows

One row per distinct change, at least one row per item. An item that produced nothing worth
documenting still gets a `chore` row with `none` in the spec-set column, so every in-scope item is
provably covered — the exit gate demands it, and `record` marks items documented from this table.
Ids run `C1`, `C2`, … in scope order; on a second pass the rows already written keep their ids and
their wording, and the added items continue the sequence.

Columns: `# | Work item | Type | What changed | Spec-set effect`.

- **Type** is a closed vocabulary — `vision shift`, `new feature`, `refactoring`, `feature drop`,
  `chore`. No sixth word.
- **What changed** is the user-visible effect, written in the project's own vocabulary and in the
  present tense. Never diff language, file lists or module names: a business-facing surface is
  served from this cell later, which is why roles and surfaces are read here and not only at
  targeting.
- **Spec-set effect** names each spec file a row moves and the edit it implies (`features.md`: new
  capability *frontmatter query* under the CLI group), or `none`.

## The file to write

The run record gains `## Changes`: the table, then one closing line giving the row count over the
item count, the count per type, and how many rows touch each spec file. One table per run — a second
pass rewrites the section in place rather than appending to it.

Write the section before you present anything, so a run resumed at the change gate in a later
session recovers the table from the record rather than from a context that is gone. The same section
is where the gate's fold lands: the record ends up carrying the confirmed table, not the draft.

Nothing else is written. `_specs/` is read-only here — `sync-specs` owns that write — no work item's
own file is touched, and no destination document is opened. No frontmatter of your own:
`changes_reviewed_at:` is the confirming edge's hook.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — `## Changes`, {n} rows over {m} items

## Notes:
- types: {n} vision shift, {n} new feature, {n} refactoring, {n} feature drop, {n} chore
- spec-set effect: {one clause per spec file any row touches, or `none`}
- read: {m} items in {m} sub-agents

## Questions:
```

`## Questions:` is always empty — extending the change table is the gate's question, not the step's.
The runner presents the gate from these lines plus the section just written. No prose outside the
block.
