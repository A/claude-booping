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
  - the plans already in the vault, parked ones included — title, type and status of each
- **Value** — the whole run's framing settled before a single research token is spent: one
  restated problem, one task type, explicit in/out scope boundaries, the scope-challenge
  questions the user must answer, and the web-research decision recorded — plus a plan directory
  that exists from wave 1, so every later step has a stable place to write into. Duplicate work
  is caught here: a parked plan that already covers the request is adopted rather than
  re-created.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the framing filled into the machine's artifact (the
    first transition bootstrapped the file with the run status; intake preserves that
    frontmatter): request verbatim, restated problem, task type with its rationale, scope
    boundaries, scope-challenge questions, and the web-research decision — `requested` when the
    user asked for deep web research (in the request itself or explicitly), `not requested`
    otherwise. `research-web` executes that decision mechanically; it is never re-judged.
  - `[CREATED|UPDATED] plans/{slug}/plan.md` — identity frontmatter only, no body: `title`,
    `type`, `status: in-spec`, `created`, and every other key of the plan frontmatter shape at
    its default (`sp: null`, `summary: ""`, the rest `null`). The body is `draft-plan`'s to
    write. `[UPDATED]` when the run was invoked on a parked plan the user named — the parked
    stub's content moves into the plan directory (the run slug is the stub's own filename stem),
    intake flips its `status:` from `backlog` to `in-spec` and refreshes `title` and `type`. No
    second plan is created.
  - nothing else — no research notes, no design, no milestones, no estimates
- **Step report** — `## Changed:` list, `## Notes:` carrying the chosen task type, the resolved
  plan path and the web-research decision, and `## Questions:` — the scope-challenge questions,
  numbered, each answerable in one line. A first pass always returns at least one: challenging
  scope is unconditional in groom. They come back empty on the re-run whose answers settle the
  framing.
- **Review gate** —
  - the user's answers to the scope questions are the confirmation — clear intent is enough, no
    separate explicit confirm is asked for
  - answers that change the task type, the restated problem or a boundary send the step back for
    another pass; otherwise the run moves on to research

## Example artifact

`plans/20260801-local-vault-directories/index.md`, after intake:

```markdown
---
status: framing
---
# Local vault directories — run index

## Framing

### Request

> I want the booping vault to be able to live inside the repo instead of ~/Claude, so a plan
> can be committed on the same branch as the code it plans.

### Restated problem

Today the vault path is fixed at `{home}/Claude/{project}/`, so plans live outside the repo they
describe and cannot travel on a feature branch with the code. The request is to make the vault
location per-repo, opt-in, with everything that resolves a vault path honouring the override.

### Task type

`feature` — a new user-facing capability with a business goal, a design and milestones. Not a
bug (nothing diverges from expected behaviour) and not a refactoring (the resolution behaviour
changes, not just its structure).

### Scope boundaries

**In scope**

- an opt-in marker that names the vault location, and the resolution order around it
- the scaffolding path that creates a repo-local vault
- keeping the default location working unchanged for every existing project

**Out of scope**

- migrating an existing vault from one location to the other
- anything about how plans are rendered or committed once the path resolves

### Web research

Not requested — the user did not ask for it.

### Scope challenge

- [ ] Does a repo-local vault need to be git-ignored, or is it meant to be committed?
- [ ] Should the scaffolding offer the location interactively, or only via a flag?
- [ ] Any new dependency or config surface you already know this must not pull in?
```

`plans/20260801-local-vault-directories/plan.md`, at the end of intake:

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

- [UPDATED] plans/20260801-local-vault-directories/index.md — framing
- [CREATED] plans/20260801-local-vault-directories/plan.md

## Notes:

- task type: feature
- plan: `plans/20260801-local-vault-directories/plan.md` (created)
- web research: not requested
- 3 scope question(s) open

## Questions:

1. Does a repo-local vault need to be git-ignored, or is it meant to be committed?
2. Should the scaffolding offer the location interactively, or only via a flag?
3. Any new dependency or config surface you already know this must not pull in?
```

Re-run that folds in the answers:

```markdown
## Changed:

- [UPDATED] plans/20260801-local-vault-directories/index.md — framing

## Notes:

- task type: feature (unchanged)
- plan: `plans/20260801-local-vault-directories/plan.md` (unchanged)
- boundaries narrowed: migration of an existing vault stays out of scope

## Questions:
```
