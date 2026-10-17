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

## Rules

The following 4 rule(s) apply to this playbook. Never silently violate one; conflict → stop and flag. Read a rule's record when its brief is not enough.

- Settle every open question with the user during grooming; in develop, stop only for force majeure, not for what grooming should have asked. [booping:rule/0004](${CLAUDE_PLUGIN_ROOT}/specs/rule/0004-questions-settled-in-grooming.md)
- Before saving a skill, agent, partial, template or briefing, check every block for scoping, duplication, configurability and hierarchy; cut motivation, restated context and preambles. [booping:rule/0006](${CLAUDE_PLUGIN_ROOT}/specs/rule/0006-information-architecture-pass.md)
- Name the values that drive the plan's main choices and flag every departure from a value or rule with its reason, so the user can refine the values. [booping:rule/0030](${CLAUDE_PLUGIN_ROOT}/specs/rule/0030-planning-shows-values-in-play.md)
- When the user corrects you — rejects a proposal, rewrites an output, says it is wrong, answers a gate other than you suggested — run `booping create core.corrections.template {vault}/corrections --set name=$(date +%Y%m%d-%H%M%S)-{step} --set step={playbook}/{step} --set did=… --set said='{the user's words verbatim}' --set artifact={run artefact, vault-relative}`, with `--set why=…` when the user states it; a plain confirmation is not a correction. [booping:rule/0031](${CLAUDE_PLUGIN_ROOT}/specs/rule/0031-corrections-are-logged.md)

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Restate the request, classify the task type, set the scope boundaries and challenge the scope in a brief written to `request.md` and posted in chat; create the plan directory with its `index.md`, or adopt a parked plan into it. | The user answers the scope-challenge questions — clear intent is the confirmation, no separate confirm is asked for; answers that change the task type, the restated problem or a boundary send the step back for another pass |
| `draft-plan` | `intake` | Research the code the request touches and post the facts in chat, then draft the whole plan against the template matching the dominant surface into `draft.md`, cut it with `booping plan split`, check it with `booping plan check` and fix the draft until clean or three rounds are spent; set `summary` frontmatter. | — |
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
| `framing` | `awaiting-clarification` | the run raised questions it cannot answer itself and wrote them to `clarifications.md` | every question in `clarifications.md` is open and attributed — an id, a topic, the date and the step that raised it |
| `framing` | `cancelled` | the user cancels the run | — |
| `researching` | `drafting` | draft-plan's research stage posted its facts, with file paths, in chat | — |
| `researching` | `cancelled` | the user cancels the run | — |
| `drafting` | `cross-reviewing` | draft-plan wrote `draft.md`, `booping plan split` exited 0 and the mdcheck milestone check passed or its three fix rounds are spent | every call that is the user's is answered; the mdcheck milestone check reports no finding on the `sp` key |
| `drafting` | `researching` | the design needs blast radius or external practice the research pass missed | — |
| `drafting` | `awaiting-clarification` | the run raised questions it cannot answer itself and wrote them to `clarifications.md` | every question in `clarifications.md` is open and attributed — an id, a topic, the date and the step that raised it |
| `drafting` | `cancelled` | the user cancels the run | — |
| `awaiting-clarification` | `framing` | the answers came back and `return_to` names `framing` | every question in `clarifications.md` carries an answer; `return_to` is `framing` — any other value picks the other return edge |
| `awaiting-clarification` | `drafting` | the answers came back and `return_to` names `drafting` | every question in `clarifications.md` carries an answer; `return_to` is `drafting` — any other value picks the other return edge |
| `awaiting-clarification` | `cancelled` | the user cancels the run | — |
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
| done | Session cleanup sweep | Sweep orphaned session rows on expiry. | [plan](plans/19700103-session-cleanup/index.md) |
| done | Login timeout fix | Session expiry fired one minute early. | [plan](plans/19700102-login-timeout/index.md) |
| done | Widget search | Full-text search across the widget catalog. | [plan](plans/19700101-widget-search/index.md) |
| ready-for-dev | Cache warm-up on deploy | Warm the read cache as part of the deploy step. | [plan](plans/19700104-cache-warmup/index.md) |



## Task Type

Exactly one per plan. Pick the row the request meets, load its guidance before framing and pick one.

