# /groom

Spec a sprint: take a rough request and produce a reviewable plan file under `~/Claude/{project}/plans/` with milestones, tasks, story points, and definitions of done.

## What it does

`/groom` walks a request through the early lifecycle states — `backlog` or fresh request → `in-spec` → `awaiting-plan-review` → `ready-for-dev`. The output is a single markdown plan file with YAML frontmatter that subsequent skills (`/develop`, `/retro`, `/learn`) read. Status transitions are manual frontmatter edits performed by `/groom` as it clears each gate; no CLI mutates them.

`/groom` does the research, drafts the milestones, estimates story points, optionally cross-validates against Gemini, and then hands the plan to you for explicit approval before it can move to `ready-for-dev`. Silence does not count as approval.

## Command

```text
/groom <free-text request, optionally referencing a parked plan>
```

Examples:

```text
/groom
/groom i want to refactor install and help skills to match other skills style
/groom plans/20260430-user-facing-documentation-site.md — we're continuing to shape this; here's feedback to address
/groom add current git commit hash to the booping CLI context, then add it to plan files; on /develop start, if the plan commit differs from repo HEAD, check git log between the two
```

Bare `/groom` picks up whatever you've been discussing in the current session. Pass a plan path to keep iterating on a draft you've already started.

The free-text body is read verbatim — anything you say there reaches the skill.

## Best practices

### More detail in the prompt = sharper plan

`/groom` works from your prompt plus the codebase plus accumulated lessons. The prompt is the only knob fully under your control, so the more concrete it is, the less the skill has to guess.

Brief prompt — lots of room for misalignment:

```text
/groom add rate limiting
```

Detailed prompt — sharply scoped, fewer rounds of revision:

```text
/groom add per-IP rate limiting to the /api/* routes in apps/api/.
Use Redis (already a dep). 100 req/min default; configurable via env.
Return 429 with Retry-After. No new middleware framework — extend the
existing one in apps/api/middleware/.
```

The detailed version costs you 30 seconds of typing and saves a full revision cycle.

### Free-text prompt extras

Anything you put in the prompt is read by the skill. Useful extras to mention up front:

- **Branch name** — `branch off feat/oauth-login` overrides the branch convention picked from `git.branches`.
- **Stop after each milestone** — tell `/develop` (later) to pause between milestones for review. `/groom` records this as a plan note.
- **Search the web** — ask the skill to verify package versions, image tags, or API endpoints against current docs before drafting.
- **Reference a template** — `/groom use the bug-investigation template for ...` selects a specific plan template.

### Define your own plan templates

Drop `*.md` files into `~/Claude/{project}/plan_templates/` to extend or override the templates that ship with the plugin. Each template needs frontmatter (`name`, `description`) and two top-level sections (`# Plan Body`, `# Quality Checklist`). A project-local template with the same `name` as a core template overrides it.

See [Vault](vault.md) for the directory layout.

## Reviewing the plan

When `/groom` enters `awaiting-plan-review` it presents the plan and waits for your verdict. The plan is not yet ready for development — you are the gate.

What to check before approving:

- **Goal is sharp.** The business goal in frontmatter matches the request, with no scope creep.
- **Milestones cover the goal end-to-end.** No silent gaps, no "and then ..." vagueness in the last milestone.
- **Tasks are sized honestly.** No 5-SP tasks except deliberate research spikes (see Story points).
- **Definitions of done are verifiable.** Each task DoD checkbox is something you can mechanically confirm — not "code looks good".
- **Cross-validation findings are addressed.** If Gemini ran, every **CRITICAL EXECUTION RISK** and **RULE VIOLATION** in its output is either applied or explicitly acknowledged in the Risk register.

Approve explicitly ("looks good", "ship it") to move the plan to `ready-for-dev`. Request changes to bounce back into `in-spec`.

## Story points

booping uses a 1–5 scale for per-task estimates. The scale is rendered into `/groom` itself from `src/config.yaml`, so the skill always estimates against the same definitions:

- **1** — Simple text/config change, no risk.
- **2** — Simple task, predictable, no risk.
- **3** — Medium task, minor risks but predictable overall.
- **4** — Complex task, medium risk, may need small research but clear enough.
- **5** — Research task — the developer needs to clarify and decompose further before proceeding.

Two thresholds drive `/groom`'s behaviour, both configurable in `src/config.yaml`:

- **`sprint.default_threshold_sp` (default `35`)** — soft cap on plan size. Above this, `/groom` proposes splitting the plan into sibling stubs rather than shipping one mega-sprint.
- **`sprint.redecompose_threshold` (default `5`)** — any task estimated at ≥ this value must be re-decomposed before the plan can leave `in-spec`. This is the gate that prevents silent research spikes from sliding into development.

Both thresholds are ceilings, not velocity targets. A 12-SP plan is fine; a 38-SP plan is the trigger to consider a split.

## Cross-validation

`/groom` can hand the drafted plan to Gemini for an outside review before presenting to you. This is **opt-in**: set `GEMINI_API_KEY` in your environment to enable. Without the key, cross-validation skips silently and the rest of the loop is unaffected.

Behaviour:

- **Runs once per plan**, after the first round of feedback. Iterative wording tweaks do not trigger re-runs; substantive scope changes may.
- **Advisory, not a CI gate.** The output is pasted to you verbatim under a "Gemini cross-validation" heading. You decide what to address.
- **Findings are categorised.** **CRITICAL EXECUTION RISK** and **RULE VIOLATION** must be applied before the plan can leave `in-spec`. **ARCHITECTURAL BLIND SPOT** may be deferred with explicit acceptance, recorded in the plan's Risk register.

`/groom` calls the validator blind — it never inspects the environment for the key. If the key is missing the call exits with code `2` and the skill reports "Gemini cross-validation skipped — `GEMINI_API_KEY` not set." and moves on.

## Config

`/groom` reads the following keys from `src/config.yaml`. See [Project config](project_config.md) for the deep-merge override mechanics; per-project tweaks live in `~/Claude/{project}/config.yaml`.

- **`sprint.default_threshold_sp`** — soft cap on total SP per plan; above this `/groom` proposes a split.
- **`sprint.redecompose_threshold`** — per-task SP value at or above which the task must be re-decomposed before the plan can leave `in-spec`.
- **`tasks`** — list of `{type, description, doc_uri}` entries (`feature`, `bug`, `refactoring`). `/groom` classifies the request against this list; the matching `doc_uri` lazy-loads detailed guidance for that task type.
- **`plan.statuses`** — the lifecycle slice `/groom` owns (`backlog`, `in-spec`, `awaiting-plan-review`) plus its outgoing transitions. The gates and `on_exit` mutations rendered into the skill body come from here.
