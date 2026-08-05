# groom playbook

Spec a sprint: take a rough request and produce a reviewable plan under `~/Claude/{project}/plans/{slug}/index.md` with milestones, tasks, story points, and definitions of done.

Grooming is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook groom
```

## What it does

The playbook walks a request through the early lifecycle states — `backlog` or fresh request → `in-spec` → `awaiting-plan-review` → `ready-for-dev`. The output is a plan directory whose `index.md` carries YAML frontmatter that the rest of the loop (`develop`, `retro`, `learn`) reads. The plan directory doubles as the playbook's run workdir, so a groom run is **resumable**: its run state lives in the same `index.md`.

Six steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Clarify the request, settle scope, create the plan directory and its identity frontmatter |
| `research-codebase` | Map the blast radius — files, modules, integrations, prior art (heavy reads delegated to `booping-researcher`) |
| `research-web` | Verify package versions, image tags, API endpoints and CLI flags against current docs |
| `draft-plan` | Design with you in conversation, then write the plan body against a plan template |
| `cross-review` | Second-model review of the written plan; findings only, no writes (skipped when no reviewer is configured) |
| `present` | Present approach, milestones and SP totals; the run's single review gate |

Design work happens in conversation inside `draft-plan` — refinement and decomposition are part of drafting, not separate steps.

## Starting a run

```text
/playbook groom
```

Bare invocation picks up whatever you have been discussing in the current session. Name a parked plan or an existing draft to keep iterating on it:

```text
/playbook groom — continue plans/20260430-11-20_documentation-site/index.md, here's feedback to address
```

Everything you say in the invocation reaches `intake` verbatim.

## Best practices

### More detail in the prompt = sharper plan

The playbook works from your request plus the codebase plus accumulated lessons. The request is the only knob fully under your control, so the more concrete it is, the less the run has to guess.

Brief request — lots of room for misalignment:

```text
/playbook groom — add rate limiting
```

Detailed request — sharply scoped, fewer rounds of revision:

```text
/playbook groom — add per-IP rate limiting to the /api/* routes in apps/api/.
Use Redis (already a dep). 100 req/min default; configurable via env.
Return 429 with Retry-After. No new middleware framework — extend the
existing one in apps/api/middleware/.
```

The detailed version costs you 30 seconds of typing and saves a full revision cycle.

### Free-text extras

Useful things to mention up front:

- **Stop after each milestone** — tell the develop playbook (later) to pause between milestones for review; groom records this as a plan note.
- **Search the web** — ask for package versions, image tags, or API endpoints to be verified against current docs before drafting.
- **Reference a template** — "use the bug-investigation template" selects a specific plan template.

Branch selection is **not** groom's job: the branch is picked and confirmed by the [develop playbook](develop.md)'s `provision` step.

### Define your own plan templates

Drop `*.md` files into `~/Claude/{project}/plan_templates/` to extend or override the templates that ship with the plugin. Each template needs frontmatter (`name`, `description`) and two top-level sections (`# Plan Body`, `# Quality Checklist`). A project-local template with the same `name` as a core template overrides it.

See [Vault](vault.md) for the directory layout.

## Reviewing the plan

`present` is the run's **only** review gate. The plan is not yet ready for development — you are the gate.

What to check before approving:

- **Goal is sharp.** The `summary` in frontmatter matches the request, with no scope creep.
- **Milestones cover the goal end-to-end.** No silent gaps, no "and then ..." vagueness in the last milestone.
- **Tasks are sized honestly.** No 5-SP tasks except deliberate research spikes (see Story points).
- **Definitions of done are verifiable.** Each task DoD checkbox is something you can mechanically confirm — not "code looks good".
- **Cross-review findings are addressed.** Every `CRITICAL` finding is folded into the plan or recorded as an explicit deferral in the Risk register.

Approve explicitly ("looks good", "ship it") to move the plan to `ready-for-dev`. A change request loops the run back to the step that owns what it touches — any change to architecture, scope, milestones, tasks or estimates sends it back to `drafting`.

## Story points

booping uses a 1–5 scale for per-task estimates, rendered into the playbook from `src/config.yaml`:

- **1** — Simple text/config change, no risk.
- **2** — Simple task, predictable, no risk.
- **3** — Medium task, minor risks but predictable overall.
- **4** — Complex task, medium risk, may need small research but clear enough.
- **5** — Research task — the developer needs to clarify and decompose further before proceeding.

Two thresholds drive the playbook's behaviour, both configurable:

- **`core.sprint.default_threshold_sp` (default `35`)** — soft cap on plan size. Above this, `present` proposes splitting the plan into sibling stubs rather than shipping one mega-sprint.
- **`core.sprint.redecompose_threshold` (default `5`)** — any task estimated at ≥ this value must be re-decomposed before the plan can leave `in-spec`.

Both thresholds are ceilings, not velocity targets. A 12-SP plan is fine; a 38-SP plan is the trigger to consider a split.

## Cross-review

`cross-review` is a **detached** step: a second model reads the written plan and returns severity findings only — it never writes. The reviewer is whatever agent `core.cross_review_agent.agent` names in config; with no `cross_review` agent configured the step is skipped and the run advances straight past it.

Disposing of findings is the runner's job, before the run advances:

- **`CRITICAL`** — folded into the plan, or recorded as an explicit deferral in `## Risk register`.
- **`RISK`** — folded in unless it reopens a call you already settled.
- **`NOTE`** — at the runner's discretion.

A finding that reopens a settled design call is folded in nowhere — it sends the run back to `drafting`.

## Config

The playbook reads these keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`core.sprint.default_threshold_sp`** — soft cap on total SP per plan; above this the run proposes a split.
- **`core.sprint.redecompose_threshold`** — per-task SP value at or above which the task must be re-decomposed.
- **`core.sprint.scale`** — the 1–5 SP definitions (each a `{sp, meaning}` entry).
- **`core.task_types`** — list of `{type, description, doc_uri}` entries (`feature`, `bug`, `refactoring`). The request is classified against this list; the matching `doc_uri` lazy-loads detailed guidance for that task type.
- **`core.cross_review_agent`** — the agent that performs the detached cross-review; absent → the step is skipped.
- **`research_agent`** — the agent the two research steps delegate their bulk reads to (default `booping:booping-researcher`).
- **`core.groom_playbook.agents`** — the delegation table rendered into the playbook.
