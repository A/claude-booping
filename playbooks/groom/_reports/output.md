Groom playbook takes user feature-development request, clarifies it if it's needed and builds
a development plan based on it.

**Context:**
- Date & Time: 1970-01-01 00:00
- Plan dir: `plans/197001010000_{kebab-title}/`


## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
| `booping:booping-researcher` | Wide read or web search where results must be aggregated outside this skill's context and returned as a summary; Map blast radius across many files (which modules and integrations a change touches); Extract patterns from a corpus too large to read directly (e.g. 'common shapes across 30 test files'); Verify package versions, image tags, API endpoints, CLI flags against current docs when many sources need to be checked; Cross-system architecture investigation across multiple repos or services; Compare framework/library options with deep tradeoff analysis | Small checks — single-file reads, one-off greps, existence checks; When the information cannot be meaningfully compressed without losing signal the caller needs to decide; When the skill already needs to read the same few files for other reasons; When the question fits in a few lines of `ls`/`grep` output |



## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Restate the request, classify the task type, set the scope boundaries and challenge the scope in a brief written to `request.md` and posted in chat; create the plan directory with its `index.md`, or adopt a parked plan into it. | The user answers the scope-challenge questions — clear intent is the confirmation, no separate confirm is asked for; answers that change the task type, the restated problem or a boundary send the step back for another pass |
| `research-codebase` | `intake` | Map the blast radius in the attached repo — touched surfaces, prior art, the conventions that bind the design, and the calls left for it; the bulk reads are delegated, the map is posted in chat. | — |
| `research-web` | `research-codebase` | Research the external ground the design rests on — current best practice, competing approaches and known pitfalls where the work is uncertain, and the external references it names, each checked against current docs. | — |
| `draft-plan` | `research-codebase`, `research-web` | Settle architecture, surface changes and trade-offs with the user, then pick the plan template matching the dominant surface and write the plan against its Plan Body — milestones, tasks with DoD and Verify, story points per task / milestone / sprint, `sp` and `summary` frontmatter; verify against the template's Quality Checklist before returning. | — |
| `cross-review` | `draft-plan` | Second-model review of the written plan — the agent reads the plan file `plans/{slug}/index.md` and returns severity findings only, writing nothing. Dispose of the findings yourself before advancing: `CRITICAL` folded into the plan or recorded as a deferral in `## Risk register`, `RISK` folded in unless it reopens a call the user settled, `NOTE` at your discretion; a finding that reopens a settled design call is folded in nowhere and sends the run back to `drafting`. | — |
| `present` | `cross-review` | Assemble the approval summary — approach, milestones, SP totals, plan path and every check outcome; recommend a split when the total passes the threshold, offer a plan branch on a repo-local vault, and carry the approval. | The run's only review gate — the summary and the full plan are approved together, and the plan reaches the `develop` playbook through this gate and no other. Ask for the approval in prose, in the message itself — never via `AskUserQuestion`. Explicit user approval: "looks good" counts, silence never does; on that word the run moves to `ready-for-dev`. A change request loops the run back to the status that owns what it touches: any change to the plan — architecture, scope, milestones, tasks or estimates — sends the run back to `drafting`, and present never absorbs a change itself. A recommended split is acknowledged, not required: the user may approve the plan whole and park no siblings |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state groom --workdir <run workdir>
```

### State: run

- Referenced by: outer graph
- Artifact: `index.md` (relative to the run workdir)
- Initial status: `framing`
- Advance: `booping playbook-transition groom <to> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `framing` | `researching` | intake posted the framing brief in chat, created `index.md` with its identity frontmatter, and the user's answers settled the scope questions — clear intent is enough | answers that change the task type, the restated problem or a boundary re-run intake first |
| `framing` | `cancelled` | the user cancels the run | — |
| `researching` | `drafting` | the blast-radius map and the web-research findings are both posted in chat | — |
| `researching` | `cancelled` | the user cancels the run | — |
| `drafting` | `cross-reviewing` | architecture, surface changes and trade-offs are settled with the user in conversation, and draft-plan wrote `index.md`'s body against the template's Plan Body and passed its Quality Checklist | every call that is the user's is answered |
| `drafting` | `researching` | the design needs blast radius or external practice the research pass missed | — |
| `drafting` | `cancelled` | the user cancels the run | — |
| `cross-reviewing` | `presenting` | the cross-review pass disposed of every finding, or no `core.groom_playbook.cross_review_agent` is configured and the pass was skipped | every CRITICAL finding folded in or recorded as a deferral — vacuously satisfied with no `core.groom_playbook.cross_review_agent` configured |
| `cross-reviewing` | `cancelled` | the user cancels the run | — |
| `presenting` | `awaiting-approval` | present posted the approval screen in chat — summary, split recommendation if any, handoff to the `develop` playbook | — |
| `presenting` | `cancelled` | the user cancels the run | — |
| `awaiting-approval` | `drafting` | the user's change request touches the plan itself — architecture, scope, milestones, tasks or estimates | — |
| `awaiting-approval` | `ready-for-dev` | the user explicitly approves the plan — "looks good" counts, silence never does | explicit user approval captured |
| `awaiting-approval` | `cancelled` | the user cancels the run | — |
| `ready-for-dev` | *(terminal)* | — | — |
| `cancelled` | *(terminal)* | — | — |

