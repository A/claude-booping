---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

# intake

[← index](../../index.md)

## Contract

- **Needs** —
  - the user's request, verbatim
  - the user's answers to the scope questions a previous pass returned, when this is a re-run
  - the task-type catalogue and the per-type guidance for the type that matches
  - the project's own conventions
  - the plans already in the vault, parked ones included — title, type and status of each
- **Value** — the whole run's framing settled before a single research token is spent: one
  restated problem, one task type, explicit in/out scope boundaries, and the scope-challenge
  questions the user must answer — plus a plan file that exists from wave 1, so every later step
  has a stable path to write into. Duplicate work is caught here: a parked plan that already
  covers the request is adopted rather than re-created.
- **Output files** —
  - `[CREATED|UPDATED] _runs/groom/{slug}/intake.md` — the framing document: request verbatim,
    restated problem, task type with its rationale, scope boundaries, scope-challenge questions.
    Frontmatter carries `reviewed_at: null`, which the confirm edge stamps. `[UPDATED]` on a
    re-run that folds in the user's answers.
  - `[CREATED|UPDATED] plans/{slug}.md` — identity frontmatter only, no body: `title`, `type`,
    `status: in-spec`, `created`, and every other key of the plan frontmatter shape at its
    default (`sp: null`, `summary: ""`, the rest `null`). The body is `draft-plan`'s to write.
    `[UPDATED]` when the run was invoked on a parked plan the user named — the run slug is then
    that plan's own filename stem rather than a freshly minted one, so this path resolves to the
    existing file: intake flips its `status:` from `backlog` to `in-spec` and refreshes `title`
    and `type`. The parked file is never renamed and no second plan file is created.
  - nothing else — no research notes, no design, no milestones, no estimates
- **Harness return** — `## Changed:` list, `## Notes:` carrying the chosen task type and the
  resolved plan path, and `## Questions:` — the scope-challenge questions, numbered, each
  answerable in one line. A first pass always returns at least one: challenging scope is
  unconditional in groom. They come back empty on the re-run whose answers settle the framing.
- **Review gate** —
  - the user answers every scope-challenge question and confirms the task type and the scope
    boundaries; explicit confirmation, silence never counts
  - answers that change the task type, the restated problem or a boundary send the step back for
    another pass; a clean confirmation moves the run on to research

## Example artifact

`_runs/groom/20260801-14-30_local-vault-directories/intake.md`:

```markdown
---
reviewed_at: null
---
# Intake — local vault directories

## Request

> I want the booping vault to be able to live inside the repo instead of ~/Claude, so a plan
> can be committed on the same branch as the code it plans.

## Restated problem

Today the vault path is fixed at `{home}/Claude/{project}/`, so plans live outside the repo they
describe and cannot travel on a feature branch with the code. The request is to make the vault
location per-repo, opt-in, with everything that resolves a vault path honouring the override.

## Task type

`feature` — a new user-facing capability with a business goal, a design and milestones. Not a
bug (nothing diverges from expected behaviour) and not a refactoring (the resolution behaviour
changes, not just its structure).

## Scope boundaries

**In scope**

- an opt-in marker that names the vault location, and the resolution order around it
- the scaffolding path that creates a repo-local vault
- keeping the default location working unchanged for every existing project

**Out of scope**

- migrating an existing vault from one location to the other
- anything about how plans are rendered or committed once the path resolves

## Scope challenge

- [ ] Does a repo-local vault need to be git-ignored, or is it meant to be committed?
- [ ] Should the scaffolding offer the location interactively, or only via a flag?
- [ ] Any new dependency or config surface you already know this must not pull in?
```

`plans/20260801-14-30_local-vault-directories.md`, at the end of intake:

```markdown
---
title: Local vault directories
type: feature
status: in-spec
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

- [CREATED] _runs/groom/20260801-14-30_local-vault-directories/intake.md
- [CREATED] plans/20260801-14-30_local-vault-directories.md

## Notes:

- task type: feature
- plan: `plans/20260801-14-30_local-vault-directories.md` (created)
- 3 scope question(s) open

## Questions:

1. Does a repo-local vault need to be git-ignored, or is it meant to be committed?
2. Should the scaffolding offer the location interactively, or only via a flag?
3. Any new dependency or config surface you already know this must not pull in?
```

Re-run that folds in the answers:

```markdown
## Changed:

- [UPDATED] _runs/groom/20260801-14-30_local-vault-directories/intake.md

## Notes:

- task type: feature (unchanged)
- plan: `plans/20260801-14-30_local-vault-directories.md` (unchanged)
- boundaries narrowed: migration of an existing vault stays out of scope

## Questions:
```
