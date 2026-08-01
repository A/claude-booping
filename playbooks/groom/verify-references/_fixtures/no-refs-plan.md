# Input — no-refs-plan

The plan below was refined by `decompose-work` and confirmed by the user at the decomposition
gate. Check every external reference it names against current upstream documentation, correct
what is wrong, and write the step's artifact into the run workdir.

## Run-time context

- project: `claude-booping` (the booping plugin repo)
- run slug: `20260801-09-40_extract-playbook-section-builders`
- run workdir: `_runs/groom/20260801-09-40_extract-playbook-section-builders/`, relative to the
  current working directory
- plan file: `plans/20260801-09-40_extract-playbook-section-builders.md`, on disk and inlined
  below

## Inputs

- the confirmed, decomposed plan — the file at the path above
- the decomposition record for the run, with its confirmation stamp
- current upstream documentation for every external reference the plan names — the vendor's own
  docs, release notes, changelogs and package registries, read now rather than recalled

## Context files

<file path="plans/20260801-09-40_extract-playbook-section-builders.md">
---
title: Extract the playbook section builders into their own module
type: refactoring
status: awaiting-plan-review
sp: 8
split_from: null
created: 2026-08-01
planned: 20260801 09:58
started: null
completed: null
retro: null
goal: null
summary: "Playbook rendering keeps working exactly as today, from code that is testable piece by piece"
commit: 7d40c1beaf95260381cd7fb4e05a9c2318bd6e74
---

# Extract the playbook section builders into their own module

## Context

**Current state** — `booping-python/src/booping/commands/render_playbook.py` both composes the
rendered procedure and builds every piece of it: the wave list, the mermaid graph, the subgraph
intros and each step section. The lesson-injection helper exists twice, once there and once in
`booping-python/src/booping/context/playbook.py`.

**Motivation** — every change to one section's shape reaches for the same 400-line module, and the
only test that covers a builder is the end-to-end composed-output test, so a builder bug surfaces
as a diff over the whole document.

**Scope** — moving code and adding tests around the seam. Not: changing rendered output, the
command's arguments, or the discovery rules.

## Decisions

- **Seam**: builders take resolved data and return strings; the command keeps every read, every
  problem notice and the ordering. Nothing that touches the filesystem moves.
- **Duplicate helper**: the copy in `context/playbook.py` is deleted rather than kept in sync — the
  context layer imports the moved one.

## Architecture

A new `booping-python/src/booping/render/playbook_sections.py` holds the wave-list, mermaid,
subgraph-intro, step-section and lesson-injection builders, each a module-level function over
already-resolved arguments. `commands/render_playbook.py` keeps loading, problem collection and
ordering, and composes the document from those calls. `context/playbook.py` imports the lesson
helper instead of carrying its own copy.

## Milestones

### M1: Move the builders — 5 SP | pending

**Goal**: the builders live in their own module and the command composes from them, with rendered
output unchanged.

**Verify**: `just test`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Move the wave-list, mermaid, subgraph-intro and step-section builders into the new module and call them from the command | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/render/playbook_sections.py` | 3 | pending |
| 1.2 | Move the lesson-injection helper beside them and drop the duplicate in the context layer | `booping-python/src/booping/render/playbook_sections.py`, `booping-python/src/booping/context/playbook.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] `booping render-playbook groom` produces output byte-identical to the pre-refactor run,
      composed section for composed section.
- [ ] No builder reads the filesystem or the playbook roots — each takes resolved arguments only.
- [ ] `just test` passes.

#### Task 1.2 DoD

- [ ] Exactly one lesson-injection helper exists in the package; the context layer imports it.
- [ ] `booping render-playbook groom --step design` still appends the same lesson block.
- [ ] `just test` passes.

### M2: Lock the seam with tests — 3 SP | pending

**Goal**: each builder is covered on its own, with the composed-output test left as the single
end-to-end case.

**Verify**: `just test && just lint && just typecheck`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Cover each moved builder directly, including the wave list for a subgraph-bearing graph and a step section with no declared inputs | `booping-python/tests/test_playbook_sections.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] Every function in the new module has at least one direct test.
- [ ] The composed-output test is unchanged and still passes.
- [ ] `just test && just lint && just typecheck` is clean.

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/commands/render_playbook.py` | loads, collects problems, orders and composes |
| `booping-python/src/booping/render/playbook_sections.py` | new home for the section builders |
| `booping-python/src/booping/context/playbook.py` | loses its duplicate lesson helper |
| `booping-python/tests/test_playbook_sections.py` | new per-builder tests |

## Final Verification

- [ ] `booping render-playbook groom` and `booping render-playbook groom --step design` produce
      output identical to the pre-refactor run.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- The rendered document's shape, the command's arguments and the discovery rules.
- The playbook driving partial and the skills that include it.
</file>

<file path="_runs/groom/20260801-09-40_extract-playbook-section-builders/decomposition.md">
---
reviewed_at: 20260801 09:58
---
# Decomposition — 20260801-09-40_extract-playbook-section-builders

## Verdict

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 3 SP), and the
sprint totals 8 SP, well under the 35 SP split threshold. The plan file was not touched.
</file>