## Step: Intake
# Frame the request

You need to read user request and confirm you have all information to work it out into a plan and file a request.

## Latest Plans

Check for context, in case a request is related to already existing plan.


| state | name | summary | path |
| --- | --- | --- | --- |
| in-progress | API throttling | Per-client rate limits on the public API. | [plan](plans/19700106-api-throttling/index.md) |
| awaiting-learning | Session cleanup sweep | Sweep orphaned session rows on expiry. | [plan](plans/19700103-session-cleanup/index.md) |
| awaiting-retro | Login timeout fix | Session expiry fired one minute early. | [plan](plans/19700102-login-timeout/index.md) |
| awaiting-retro | Widget search | Full-text search across the widget catalog. | [plan](plans/19700101-widget-search/index.md) |
| ready-for-dev | Cache warm-up on deploy | Warm the read cache as part of the deploy step. | [plan](plans/19700104-cache-warmup/index.md) |



## Task Types

Exactly one per plan. Pick the row the request meets, load its guidance before framing, and rule
the siblings out by name.

| type | fits when | guidance |
| --- | --- | --- |
| `feature` | New user-facing capability. Needs business goal, design, milestones, DoD. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_feature.md) |
| `bug` | Defect — observed behavior diverges from expected. Needs triage, reproduction, root-cause hypothesis, minimal fix, and a regression test. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_bug.md) |
| `refactoring` | Internal structure change with no user-visible behavior change. Needs current-vs-target design, migration steps, and a no-behavior-change DoD. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_refactoring.md) |


## The plan's identity frontmatter

Create `index.md` carrying the shape below. `created` is the run's clock to the minute, not just
the date — copy the value verbatim. `status` is the run machine's and is written by
`booping playbook-transition`, never by hand.

---
title: {Descriptive Title}
type: feature | bug | refactoring
status: framing                  # the run machine's status — written by `booping playbook-transition`, never by hand
sp: {total}                      # sprint total, summed from milestone totals
split_from: null                 # sibling stubs only: path to the primary plan this was split from
created: 1970-01-01 00:00        # when the plan directory was created — the run's clock, to the minute
planned: null                    # date keys — owned by the run machine's edge hooks, same shape as `created`
started: null
completed: null
retro: null
goal: null
summary: ""                      # one-line plan intent for search + plan listings (≤ ~120 chars)
commit: null
---


## The brief — written to `request.md`, posted in chat

The framing brief is this step's outcome: it is written to `request.md`, which every later step
reads, and posted in chat, where the user answers it. Both carry the same block, with exactly
these parts, in this order:

- **Request** — the request as a blockquote, character-for-character. Nothing added, nothing
  tidied, nothing summarised.
- **Task type** — one backticked type from the catalogue, with the rationale that rules each
  sibling type out by name and on a stated test.
- **Problem** — what the system does today and what must change, in the request's own
  domain terms.
- **Clarifications and Decisions**: list of one-line clarifications and decisions made with user when refining on this plan

## Step: Research Codebase
Map the blast radius — files, modules, integrations, external surfaces; check prior art.

## Step: Research Web
- Research when uncertain: for complex, novel, or non-obvious work, search the web for current best practices, competing approaches, and known pitfalls before locking design decisions.
- Verify external references: every package version, image tag, API endpoint, CLI flag, or config option named in the plan is checked against current docs. Never assume.

## Step: Draft Plan
# Write the plan

Your task is to build a plan for the user request, from the framing and the research findings this
conversation already carries — the blast-radius map and the external ground the work rests on.

- **Draft design with the user**: architecture, pattern choices, data / API / config surface
  changes, open trade-offs. Iterate until aligned before writing.