| type | fits when | guidance |
| --- | --- | --- |
| `feature` | New user-facing capability. Needs business goal, design, milestones, DoD. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_feature.md) |
| `bug` | Defect — observed behavior diverges from expected. Needs triage, reproduction, root-cause hypothesis, minimal fix, and a regression test. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_bug.md) |
| `refactoring` | Internal structure change with no user-visible behavior change. Needs current-vs-target design, migration steps, and a no-behavior-change DoD. | [guidance](${CLAUDE_PLUGIN_ROOT}/docs/task_refactoring.md) |


## The plan directory

Create it in one call, with `{plan-dir}` the preamble's `Plan dir:` line resolved against the
vault and `{title}` the plan's descriptive title:

```
booping create core.groom_playbook.template {plan-dir} --set title="{title}" --set type={type}
```

The printed diff is the confirmation — do not read the created files back. A target reported as
already existing was not written; decide what that means for this run.

- A request naming open items (`OI-NNNN`) links each to the new plan once the directory exists:
  `booping items plan {ids} --plan {plan-dir}/index.md`.

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

## Step: Draft Plan
# Draft the plan

Produce an implementation plan an autonomous developer agent will execute milestone by milestone in the attached repository, from the framing this conversation carries. Change no repository file. `{plan-dir}` is the preamble's `Plan dir:` line, `{slug}` its last segment. Work in four stages.

## 1. Research

Read the code the request touches and anything it depends on; delegate bulk reads to `booping:booping-researcher`. Post the facts, each with its file path, in chat, then advance the run to `drafting`.

## 2. Draft

