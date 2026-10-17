# Read the delivered items and build the typed change table

You receive the workdir (`{vault}/docs/`), the run record already on disk — its `## Briefing` and
the confirmed scope from its `## Scope` section, the delivered items this run covers — and the
spec records: the values and the feature index below, the audience record
`{vault}/reference/0001-audience.md` and the surfaces record
`{vault}/reference/0003-documentation-surfaces.md`. On a re-entry from the change gate you
also receive the items the user added; only those are read again.

This is the run's one expensive read, paid once and compressed. You read no work item yourself: each
is read in its own sub-agent, and what comes back to you is a row, never the item's text.

## The values

{% set values = 'core.docs_playbook.queries.values' | query -%}
{% if values -%}
| Value | Kind | Summary | Path |
| --- | --- | --- | --- |
{% for v in values -%}
| {{ v.title }} | {{ v.kind }} | {{ v.summary }} | {{ v.path }} |
{% endfor -%}
{%- else -%}
_No value records._
{%- endif %}

## The feature index

{% set features = 'core.docs_playbook.queries.features' | query -%}
{% if features -%}
| Story | Summary | Status | Path |
| --- | --- | --- | --- |
{% for f in features -%}
| {{ f.title }} | {{ f.summary }} | {{ f.status }} | {{ f.path }} |
{% endfor -%}
{%- else -%}
_No story records._
{%- endif %}

## The fan-out

Read the audience and surfaces records yourself, then spawn one sub-agent per in-scope item — the
researcher agent `config.core.research_agent` names — all in a single message so they run in
parallel. Each brief carries:

- the one item's path, and nothing pointing past it: no sibling item, no commit range, no repo
  history — a sub-agent that wanders re-reads what another one already owns
- the record facts its row must be tied to: the briefing's vision in a line, the role names with
  the depth each one reads at (reference/0001), the surface paths with the audience and depth of
  each (reference/0003), and the story titles of the feature index. The role names and the surface
  paths are what the row's **Audience** and **Target files** cells are filled from, so a brief that
  omits them gets those two cells invented
- the fixed question — what changed for someone who uses this project, of which type, against which
  record — plus the row shape below and the instruction to return the row or rows alone

## The rows

One row per distinct change, at least one row per item. An item that produced nothing worth
documenting still gets a `chore` row with `none` in the spec-set effect column, so every in-scope
item is provably covered — the exit gate demands it, and `record` marks items documented from this
table. Ids run `C1`, `C2`, … in scope order; on a second pass the rows already written keep their
ids and their wording, and the added items continue the sequence.

Columns: `# | Work item | Type | What changed | Audience | Target files | Spec-set effect`.

- **Type** is a closed vocabulary — `vision shift`, `new feature`, `refactoring`, `feature drop`,
  `chore`. No sixth word.
- **What changed** is the user-visible effect, written in the project's own vocabulary and in the
  present tense. Never diff language, file lists or module names: a business-facing surface is
  served from this cell later, which is why roles and surfaces are read here and not only at
  targeting.
- **Audience** names the roles that consume this change, taken from reference/0001 by their own
  names — never a role invented here, never "everyone". A change no role outside the repo consumes
  says so with the one role that does.
- **Target files** names the surfaces the change plausibly belongs on, taken from
  reference/0003 by their own paths, vault-relative where that record writes them so. These are
  **candidates, not the plan** — `targeting` owns the destinations and may add, drop or split them
  against the surfaces' depth ceilings. A row whose change is already documented on a surface still
  names it, so the gate can see the overlap.
- **Spec-set effect** names each record a row moves and the edit it implies (`story/0004`: a
  criterion for directory-scoped targets; `reference/0001`: a new audience; a new story:
  *frontmatter query*), or `none`. The spec records are themselves a surface: a row that moves one
  names it under **Target files** too.

Audience and Target files are why reference/0001 and reference/0003 are read at this step. Filling
either from your own judgement rather than from those two records is the failure mode — a role or a
path that does not appear there does not exist.

## The file to write

The run record gains `## Changes`: the table, then one closing line giving the row count over the
item count, the count per type, and how many rows touch each record. One table per run — a second
pass rewrites the section in place rather than appending to it.

Write the section before you present anything, so a run resumed at the change gate in a later
session recovers the table from the record rather than from a context that is gone. The same section
is where the gate's fold lands: the record ends up carrying the confirmed table, not the draft.

Nothing else is written. The spec records are read-only here — `sync-specs` owns that write — no
work item's own file is touched, and no destination document is opened. No frontmatter of your own:
`changes_reviewed_at:` is the confirming edge's hook.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — `## Changes`, {n} rows over {m} items

## Notes:
- types: {n} vision shift, {n} new feature, {n} refactoring, {n} feature drop, {n} chore
- audience: {one clause per role any row names, with the row ids}
- target files: {one clause per surface any row names, with the row ids}
- spec-set effect: {one clause per record any row touches, or `none`}
- read: {m} items in {m} sub-agents

## Questions:
```

`## Questions:` is always empty — extending the change table is the gate's question, not the step's.
The runner presents the gate from these lines plus the section just written. No prose outside the
block.
