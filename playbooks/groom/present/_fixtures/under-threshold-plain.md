# Input — under-threshold-plain

Assemble the approval summary for this run and put it to the user. This is the first
presentation of the plan — no handoff has been written before.

## Run-time context

- project: `claude-booping` — the booping plugin repo, a uv Python project with a Jinja2
  rendering pipeline
- run slug: `20260801-plan-summary-frontmatter`
- run workdir: `_runs/groom/20260801-plan-summary-frontmatter/`, relative to the current
  working directory
- the current working directory **is the project vault**, and the vault lives **outside the
  repository being planned**: it is the default `~/Claude/claude-booping/`, the repo's `.booping`
  marker carries no `vault_path:` key, and nothing this run writes lands in the repo's working
  tree
- sizing thresholds in force this run: split threshold **35 SP**, re-decompose threshold **5 SP**
- run start: **2026-08-01 10:30 UTC**; this pass runs at **12:15 UTC**

## Inputs

- the drafted plan — `plans/20260801-plan-summary-frontmatter.md`, on disk; the
  decomposition pass left it untouched and the user confirmed it as drafted
- the confirmed design — `_runs/groom/20260801-plan-summary-frontmatter/design.md`, on disk
- the split threshold and the decomposition pass's outcome —
  `_runs/groom/20260801-plan-summary-frontmatter/decomposition.md`, on disk
- the reference-verification results —
  `_runs/groom/20260801-plan-summary-frontmatter/references.md`, on disk
- the cross-review outcome, as `draft-plan` returned it:

  > - cross-review: no `cross_review` agent configured — not run

- no earlier presentation of this plan — this is round one, and no change request has been made

## Context files

<file path="plans/20260801-plan-summary-frontmatter.md">
---
title: Plan summary line in frontmatter
type: feature
status: awaiting-plan-review
sp: 18
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: "The sprints snapshot says what each plan is for without opening it"
commit: null
---

# Plan summary line in frontmatter

## Context

**Current state** — `sprints.md` lists every plan by title and status. A title is a handle, not a
description, so working out what a plan is actually for means opening it.

**Motivation** — the snapshot is the one place the whole vault is visible at once, and it is the
least informative view of it.

**Scope** — a `summary:` frontmatter key, loaded with the rest of the plan's frontmatter and
rendered as a column in the snapshot. Not: back-filling summaries into existing plans, and not
any change to the snapshot's sort order or its other columns.

## Decisions

- **Key shape**: a single optional string, defaulting to `null` — a plan without one renders an
  empty cell rather than failing to load.
- **Where it is authored**: by the drafting step, alongside `sp:` — it describes the plan's
  intent, so it is written when the intent is settled.
- **Rendering**: a new column in the existing snapshot template; no second view.

## Architecture

`Plan` gains a `summary: str | None` field populated by the existing frontmatter loader, so no
parsing path changes. `sprints.md.j2` gains one column, truncated at render time rather than at
write time so the stored value stays whole.

## Milestones

### M1: Frontmatter key — 8 SP | pending

**Goal**: the key round-trips through the loader and the frontmatter writer with a null default.

**Verify**: `just test booping-python/tests/test_plan.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `summary` to the `Plan` model with a `None` default | `booping-python/src/booping/context/plan.py` | 3 | pending |
| 1.2 | Document the key in the plan frontmatter shape | `docs/template_plan_frontmatter.md` | 2 | pending |
| 1.3 | Loader tests: present, absent, empty string | `booping-python/tests/test_plan.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] A plan without `summary:` loads with `summary is None` rather than raising.
- [ ] `booping frontmatter-update` can set and remove the key.

#### Task 1.2 DoD

- [ ] The key, its type and its default are documented alongside the existing keys.

#### Task 1.3 DoD

- [ ] All three cases are asserted, and `just test` passes.

### M2: Snapshot column — 10 SP | pending

**Goal**: the rendered snapshot carries the summary for every plan that has one, and renders
cleanly for those that do not.

