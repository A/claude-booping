# Input — indexed plan store

The plan below was written by `draft-plan` against the `backend` template and cross-reviewed in
place; the user has not read it yet. Refine it against the sizing thresholds and write the
decomposition artifact into the run workdir.

## Run-time context

- project: `claude-booping` — the booping plugin repository; the vault it grooms into is the
  default `~/Claude/claude-booping/`
- run slug: `20260801-indexed-plan-store`
- run workdir: `_runs/groom/20260801-indexed-plan-store/`, relative to the current working
  directory — it already holds the confirmed framing, the blast-radius map and the confirmed
  design
- plan file: `plans/20260801-indexed-plan-store.md`, on disk, written and complete

## Inputs

- the written plan — `plans/20260801-indexed-plan-store.md`, on disk: 4 milestones,
  per-task and per-milestone story points, the sprint total mirrored in its `sp:` frontmatter
- the re-decompose threshold — **5 SP**: a task at or over it needs another pass before a single
  agent briefing can carry it
- the split threshold — **35 SP**: a sprint total past it should be proposed as two siblings
- the SP scale:
  - 1 — simple text/config change, no risk
  - 2 — simple task, predictable, no risk
  - 3 — medium task, minor risks but predictable overall
  - 4 — complex task, medium risk, may need small research but clear enough
  - 5 — research task: the developer would have to clarify and decompose it further before
    proceeding
- rework from the user: none — this is the run's first pass through decomposition

## Context files

<file path="plans/20260801-indexed-plan-store.md">
---
title: Indexed plan store
type: refactoring
status: in-spec
sp: 18
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Vault reads stay fast as a project's plan history grows past a few hundred plans"
commit: null
---

# Indexed plan store

## Context

**Current state** — every command that needs plans re-reads the whole `plans/` directory:
`Context.assemble()` globs `plans/*.md`, parses each file's frontmatter and builds `context.plans`.
`render-sprints`, `/chat`'s orient refresh and `transition`'s plan lookup each pay that scan.

**Motivation** — one vault has crossed 400 plans and a `booping transition` now spends most of its
wall time parsing files it never looks at. The scan is O(all plans) for operations that need one
plan or a summary row per plan.

**Scope** — introducing an on-disk index over the vault's plans, moving the read paths onto it, and
keeping it current on write. Not: changing the plan file format, the frontmatter keys, or what any
command outputs.

## Decisions

- **Markdown stays the source of truth**: the index is a derived cache — deleting it must cost
  nothing but a rebuild, so a corrupted or absent index is never a hard failure.
- **Rebuild on staleness, not on a watcher**: the store compares the index's recorded mtimes
  against the directory and rebuilds what drifted, so an index edited outside booping self-heals.
- **One reader type**: every caller goes through `PlanStore`; no command keeps a private path into
  `plans/`, or the cache and the directory drift apart per caller.

## Architecture

`booping-python/src/booping/context/store.py` gains `PlanStore`, holding the index at
`{vault}/_booping/plans.index.json`: one record per plan with its path, mtime and parsed
frontmatter. `PlanStore.all()` returns the summary rows `sprints.md` renders from; `PlanStore.get(path)`
returns one plan. `Context.assemble()` builds `context.plans` from `PlanStore.all()` instead of
globbing, and `transition` resolves its target through `PlanStore.get()`. The flat-file scan in
`context/plan.py` disappears once nothing calls it. Every command that writes a plan calls
`PlanStore.refresh(path)` before returning, so the next read is already warm.

## Milestones

### M1: The index and its schema — 4 SP | pending

**Goal**: an index can be built from a vault and detected as stale.

