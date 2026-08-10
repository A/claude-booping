# groom playbook

Spec a sprint: take a rough request and produce a reviewable plan under `~/Claude/{project}/plans/{slug}/` — an `index.md` plus one file per milestone under `milestones/`, carrying tasks, story points, and definitions of done.

Grooming is a **playbook**, not a skill — it is driven by [`/playbook`](playbook.md):

```text
/playbook groom
```

## What it does

Run states: `framing` → `researching` → `drafting` → `cross-reviewing` → `presenting` → `awaiting-approval` → `ready-for-dev`. Two loopbacks: `drafting → researching` when the design needs blast radius the research pass missed, and `awaiting-approval → drafting` when your change request touches the plan itself.

Almost every step runs in your session — inline, or assisted (heavy reads go to the research agent, which returns a bounded summary). The exception is `cross-review`, which hands the drafted plan to a second-model reviewer and does nothing unless you name one. `present` is the run's single approval gate.

The output is a plan directory `~/Claude/{project}/plans/{slug}/`. Its `index.md` carries the approach, the scope and the YAML frontmatter the rest of the loop (`develop`, `retro`, `learn`) reads; each milestone is a file of its own under `milestones/`, and that file — not a section of the index — is what develop hands a coding agent as its contract. `index.md`'s `## Milestones` table and the plan's total story points are generated from those files, never hand-kept. Groom creates the directory with one `booping scaffold` call from a config-declared tree, so the fresh `index.md` arrives complete — including a real `commit:` stamped with repo HEAD at creation, and `draft-plan` scaffolds each milestone file the same way. The intake briefing and any web-research notes land beside it. The directory doubles as the run workdir, so a groom run is **resumable**: its run state lives in the same `index.md`.

A plan is always a directory: `core.plans.glob` resolves `plans/*/index.md` and nothing else, and `core.plans.milestones.glob` resolves the milestone files inside it. A vault still holding flat `plans/{slug}.md` files converts them with `/playbook migrate`.

Six steps, in dependency order:

| Step | What it does |
|------|--------------|
| `intake` | Clarify the request, settle scope, scaffold the plan directory — briefing, identity frontmatter, `commit:` at repo HEAD — with one `booping scaffold` call |
| `research-codebase` | Map the blast radius — files, modules, integrations, prior art (assisted: heavy reads go to the research agent) |
| `research-web` | Check external practice where the design is uncertain, and verify package versions, image tags, API endpoints and CLI flags against current docs |
| `draft-plan` | Design with you in conversation, then write the plan against a plan template — `index.md` plus one milestone file each |
| `cross-review` | Hand the drafted plan to a second-model reviewer for severity findings — skipped unless `core.groom_playbook.cross_review_agent` names one (unset by default) |
| `present` | Present approach, milestones and SP totals; the run's single approval gate |

Refinement and decomposition happen inside `draft-plan`.

## Starting a run

```text
/playbook groom
```

Bare invocation picks up whatever you have been discussing in the current session. Name a parked plan or an existing draft to keep iterating on it:

```text
/playbook groom — continue plans/202604301120_documentation-site/index.md, here's feedback to address
```

Everything you say in the invocation reaches `intake` verbatim.

## Best practices

### More detail in the prompt = sharper plan

The playbook works from your request, the codebase, and accumulated lessons. The request is the only knob fully under your control — the more concrete it is, the less the run has to guess.

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

### Free-text extras

Useful things to mention up front:

- **Reference a template** — "use the bug-investigation template" selects a specific plan template.

Branch selection is **not** groom's job — the [develop playbook](develop.md)'s `provision` step picks and confirms it.

### Define your own plan templates

Drop `*.md` files into `~/Claude/{project}/plan_templates/` to extend or override the templates that ship with the plugin. Each template needs frontmatter (`name`, `description`) and two top-level sections (`# Plan Body`, `# Quality Checklist`). A project-local template with the same `name` as a core template overrides it.

See [Vault](vault.md) for the directory layout.

## Reviewing the plan

What to check before approving at `present`, the run's **only** review gate:

- **Goal is sharp.** The `summary` in frontmatter matches the request, with no scope creep.
- **Milestones cover the goal end-to-end.** No silent gaps, no "and then ..." vagueness in the last milestone.
- **Tasks are sized honestly.** No 5-SP tasks except deliberate research spikes (see Story points).
- **Definitions of done are verifiable.** Each DoD checkbox is mechanically confirmable — not "code looks good".

Approve explicitly ("looks good", "ship it") to move the plan to `ready-for-dev`, groom's terminal status and the queue the [develop playbook](develop.md) claims from. A change request touching architecture, scope, milestones, tasks or estimates sends the run back to `drafting`.

## Story points

booping uses a 1–5 scale for per-task estimates, set in `src/config.yaml`:

- **1** — Simple text/config change, no risk.
- **2** — Simple task, predictable, no risk.
- **3** — Medium task, minor risks but predictable overall.
- **4** — Complex task, medium risk, may need small research but clear enough.
- **5** — Research task — the developer needs to clarify and decompose further before proceeding.

Two thresholds drive the playbook's behaviour, both configurable:

- **`core.sprint.default_threshold_sp` (default `35`)** — soft cap on plan size. Above this, `present` proposes splitting the plan into sibling stubs rather than shipping one mega-sprint.
- **`core.sprint.redecompose_threshold` (default `5`)** — any task estimated at ≥ this value must be re-decomposed before the run can leave `drafting`.

Both thresholds are ceilings, not velocity targets. A 12-SP plan is fine; a 38-SP plan is the trigger to consider a split.

## Config

The playbook reads these keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`core.sprint.default_threshold_sp`** — soft cap on total SP per plan; above this the run proposes a split.
- **`core.sprint.redecompose_threshold`** — per-task SP value at or above which the task must be re-decomposed.
- **`core.sprint.scale`** — the 1–5 SP definitions (each a `{sp, meaning}` entry).
- **`core.task_types`** — list of `{type, description, doc_uri}` entries (`feature`, `bug`, `refactoring`). The request is classified against this list; the matching `doc_uri` lazy-loads detailed guidance for that task type.
- **`core.groom_playbook.cross_review_agent`** — the agent that cross-reviews the drafted plan. `null` by default, which skips the `cross-reviewing` step entirely.
- **`core.research_agent`** — the agent assisted steps hand their bulk reads to (default `booping:booping-researcher`). Shared across playbooks, so it sits directly under `core`.