- **Write the plan**: pick a plan template from [Available plan templates](#available-plan-templates)
  whose name + description matches the work, then produce the plan against its `# Plan Body` — see
  [Plan Structure](#plan-structure).
- **Write `summary`**: set the `summary:` frontmatter to a single line of plain plan intent — ≤ ~120
  chars / ~20 words, no prose, no trailing period needed. It feeds search and the `sprints.md`
  snapshot.

## Hard rules

- The orchestrator never edits files outside `{project}/plans/`.
- Each milestone executable in a fresh session with only the plan as context.
- Sprint total past **35 SP** — offer the user a split at a dependency seam (the first slice
  shippable on its own, each later one useless without it), keep only the first slice that fits the
  threshold in this plan, and park the rest as sibling stubs to be groomed in their own runs. They
  may decline and keep one plan.
- User approval is **explicit** — "looks good" is enough; silence is not.

## Plan Structure

The plan is the run's `index.md`: frontmatter, then the title, then the body.

### Frontmatter

```yaml
---
title: {Descriptive Title}
type: feature | bug | refactoring
status: framing                  # the run machine's status — written by `booping playbook-transition`, never by hand
sp: {total}                      # sprint total, summed from milestone totals
split_from: null                 # sibling stubs only: path to the primary plan this was split from
created: 1970-01-01 00:00        # when the plan directory was created — the run's clock, to the minute
planned: null                    # date keys — owned by the run machine's edge hooks, same shape as `created`
started: null
completed: null
retro: null
goal: null
summary: ""                      # one-line plan intent for search + plan listings (≤ ~120 chars)
commit: null
---

```

`sp` and `summary` are yours to write. `title` and `type` are intake's — correct them only where
the design changed them. `status` and every date and outcome key belong to the run machine and its hooks: whatever intake
left `null` stays `null`.

### Title

One H1 matching `title:`, and the only H1 in the file.

### Body + Quality Checklist

Each plan template is one file with two top-level sections:

- `# Plan Body` — the structure the plan is written against, section for section, in its order.
  None dropped, none extra.
- `# Quality Checklist` — walked item by item against the plan as written, before the plan is
  returned. An unsatisfied item is fixed, not reported as satisfied.

Read the chosen file before drafting: neither section can be guessed from its catalogue line.

When no entry fits, author one at `{project}/plan_templates/{name}.md` first, then draft against
it — frontmatter (`name`, `description`) plus both top-level sections, generic for its surface
class: placeholders throughout, no path, milestone or story-point value from this run baked in.
Never draft into a bad-fit template, never improvise a shape and name a template after it.


## Available plan templates

Pick the entry whose name and description match the **dominant surface** of the work — the surface
most of the milestones land on. A near miss loses on that surface, not on taste.

| Name | Source | Description | Read from |
| --- | --- | --- | --- |
| `backend` | core | Backend feature work — APIs, data models, services, migrations, background jobs, protocols. Stack-agnostic. | `${CLAUDE_PLUGIN_ROOT}/docs/plan_templates/backend.md` |
| `claude-skill` | core | Authoring or refactoring a Claude Code skill — skill bodies, partials, config schema, rendered outputs, skill-level agents. | `${CLAUDE_PLUGIN_ROOT}/docs/plan_templates/claude_skill.md` |
| `cli` | core | CLI tool work — argument parsing, subcommands, I/O, error handling, exit codes. Standalone scripts or larger CLI suites. | `${CLAUDE_PLUGIN_ROOT}/docs/plan_templates/cli.md` |
| `documentation` | core | Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.). | `${CLAUDE_PLUGIN_ROOT}/docs/plan_templates/documentation.md` |
| `frontend` | core | Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla). | `${CLAUDE_PLUGIN_ROOT}/docs/plan_templates/frontend.md` |



## Sprint planning

A plan is estimated as a single sprint: every task carries story points, task points sum into the
milestone total, milestone totals sum into the plan's `sp`.

Story points measure the **complexity and review burden** of getting a task to a merged, accepted
state: design judgment, blast radius, ambiguity, integration surface, and how much careful reading
the diff demands. AI does implementation cheaply; this is what remains.

### Scale

| SP | Meaning |
|----|---------|
| 1 | Simple text/config change, no risk |
| 2 | Simple task, predictable, no risk |
| 3 | Medium task, minor risks but predictable overall |
| 4 | Complex task, medium risk, may need small research but clear enough |
| 5 | Research task — developer needs to clarify and decompose further before proceeding |


Development bundles **up to 2 consecutive milestone(s)** into a single agent briefing — size
milestones against that combined review burden.

### Thresholds

- **5 SP re-decompose threshold** — a task at or over it is split before the plan is
  returned. Cut at a seam in its own work, never at its midpoint; each half stands alone with its
  own DoD and Verify, and the milestone and sprint totals are re-summed from the new leaves.
- **35 SP split threshold** — not a velocity: the point past which a sprint is too large to
  hold together as one coherent iteration.

Estimate the work as it honestly stands: never shave a task to land under a threshold, never
inflate one, and never re-estimate a task down to dodge a split.

Project-specific sizing overrides live in `{project}/_booping/skill_groom.md` and take precedence.

## Step: Cross Review

Second-model review of the written plan — the agent reads the plan file `plans/{slug}/index.md` and returns severity findings only, writing nothing. Dispose of the findings yourself before advancing: `CRITICAL` folded into the plan or recorded as a deferral in `## Risk register`, `RISK` folded in unless it reopens a call the user settled, `NOTE` at your discretion; a finding that reopens a settled design call is folded in nowhere and sends the run back to `drafting`.

Tell the `codex` agent to get its instructions by calling this command: `booping render-playbook groom --step cross-review`.

## Step: Present
Present user the resulting plan as:

```
Request: {path}
Plan: {path}
Status: {status}
SPs: {SP total}

| # | Summary | SP |
| - | ------- | -- |
{one row per milestone — its id, what it delivers, its SP}

## Next Steps

Approve plan or jump into develop via:

/playbook develop {plan path}
```

Ask for approval in **prose**, in the message itself — never through `AskUserQuestion`, and
never as a `## Questions:` entry. One plain sentence after the screen: the plan is ready for
development, or say what to change. Read the reply as chat text; "looks good" approves,
silence does not.

Open questions that are not the approval ask still go in a `## Questions:` block below the
table.