**Verify**: `just test booping-python/tests/test_store.py && just typecheck`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Index format, builder and atomic write | `booping-python/src/booping/context/store.py` | 2 | pending |
| 1.2 | Staleness detection and partial rebuild | `booping-python/src/booping/context/store.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] Building an index over a vault records path, mtime and parsed frontmatter per plan.
- [ ] The index is written atomically — an interrupted write leaves the previous index readable.
- [ ] An unparseable plan is recorded with its error rather than aborting the build.

**Verify**: `just test booping-python/tests/test_store.py::test_build`

#### Task 1.2 DoD

- [ ] A plan whose mtime moved is re-parsed; the rest are read from the index.
- [ ] A missing or corrupt index triggers a full rebuild instead of raising.
- [ ] A plan deleted from disk is dropped from the index on the next read.

**Verify**: `just test booping-python/tests/test_store.py::test_staleness`

---

### M2: Reads move to the store — 7 SP | pending

**Goal**: no command reads `plans/*.md` directly; all of them go through `PlanStore`.

**Verify**: `just test && rg -n "plans/\*\.md|glob\(" booping-python/src/booping/ | grep -v store.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Move plan reads from flat files to the indexed store | `booping-python/src/booping/context/plan.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/src/booping/commands/render_sprints.py`, `booping-python/src/booping/commands/transition.py` | 5 | pending |
| 2.2 | `debug-context` reports the index's source and freshness | `booping-python/src/booping/commands/debug_context.py` | 2 | pending |

#### Task 2.1 DoD

- [ ] `Context.assemble()` populates `context.plans` from `PlanStore.all()` rather than globbing
      `plans/*.md`.
- [ ] `render-sprints` renders from the store and produces a `sprints.md` byte-identical to today's
      for the same vault.
- [ ] `transition` resolves its target plan through `PlanStore.get()`, including for a plan created
      moments earlier in the same command.
- [ ] The flat-file scan in `context/plan.py` is deleted, and no module outside `store.py` touches
      `plans/` on a read path.
- [ ] A vault with no index on disk still serves every one of those reads on the first call.
- [ ] `just test` passes with the existing plan-loading tests unchanged.

**Verify**: `just test booping-python/tests/test_context.py booping-python/tests/test_render_sprints.py booping-python/tests/test_transition.py`

#### Task 2.2 DoD

- [ ] `booping debug-context` prints the index path, its record count and whether it was rebuilt on
      this call.
- [ ] It reports plans the index recorded as unparseable, with their errors.

**Verify**: `bin/booping debug-context | grep -A4 '^plan_store:'`

---

### M3: Writers keep the index current — 4 SP | pending

**Goal**: a command that writes a plan leaves the index warm behind it.

**Verify**: `just test booping-python/tests/test_store_refresh.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `frontmatter-update` and `transition` refresh the written plan's record | `booping-python/src/booping/commands/frontmatter_update.py`, `booping-python/src/booping/commands/transition.py` | 2 | pending |
| 3.2 | Refresh before the post hooks, so `render-sprints` sees the new status | `booping-python/src/booping/hooks.py` | 2 | pending |

#### Task 3.1 DoD

- [ ] Both commands call `PlanStore.refresh(path)` after their write and before returning.
- [ ] A refresh failure is logged and does not fail the command — the next read rebuilds.

**Verify**: `just test booping-python/tests/test_store_refresh.py`

#### Task 3.2 DoD

- [ ] The refresh runs before `plan.hooks.post`, so the `render-sprints` hook renders the status
      the transition just wrote.
- [ ] A transition and an immediate `render-sprints` produce the same table.

**Verify**: `just test booping-python/tests/test_transition.py::test_post_hooks_see_new_status`

---

### M4: Docs and cleanup — 3 SP | pending

**Goal**: the index is documented as a cache and the dead helpers are gone.

**Verify**: `just lint && just test`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Document the index, its location and how to discard it | `CLAUDE.md`, `documentation/vault.md` | 2 | pending |
| 4.2 | Delete the superseded loader helpers and their tests | `booping-python/src/booping/context/plan.py`, `booping-python/tests/test_plan_loader.py` | 1 | pending |

#### Task 4.1 DoD

- [ ] Both documents state that the index is derived and safe to delete.
- [ ] The vault-layout section names `_booping/plans.index.json`.

**Verify**: `just docs`

#### Task 4.2 DoD

- [ ] No unreferenced loader helper survives in `context/plan.py`.
- [ ] The tests that covered them are deleted, not skipped.

**Verify**: `just test && just lint`

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/context/store.py` | the index and the only module that touches `plans/` |
| `booping-python/src/booping/context/plan.py` | today's flat-file scan; shrinks to the parsed-plan type |
| `booping-python/src/booping/commands/transition.py` | the hottest single-plan read path |

## Final Verification

- [ ] A 400-plan vault renders `sprints.md` and runs a transition without re-parsing every file.
- [ ] Deleting the index file changes no output, only the first call's cost.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Changing the plan file format or any frontmatter key.
- A database of any kind — the index is a plain file, rebuilt from markdown.
- Indexing anything other than plans (retros, lessons, notes stay as they are).
</file>