Pick the template ([Available plan templates](#available-plan-templates)) and write the whole plan to `{plan-dir}/draft.md`: every section of its `# Plan Body`, in its order, the milestones under `## Milestones` in this format:

```
### M{nn} — {title}

sp: {n}
depends_on: [M{nn}, …]

#### Tasks

#### Definition of Done

#### References

#### Verify
```

- `{nn}` is the milestone's position in execution order, two digits; `sp` is 1–4, `depends_on` is `[]` when nothing precedes it.
- Each milestone has one Verify command scoped to that milestone, written as a single inline code span; the whole-repo check goes only in Final Verification.
- Decide what the code and the request settle, and record each assumption in the plan. A call only the user can make goes to the user: in a supervised run ask it in chat; in an autonomous run write it to `clarifications.md` (format: `${CLAUDE_PLUGIN_ROOT}/docs/clarifications.md`) and park the run on `awaiting-clarification`.
- Sprint total past **35 SP** — offer the user a split at a dependency seam (the first slice shippable on its own, each later one useless without it), keep only the first slice that fits the threshold in this plan, and park the rest as sibling stubs to be groomed in their own runs. They may decline and keep one plan.

## 3. Split

```
booping plan split {plan-dir}/draft.md --replace
```

Exit 3 (no milestone heading) or 4 (written with `flag:` lines) — the draft is off-format. Spawn a `general-purpose` sub-agent with model and effort `opus:medium`, handing it `draft.md`'s path, the split's stderr and the format above: it rewrites the draft into that format at `/tmp/booping-split-{slug}/draft.md` and writes nothing in the vault. Copy that file over `{plan-dir}/draft.md` and split again. Exit 1 or 2 — stop and report the `error:` line.

## 4. Check

```
mdcheck ${CLAUDE_PLUGIN_ROOT}/playbooks/groom/_schemas/milestone.yaml {plan-dir}/milestones/*/M*.md
```

Exit 1 — fix the milestones its findings name in `draft.md`, then back to stage 3. At most three rounds; findings left after the third are carried to `present`.

Then set the summary — one line of plain plan intent, ≤ ~120 chars / ~20 words:

```
booping frontmatter-update {plan-dir}/index.md summary="{one line}"
```

`sp` is not yours — split stamps it.

## Hard rules

- Never edit files outside `{project}/plans/`.
- User approval is **explicit** — "looks good" is enough; silence is not.

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

Each template is one file with two top-level sections:

- `# Plan Body` — the structure the plan is written against, section for section, in its order.
  None dropped, none extra.
- `# Quality Checklist` — constraints the plan meets; read with the body, not walked as a separate pass.

Read the chosen file before drafting: neither section can be guessed from its catalogue line.

When no entry fits, author one at `{project}/plan_templates/{name}.md` first, then draft against
it — frontmatter (`name`, `description`) plus both top-level sections, generic for its surface
class: placeholders throughout, no path, milestone or story-point value from this run baked in.
Never draft into a bad-fit template, never improvise a shape and name a template after it.

The draft is one file, cut into `index.md` and the milestone files by `booping plan split`.

`summary` is yours:

```
booping frontmatter-update {plan-dir}/index.md summary="{one line}"
```

`sp` is not — never hand-write it.


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


Development packs a contiguous run of milestones, in `id` order, into a single agent briefing while
their summed SP stays at or under **15 SP** — size milestones against that combined
review burden.

### Thresholds

- **5 SP re-decompose threshold** — a task or a milestone at or over it is split before
  the plan leaves drafting. Cut at a seam in its own work, never at its midpoint; each half stands
  alone with its own DoD and Verify, and the milestone and sprint totals are re-summed from the new
  leaves.
- **35 SP split threshold** — not a velocity: the point past which a sprint is too large to
  hold together as one coherent iteration.

Estimate the work as it honestly stands: never shave a task to land under a threshold, never
inflate one, and never re-estimate a task down to dodge a split.

Project-specific sizing overrides live in `{project}/_booping/skill_groom.md` and take precedence.

## Rules

The following 4 rule(s) apply to this step. Never silently violate one. Read a rule's record when its brief is not enough.

- When the plan deletes or renames partials, agents, CLAUDE.md lines or doc links, make the cleanup of every stale reference a milestone task with its own DoD in this sprint. [booping:rule/0007](${CLAUDE_PLUGIN_ROOT}/specs/rule/0007-stale-references-cleaned-in-sprint.md)
- For user-facing content (release notes, docs, changelogs), put the audience filter into the task's DoD: only what that audience touches, no internal churn. [booping:rule/0008](${CLAUDE_PLUGIN_ROOT}/specs/rule/0008-audience-scoped-content.md)
- When folding DoD and Verify into tasks, state the exact return shape the worker replies with — only what the orchestrator needs (e.g. the list of changed files). [booping:rule/0009](${CLAUDE_PLUGIN_ROOT}/specs/rule/0009-bounded-agent-return-contract.md)
- When the plan defines a user-facing output or log format, lock its exact content with the user now — line fields, truncation rules, trailers — not just the format in prose. [booping:rule/0010](${CLAUDE_PLUGIN_ROOT}/specs/rule/0010-output-content-locked-in-grooming.md)

## Step: Cross Review

Second-model review of the written plan — the agent reads the plan file `plans/{slug}/index.md` and returns severity findings only, writing nothing. Dispose of the findings yourself before advancing: `CRITICAL` folded into the plan or recorded as a deferral in `## Risk register`, `RISK` folded in unless it reopens a call the user settled, `NOTE` at your discretion; a finding that reopens a settled design call is folded in nowhere and sends the run back to `drafting`.

Tell the `codex` agent to get its instructions by calling this command: `booping render-playbook groom --step cross-review`.

## Step: Present
Read the plan's milestone rows — never a hand-kept list — with `{plan-dir}` the preamble's `Plan dir:` line:

```
booping query --glob {plan-dir}/milestones/*/M*.md --columns id,title,sp,status
```

Then check the milestone contract:

```
mdcheck ${CLAUDE_PLUGIN_ROOT}/playbooks/groom/_schemas/milestone.yaml {plan-dir}/milestones/*/M*.md
```

Present user the resulting plan as:

```
Request: {path}
Plan: {path}
Status: {status}
SPs: {sum of the rows' sp}

{the table the query printed}

{the check's output, or "milestone contract: clean" when it printed nothing}

Decisions:
1. {decision} — (user) | (proposal)

## Next Steps

Approve plan or jump into develop via:

/playbook develop {plan path}
```

`Decisions:` numbers every call the plan takes as settled — the brief's clarifications and
decisions, each assumption the plan records — one plain line each, `(user)` for the user's words,
`(proposal)` for yours.

Ask for approval in **prose**, in the message itself — never through `AskUserQuestion`, and
never as a `## Questions:` entry. One plain sentence after the screen: the plan is ready for
development, or say what to change. Read the reply as chat text; "looks good" approves,
silence does not.

Open questions that are not the approval ask still go in a `## Questions:` block below the
table.