**Verify**: `just test booping-python/tests/test_render_sprints.py && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add the column to the snapshot template with render-time truncation | `src/templates/sprints.md.j2` | 4 | pending |
| 2.2 | Render tests over a vault mixing plans with and without the key | `booping-python/tests/test_render_sprints.py` | 3 | pending |
| 2.3 | Note the new column in the docs site's vault page | `documentation/vault.md` | 3 | pending |

#### Task 2.1 DoD

- [ ] A plan with no summary renders an empty cell, not the literal `None`.
- [ ] A long summary is truncated in the table and left whole in the plan file.

#### Task 2.2 DoD

- [ ] The mixed-vault case is asserted against the rendered output.

#### Task 2.3 DoD

- [ ] The page describes the column and where the value comes from.

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/context/plan.py` | the plan model and its frontmatter loader |
| `src/templates/sprints.md.j2` | the snapshot template |
| `docs/template_plan_frontmatter.md` | the documented frontmatter shape |

## Final Verification

- [ ] A vault mixing plans with and without summaries renders without error.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Back-filling summaries into plans that predate the key.
- Any change to the snapshot's sort order or its existing columns.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Project vault layout` | name the new frontmatter key | M1.2 |
</file>

<file path="_runs/groom/20260801-plan-summary-frontmatter/design.md">
---
reviewed_at: 20260801 11:20
---
# design — 20260801-plan-summary-frontmatter

## Approach

One optional `summary:` string on the plan's frontmatter, loaded by the existing frontmatter
loader into a nullable field on the plan model, and rendered as one extra column in the snapshot
template. Truncation happens at render time so the stored line stays whole. Nothing else about
the snapshot changes — same rows, same order, same other columns.

## Surface changes

- **Frontmatter** — a new optional `summary` key, default `null`, documented with the rest of
  the shape.
- **Model** — `Plan.summary: str | None`, populated by the loader that already reads the
  frontmatter; no new parsing path.
- **Template** — one column in `sprints.md.j2`, truncated for display.
- **Docs** — the frontmatter shape doc and the docs-site vault page.

## Alternatives

- **A separate description file per plan** — rejected: a second file to keep in sync with the
  plan, and invisible in Obsidian's Properties view.
- **Deriving the summary from the plan's first paragraph** — rejected: the first paragraph is
  written for a reader who has already opened the plan, and it drifts as the plan is revised.

## Trade-offs

- **Truncate at write time or at render time** — truncating on write keeps the template simple
  but loses the whole line; truncating on render keeps the stored value whole at the cost of one
  filter in the template. — **Settled:** truncate at render time.
- **Required or optional key** — requiring it would make every snapshot row informative but
  breaks every plan already in the vault. — **Settled:** optional, defaulting to null.

## Risks

- A very long summary could push the snapshot table past a readable width — mitigated by the
  render-time truncation.
- A plan file predating the key must still load — mitigated by the null default and a loader
  test over the absent case.
</file>

<file path="_runs/groom/20260801-plan-summary-frontmatter/decomposition.md">
---
reviewed_at: 20260801 11:52
---
# Decomposition — 20260801-plan-summary-frontmatter

## Verdict

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 4 SP), and the
sprint totals 18 SP, under the 35 SP split threshold, so no split candidate is flagged. The plan
file was not touched.
</file>

<file path="_runs/groom/20260801-plan-summary-frontmatter/references.md">
# references — 20260801-plan-summary-frontmatter

## Verdict

Verified — 2 references checked, 0 corrected, 0 unverifiable.

## Checked

| Reference | Named in | Plan claims | Upstream | Verdict | Source (checked 20260801) |
| --------- | -------- | ----------- | -------- | ------- | ------------------------- |
| Jinja2 `truncate` filter | M2.1 · render-time truncation | the filter takes a length and a `killwords` flag | signature is as the plan names it | ok | https://jinja.palletsprojects.com/en/stable/templates/ |
| Obsidian Properties typing | M1.2 · documented frontmatter shape | an absent key shows as an empty property rather than an error | matches the documented behaviour | ok | https://help.obsidian.md/Editing+and+formatting/Properties |
</file>
