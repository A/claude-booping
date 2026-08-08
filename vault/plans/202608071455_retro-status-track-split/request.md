# Framing brief

## Request

> can we update retro playbook, so it takes plan, but keeps its state on ./retrospective/{datetime}-{title}.md file, keep its status there and link retro to a plan with frontmatter `retro` field. Also develop moves plan into `done` status. awaiting retro/learing will be retro statuses, in parallel with plan status. Motivation: 80% of developed plans ends in awaiting retro now, but technically it means done, I want to split this into a separate track to not burry plans in awaiting-retro statuses. After we pilot this change - we'll add same flow for codereview (out of scope, but i want to take into account how it will be developed after implementation).

## Task type

`feature` — new capability: retro lifecycle moves to its own artifact track with plan linkage, and the develop machine's terminal handoff changes. Not `bug`: nothing diverges from its specified behavior — the current chaining works as designed; the complaint is a design limitation. Not `refactoring`: the change is user-visible — plan statuses end at `done` after develop, retros carry their own `awaiting-retro`/`awaiting-learning` statuses, and a new `retro:` frontmatter link appears.

## Problem

Today the shipped playbooks chain their state machines through one artifact — the plan's `index.md`. `develop` ends a sprint at `awaiting-retro`, `retro` moves it to `awaiting-learning`, `learn` finally writes `done`. In practice ~80% of developed plans sit at `awaiting-retro`: development is finished, but the plan listing buries them under a status that really means "done, retro pending". The retro/learn tail should become its own track: `develop` closes the plan at `done`; the `retro` playbook takes a plan as input but persists its run state on a retrospective artifact (`retrospectives/{datetime}-{title}.md` in the vault), which carries `awaiting-retro` → `awaiting-learning` → its own terminal; the plan links to it via a `retro:` frontmatter field. `code-review` gets the same treatment later — out of scope, but the design must leave that seam open.

## Clarifications and Decisions

- Retro artifact: `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — existing scaffold dir, slug matches plan convention, single file is the run artifact.
- Retro queue: query plans with `status: done` + `retro: null` — no stub creation; develop changes only its terminal status.
- Learn moves fully to the retro track: queries retrospectives at `awaiting-learning`, closes the retro artifact to `done`; plan untouched by learn.
- Migration 003 ships: plans at `awaiting-retro`/`awaiting-learning` move to `done`, retrospective stubs backfilled at matching status with `retro:` links.
- Retro artifact carries a `plan:` frontmatter back-link to its plan.
- No post-implementation reshape milestone — declared out of scope.
- code-review same-pattern follow-up is out of scope, but the design keeps the seam open (artifact-track pattern must be reusable).
