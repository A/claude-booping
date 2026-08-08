---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

# intake

[← index](../../index.md)

## Contract

- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.
- **Needs** —
  - the user's request, verbatim
  - the user's answers to the scope questions a previous pass returned, when this is a re-run
  - the task-type catalogue and the per-type guidance for the type that matches
  - the project's own conventions
  - the recent plans in the vault — status, title and summary of each — so a request that a
    parked or existing plan already covers is caught
- **Value** — the whole run's framing settled before a single research token is spent: one
  restated problem, one task type, explicit scope decisions, and the scope-challenge
  questions the user must answer — plus a plan directory that exists from wave 1, so every
  later step has a stable place to write into. Duplicate work is caught here: a parked plan
  that already covers the request is adopted rather than re-created.
- **Output files** —
  - `[CREATED] plans/{slug}/request.md` — the framing brief, also posted verbatim in chat
    (both carry the same block): the request as a blockquote, character-for-character; the
    task type with the rationale that rules each sibling type out by name; the problem —
    what the system does today and what must change, in the request's own domain terms; and
    the clarifications and decisions settled with the user, one line each. The slug is
    `{YYYYMMDDHHMM}_{kebab-title}`.
  - `[CREATED|UPDATED] plans/{slug}/index.md` — the plan document, identity frontmatter
    only, no body: `title`, `type`, `created`, and every other key of the plan frontmatter
    shape at its default (`sp: null`, `summary: ""`, the rest `null`). `status:` is the run
    machine's — bootstrapped by the first transition and never written here — and the
    lifecycle mirror `plan_status:` is stamped by the edge scripts, not by intake. The body
    is `draft-plan`'s to write. `[UPDATED]` when the run was invoked on a parked plan the
    user named — the parked stub's content moves into the plan directory, its lifecycle
    resumes from `backlog`, and `title` and `type` are refreshed. No second plan is created.
  - nothing else — no research notes, no design, no milestones, no estimates
- **Step report** — the brief posted in chat, closed by `## Notes:` carrying the chosen task
  type and the resolved plan directory, and `## Questions:` — the scope-challenge questions,
  numbered, each answerable in one line. A first pass always returns at least one:
  challenging scope is unconditional in groom. They come back empty on the re-run whose
  answers settle the framing.
- **Review gate** —
  - the user's answers to the scope questions are the confirmation — clear intent is enough, no
    separate explicit confirm is asked for
  - answers that change the task type, the restated problem or a boundary send the step back for
    another pass; otherwise the run moves to `researching`

## Example artifact

`plans/20260801-14-30_local-vault-directories/request.md`, after intake:

```markdown
# Local vault directories — request

## Request

> I want the booping vault to be able to live inside the repo instead of ~/Claude, so a plan
> can be committed on the same branch as the code it plans.

## Task type

`feature` — a new user-facing capability with a business goal, a design and milestones. Not a
bug (nothing diverges from expected behaviour) and not a refactoring (the resolution behaviour
changes, not just its structure).

## Problem

Today the vault path is fixed at `{home}/Claude/{project}/`, so plans live outside the repo they
describe and cannot travel on a feature branch with the code. The request is to make the vault
location per-repo, opt-in, with everything that resolves a vault path honouring the override.

## Clarifications and Decisions

- In scope: an opt-in marker naming the vault location, the resolution order around it, and the
  scaffolding path that creates a repo-local vault.
- Out of scope: migrating an existing vault from one location to the other.
- The default location keeps working unchanged for every existing project.
```

`plans/20260801-14-30_local-vault-directories/index.md`, at the end of intake (the run
machine's `status:` was bootstrapped by the first transition; intake preserves it):

```markdown
---
status: framing
title: Local vault directories
type: feature
sp: null
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: ""
commit: null
---
```

## Return Format

First pass:

```markdown
## Changed:

- [CREATED] plans/20260801-14-30_local-vault-directories/request.md — framing brief
- [CREATED] plans/20260801-14-30_local-vault-directories/index.md

## Notes:

- task type: feature
- plan: `plans/20260801-14-30_local-vault-directories/index.md` (created)
- 3 scope question(s) open

## Questions:

1. Does a repo-local vault need to be git-ignored, or is it meant to be committed?
2. Should the scaffolding offer the location interactively, or only via a flag?
3. Any new dependency or config surface you already know this must not pull in?
```

Re-run that folds in the answers:

```markdown
## Changed:

- [UPDATED] plans/20260801-14-30_local-vault-directories/request.md — decisions folded in

## Notes:

- task type: feature (unchanged)
- plan: `plans/20260801-14-30_local-vault-directories/index.md` (unchanged)
- boundaries narrowed: migration of an existing vault stays out of scope

## Questions:
```
