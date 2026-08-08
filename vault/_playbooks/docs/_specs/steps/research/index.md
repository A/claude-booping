---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# research

## Contract

- **Needs** —
  - the delivered work items the run's confirmed scope covers — enough of each to find and read
    it: identity, status, the date it landed
  - what the project is, who it serves and where it is heading — the vocabulary every row is
    written in
  - the audiences the documentation serves and the tone and depth each one needs
  - the markdown documentation surfaces that exist, each with its format, audience and depth
  - the features, capabilities and groups the project ships today
- **Value** — the run's one expensive read, paid once and compressed. Each in-scope item is read
  in its own sub-agent against a fixed question — what changed, of which type, against which spec
  file — so no plan body, diff or commit log ever reaches the driving context and no sub-agent
  wanders into the repo's history. What comes back is a **typed row tied to the spec set**, and
  the table of those rows is the contract the rest of the run works from: `sync-specs` applies the
  spec-set column, `targeting` turns rows into destination documents, and the row ids are how a
  targeting row cites what a writer must say. The type vocabulary is closed — vision shift, new
  feature, refactoring, feature drop, chore — and `chore` is the row for an item with no spec-set
  effect and no destination, kept so every in-scope item is provably covered: the exit gate
  demands a row per item, and `record` marks items documented from this same table. Rows are
  written in the project's own vocabulary and state the user-visible effect, never diff language
  or file lists — that is what lets a business-facing surface be served from a row later, and why
  roles and surfaces are read here rather than only at targeting. The table is written to the run
  record before it is presented, so a run resumed at the change gate in a later session recovers
  it from the artifact instead of a context that is gone.
- **Output files** —
  - `[UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md` — the run record gains `## Changes`: the
    typed table plus one closing count line. One table per run — a second pass after the user adds
    items rewrites the section in place rather than appending, and rows the first pass already
    produced keep their ids and wording. The runner folds the user's extensions and refinements
    into the same section at the gate, so the record ends up carrying the confirmed table, not the
    draft. No frontmatter of the step's own: `changes_reviewed_at:` is the confirming edge's hook.
  - nothing else — `_specs/` is read-only here (`sync-specs` owns that write), no work item's own
    file is touched, and no destination document is opened.
- **Harness return** — the runner's own, assembled from the fan-out; no sub-agent produces it.
  `## Changed:` names the run record alone, annotated with the row count and the item count behind
  it. `## Notes:` carries the count per type, one clause per spec file any row touches, and the
  fan-out size — the runner presents the gate from those lines plus the section it just wrote.
  `## Questions:` is always empty: extending the change table is the gate's question, not the
  step's.
- **Review gate** —
  - extend, refine and confirm the change table, presented in chat from the section just written
  - an extension naming items that still have to be read sends the run back to this step, which
    reads only the added items and rewrites the section
  - confirmation is explicit — silence never counts; the confirming edge stamps
    `changes_reviewed_at:` on the run record
- **Delegation** — assisted, as the **Delegation levels** section of
  `${CLAUDE_PLUGIN_ROOT}/documentation/playbook.md` defines it: the runner performs the step and
  delegates the reading to one sub-agent per in-scope item, instances in parallel. No `detached:`
  key — the researcher is named in the body from `config.core.research_agent`. Each sub-agent is
  briefed with one item plus the spec-set facts its row must be tied to, and returns the row
  alone, never the item's text; the runner holds the rows, assembles the table and writes it. The
  decomposition's `opus-5:high` binds those reading sub-agents — an assisted step has no
  frontmatter model of its own, and the runner's model is the user's.

## Example artifact

The `## Changes` section appended to `{vault}/docs/202608081352-retro-and-code-review-track-splits.md`:

````markdown
## Changes

| # | Work item | Type | What changed | Spec-set effect |
| --- | --- | --- | --- | --- |
| C1 | `plans/202608071455_retro-status-track-split/index.md` | new feature | a retrospective is now its own artifact with its own status track; a plan reaches `done` and stays there, and the retro queue is read off plan frontmatter | `features.md`: new capability *retro track* under the review group; `targets.md`: README's hand-maintained Statuses narrative no longer matches |
| C2 | `plans/202608072133_learn-targets-consolidation/index.md` | refactoring | a lesson is addressed with a `targets:` list — playbook, step, agent or skill — instead of living in a per-surface file; an untargeted lesson injects nowhere | `features.md`: the *lessons* capability is reworded, none added |
| C3 | `plans/202608072133_learn-targets-consolidation/index.md` | chore | the invocation log moved to the vault root and is gitignored there | none — no surface describes it |
| C4 | `plans/202608081156_code-review-track-split/index.md` | new feature | code review is queued off plan frontmatter (`code_review: null`) rather than a dedicated status, so review and retro no longer compete for the same field | `features.md`: new capability *code-review queue*; `targets.md`: the docs site's lifecycle page describes the old status |
| C5 | `plans/20260805-12-35_frontmatter-query/index.md` | new feature | `booping query` reads vault frontmatter, so any config mapping can act as a query spec | `features.md`: new capability *frontmatter query* under the CLI group |

5 rows over 4 items — 3 new feature, 1 refactoring, 1 chore; no vision shift and no feature drop,
so the briefing stands. `features.md` is touched by 4 rows, `targets.md` by 2, `roles.md` and the
briefing by none.
````

A run whose scope holds a single item writes the same section with one row; an item that produced
nothing worth documenting still gets its `chore` row, with `none` in the spec-set column.

## Return Format

````markdown
## Changed:
- [UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md — `## Changes`, {n} rows over {m} items

## Notes:
- types: {n} vision shift, {n} new feature, {n} refactoring, {n} feature drop, {n} chore
- spec-set effect: {one clause per spec file any row touches, or `none`}
- read: {m} items in {m} sub-agents

## Questions:
````
