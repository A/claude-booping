---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# survey

## Contract

- **Needs** —
  - which of the four spec-set files exist — briefing, roles, surfaces, feature index — and,
    for each one present, whether it is structurally complete or missing sections its own
    contract requires
  - the project's delivered work items, each with its status and the date it landed
  - the ledger of work already documented — which items earlier runs covered, and the run
    record that covered each
- **Value** — the run's cheap opening: two facts settled before a single expensive read
  happens, and a run record on disk to carry them. **How much of the spec set is usable** is
  judged by shape alone — `missing`, `incomplete`, `present` — never by whether the content
  looks dated; content drift is the change table's business, and the same vocabulary is what
  the exit edges read (`the survey found no missing or incomplete spec file`). **What shipped
  without documentation** is the delivered items minus the ledger's rows, so an old postponed
  item developed late surfaces in the run after it lands, not never. Nothing beyond identity,
  status, date and a one-line headline is taken from a work item — reading them is `research`'s
  job, in its own sub-agents. The two reports must be decisive enough for the runner to see
  which of the three routes out of the scope gate the user's answer will take: some spec file
  needs work, the spec set is current and the spec waves are skipped, or there is nothing to do
  at all. A re-survey after a scope answer that asked for a different item range or for spec
  files the first pass did not inspect rewrites the same run record — a run has exactly one.
  The record is also the run's memory: it opens an empty `## Scope` the runner fills with the
  confirmed answer at the gate, so a run resumed at `briefing` or `researching` in a later
  session recovers the item range from the artifact instead of a context that is gone.
- **Output files** —
  - `[CREATED|UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md` — the run record, opened with
    `## Spec set`, `## Undocumented work`, and a `## Scope` holding one placeholder line the
    runner replaces at the gate — this step never writes into it, having no confirmed answer
    to write, and a re-survey leaves whatever the section already holds.
    `{YYYYMMDDHHmm}` is the clock at open;
    `{title}` is a kebab headline for the undocumented set as a whole (`nothing-to-document`
    when it is empty). Frontmatter carries `title:` and nothing else — `status:` is
    `playbook-transition`'s, `started:` and `commit:` the surveying edge's hooks', and every
    later stamp its own edge's.
  - nothing else is written: `_specs/` is read-only to this step, the ledger
    `_specs/documented.md` is appended by the `close-documented` hook at `record`, and no work
    item's own file is touched.
- **Harness return** — the standard block. `## Changed:` names the run record alone.
  `## Notes:` carries the spec-set verdict as one clause per file, the undocumented count with
  its date range, and the route the findings point at — the runner asks the scope gate from
  those three lines plus the record itself. `## Questions:` is always empty: the scope question
  is the runner's gate, not the step's, and the step never asks for a decision it would only
  hand back.
- **Review gate** —
  - confirm the run scope — which spec files to refresh, which delivered items to cover
  - the gate is the runner's, taken after the return lands and asked against the run record's
    two tables; a `present` spec file may still be picked for a refresh, and an undocumented
    item may still be dropped from scope
- **Delegation** — detached; generic sub-agent at `opus-5:medium`. The sweep reads four spec
  files, the delivered items' frontmatter and the ledger, and none of that belongs in the
  driving context — only the two tables and the return come back.

## Example artifact

`{vault}/docs/202608081352-retro-and-code-review-track-splits.md`, as opened:

````markdown
---
title: Retro and code-review track splits
---

# Retro and code-review track splits

## Spec set

| File | State | Gap |
| --- | --- | --- |
| `_specs/index.md` — briefing | present | — |
| `_specs/roles.md` | present | — |
| `_specs/targets.md` | incomplete | no entry for `CHANGELOG.md`, which this playbook introduces |
| `_specs/features.md` | missing | never written |

2 of 4 usable — `targets` and `features` need the spec waves; briefing and roles are complete
and are refreshed only if the scope answer asks for it.

## Undocumented work

| Work item | Status | Landed | Headline |
| --- | --- | --- | --- |
| `plans/202608071455_retro-status-track-split/index.md` | done | 2026-08-07 | retro artifact split off the plan lifecycle into its own status track |
| `plans/202608072133_learn-targets-consolidation/index.md` | done | 2026-08-08 | lessons addressed by `targets:` instead of per-surface files |
| `plans/202608081156_code-review-track-split/index.md` | done | 2026-08-08 | code review queued off plan frontmatter rather than a status |
| `plans/20260805-12-35_frontmatter-query/index.md` | done | 2026-07-29 | `booping query` over vault frontmatter — postponed, delivered late |

4 items sit outside the ledger, landing 2026-07-29 → 2026-08-08. `_specs/documented.md` holds
11 rows, most recently `plans/202608061007_testing-ci-snapshots-mdcheck/index.md`.

## Scope

_Not yet confirmed — the runner writes the settled scope here at the scope gate._
````

A first run finds every spec file `missing` and writes the same three sections — the spec-set
table reading `missing` four times, with the prose line saying the whole set has to be
established. A run with an empty undocumented set keeps the heading and writes one line under
it (`nothing has landed since the ledger's last row`), so the scope gate can close the run.
`## Scope` is written identically in every case: heading plus the one placeholder line.

## Return Format

````markdown
## Changed:
- [CREATED|UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md

## Notes:
- spec set: {n} of 4 usable — {one clause per file: name, state, the gap when not present}
- undocumented: {n} items outside the ledger, {earliest} → {latest}
- route: {spec waves needed | spec set current, straight to research | nothing to do}

## Questions:
````
