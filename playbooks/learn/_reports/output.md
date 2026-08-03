Turn retrospective findings into durable behavior changes routed to exactly one target each.

## Guidance

- Learn handles plans in `awaiting-learning` status.
- The retrospective lives at `plans/{primary-slug}/retro.md`; its `plans:` frontmatter lists the working set the run covers, and the plan whose directory holds it is the **primary**.
- The run workdir is the primary plan's directory `plans/{primary-slug}/` — `index.md` there is the run artifact.
- Learn writes only to this project's vault (`_lessons/`, `_booping/`) and the attached repo's `CLAUDE.md` — **never** the global `~/.claude/CLAUDE.md` or any user-level scope.

## Single-location rule

Every accepted learning lands in **exactly one** target. If a candidate would otherwise span two targets, decompose it into two distinct rows in the review table — one row per target. The four targets, when-to-use tests, and example filenames live in the routing matrix below; do not restate it elsewhere.

## Routing Matrix

This matrix is the routing contract for /learn candidates. Every accepted learning lands in exactly one target — no duplicates across targets, no multi-target rows.

| Target | When to use | Lands at | Examples |
|--------|-------------|----------|----------|
| **Lesson** | Behavior change reaching one or more playbooks, playbook steps, or agents — design heuristic, test discipline, IA rule. Concrete, short, with one example. | `_lessons/{N}_<kebab>.md`, with a `targets:` list naming what it applies to | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy" |
| **Skill extra instructions** | Tweak or extend a single skill's method (groom / develop / retro / learn / chat / install / help). | `_booping/skill_<skill>.md` | `skill_groom.md`, `skill_develop.md`, `skill_retro.md`, `skill_learn.md`, `skill_chat.md`, `skill_install.md`, `skill_help.md` |
| **Agent extra instructions** | Hook a single agent's behavior. Compact list. | `_booping/agent_<full-agent-name>.md` | `agent_booping-researcher.md`, `agent_booping-developer.md` |
| **Repository CLAUDE.md** | Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. | `<repo>/CLAUDE.md` (the attached repo's file — **never** the global `~/.claude/CLAUDE.md` or any user-level scope) | (single canonical target — no filename variants) |

If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets. A lesson is the one target that carries its own routing: it lands in this project's `_lessons/` and its `targets:` list wires it to the playbooks, steps and agents it applies to — several entries in one list are one row, not a multi-target row.

The skill infers the exact filename per candidate; the example lists above are validation aids, not full enumerations.


## Plans awaiting learning

_No plans at `awaiting-learning`._

## High-level workflow

1. Intake — resolve the retrospective and its working set; validate `awaiting-learning` status.
2. Extract candidates — inline, decomposed into atomic rules, routed via the matrix.
3. Update-vs-create sweep — filtered read of existing lessons and extensions.
4. Present unified review table — user accepts / rejects / adds rows.
5. Write accepted items — one pass per target type, no per-edit prompts.
6. Transition and commit.





## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Resolve the run's retrospective — from `$ARGUMENTS` as a retro path, or by picking a plan from the awaiting-learning list and following its `retro:` frontmatter — settle the working set from the retro's `plans:` list with the primary plan's directory as the workdir, validate every plan sits at learn's entry status, then read the retrospective in full and each plan for context. | — |
| `extract-candidates` | `intake` | Decompose every retrospective insight into atomic candidates — one imperative rule per candidate, single concern, no bare internal IDs, one sentence per review-table cell — and route each to exactly one target from the preamble's routing matrix, holding the set in context for the sweep. | — |
| `dedup-sweep` | `extract-candidates` | Sweep every candidate against existing coverage — the vault's lessons, the `_booping/` extensions, and the repo's `CLAUDE.md` — and record a per-candidate verdict: new, update-existing at the target already holding the rule, or a conflict flagged visibly for the review table. | — |
| `review-table` | `dedup-sweep` | Present the unified review table in the format the review-table doc owns — every candidate with its target and sweep verdict, conflicts flagged — and collect the user's accept / reject / add response in a single `AskUserQuestion` call, never per row; the recorded response is the run's consent to write. | — |
| `write` | `review-table` | Write every accepted row in one pass per target type — new lesson files at the next free number, in-place updates to the file the sweep matched, `_booping/` extension edits, one-line bullets into the repo's `CLAUDE.md` — with table acceptance as the sole consent and never a write outside the vault and the attached repo. | — |
| `transition` | `write` | Fire the exit transition from the workdir — `booping playbook-transition learn done` — whose hook moves every sibling plan to `done`, re-renders sprints.md and commits the vault including the written lessons and extensions; commit any repo `CLAUDE.md` addition separately in the repo working tree, then close on a report of items written per target. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state learn --workdir <run workdir>
```

### State: run

- Referenced by: outer graph
- Artifact: `index.md` (relative to the run workdir)
- Initial status: `awaiting-learning`
- Advance: `booping playbook-transition learn <to> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-learning` | `done` | every accepted row from the confirmed review table is written to its single target | user confirmed the review table — the accept / reject / add response is recorded; every accepted lesson written to its target file |
| `done` | *(terminal)* | — | — |

## Step: Intake
The current set of plans in `awaiting-learning` is listed in the [Plans awaiting learning](#plans-awaiting-learning) table of the preamble.

Resolve `$ARGUMENTS` to a retrospective file path.

**No `$ARGUMENTS`**: branch on the plans-list size.

- **Zero plans**: STOP with `No plans in awaiting-learning. Run the retro playbook first to write a retrospective.`
- **Exactly one plan**: auto-select it (do not call `AskUserQuestion` — it requires ≥2 options).
- **Multiple plans**: present the list via `AskUserQuestion` (single-select; one option per plan). Plans sharing one `retro:` value are one working set — offer the set as a single option, not one option per sibling.

Read the selected plan's `retro:` frontmatter to resolve the retrospective file.

**`$ARGUMENTS` provided**: treat it as the retrospective file path. Read it and follow its `plans:` frontmatter to the associated plans.

## Working set and workdir

The retrospective's `plans:` frontmatter is the **working set** — every plan this run absorbs lessons for. The plan whose directory holds the retrospective is the **primary**, and its directory `plans/{primary-slug}/` is the run workdir. A retrospective without a `plans:` list covers only the plan it was resolved from.

Validate every working-set plan's `status:` is `awaiting-learning`. On mismatch, STOP with this verbatim error:

> `learn playbook requires a plan in status 'awaiting-learning'; got '{current-status}' for {plan-path}. Use the list above to pick a candidate.`

Read the retrospective in full — it is the sole source the run extracts from. Read each working-set plan for context only: scope, decisions on record, what the retro's findings refer to.

## The report — posted in chat

```markdown
## Learn intake

Retrospective: {path}
Working set: {a table with columns: plan path, status, goal verdict from the retro's `goal_verdicts:` when present}
```

## Step: Extract Candidates
Extract candidates for self-learning from the retrospective read at `intake`. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the review-table `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick a target from the routing matrix in the preamble. When the target is a lesson, pick its `targets:` entries from the target space below — the routing matrix decides *which kind of file* the candidate lands in, the target space decides *what the lesson is wired to*.

Nothing is presented to the user yet — the dedup sweep runs first, and the review table is the single surface where candidates appear.

## Lesson Target Space

Every lesson targets exactly one entry from the space below, written into its `targets:` frontmatter list. Entry forms — exact names only, no globs, no wildcards, no negation:

- `{playbook}` — the whole playbook, e.g. `develop`
- `{playbook}/{step}` — one step of it, e.g. `develop/develop-loop`
- `agent:{id}` — one agent, e.g. `agent:booping-developer`


### develop

| Step | Summary |
| --- | --- |
| `develop/develop-loop` | Run the sprint group by group — one briefing per group to the worker agent, one worker at a time on the sprint branch; on each report verify against the milestone's DoD and its plan-authored Verify, flip the checkboxes, task rows and milestone status, commit per milestone, refresh and commit the vault snapshot, and report what shipped before the next group. |
| `develop/intake` | Adopt the plan the preamble resolved — validate its `status:` against an entry transition, capture the user's approval when it entered at `awaiting-plan-review`, then check plan validity against the repo's current commit: cheap summary first, the plan-named diff only on the user's word; trivial drift patched in place, non-trivial drift halted back to grooming. |
| `develop/provision` | Set the sprint up — pick the branch from the plan's task type per the branch conventions, propose a kebab-case name and create it off the repo's current branch only after the user confirms; then settle the milestone groups the briefings will cover, within the configured ceiling, and fire the `ready-for-dev` → `in-progress` transition. |
| `develop/verify` | Run the project's guardrails over the finished sprint once — tests, lint, typecheck, formatter, whatever else must hold for a PR to open without CI failing — plus the plan's own bookkeeping, every DoD checkbox `[x]` and every milestone `done`, read off disk, and return what passed and what failed; no code-quality judgement, no fixes applied here. |
| `develop/wrap-up` | Close the run — update the documentation the sprint invalidated, make one closing commit, fire the `in-progress` → `awaiting-retro` transition, refresh and commit the vault snapshot, then report the sprint and hand off to `/retro`. Guardrail results and completeness arrive as verify's evidence and are never re-established here. |

**Agents:**

- `agent:booping-developer` — All coding tasks — always delegate; never edit application code from the orchestrator
- `agent:booping-researcher` — Phase 0 drift spot-check: given a large set of plan-named files, determine whether actual file shape matches the plan's assumptions

### groom

| Step | Summary |
| --- | --- |
| `groom/cross-review` | Second-model review of the written plan — requires the plan file `plans/{slug}/index.md`, which the reviewing agent reads; it returns severity findings only and writes nothing. Skip the step when the project configures no `cross_review` agent. |
| `groom/draft-plan` | Settle architecture, surface changes and trade-offs with the user, then pick the plan template matching the dominant surface and write the plan against its Plan Body — milestones, tasks with DoD and Verify, story points per task / milestone / sprint, `sp` and `summary` frontmatter; verify against the template's Quality Checklist before returning. |
| `groom/intake` | Restate the request, classify the task type, set the scope boundaries and challenge the scope in a brief written to `request.md` and posted in chat; create the plan directory with its `index.md`, or adopt a parked plan into it. |
| `groom/present` | Assemble the approval summary — approach, milestones, SP totals, plan path and every check outcome; recommend a split when the total passes the threshold, offer a plan branch on a repo-local vault, and carry the approval. |
| `groom/research-codebase` | Map the blast radius in the attached repo — touched surfaces, prior art, the conventions that bind the design, and the calls left for it; the bulk reads are delegated, the map is posted in chat. |
| `groom/research-web` | Research the external ground the design rests on — current best practice, competing approaches and known pitfalls where the work is uncertain, and the external references it names, each checked against current docs. |

**Agents:**

- `agent:booping-researcher` — Wide read or web search where results must be aggregated outside this skill's context and returned as a summary; Map blast radius across many files (which modules and integrations a change touches); Extract patterns from a corpus too large to read directly (e.g. 'common shapes across 30 test files'); Verify package versions, image tags, API endpoints, CLI flags against current docs when many sources need to be checked; Cross-system architecture investigation across multiple repos or services; Compare framework/library options with deep tradeoff analysis

### learn

| Step | Summary |
| --- | --- |
| `learn/dedup-sweep` | Sweep every candidate against existing coverage — the vault's lessons, the `_booping/` extensions, and the repo's `CLAUDE.md` — and record a per-candidate verdict: new, update-existing at the target already holding the rule, or a conflict flagged visibly for the review table. |
| `learn/extract-candidates` | Decompose every retrospective insight into atomic candidates — one imperative rule per candidate, single concern, no bare internal IDs, one sentence per review-table cell — and route each to exactly one target from the preamble's routing matrix, holding the set in context for the sweep. |
| `learn/intake` | Resolve the run's retrospective — from `$ARGUMENTS` as a retro path, or by picking a plan from the awaiting-learning list and following its `retro:` frontmatter — settle the working set from the retro's `plans:` list with the primary plan's directory as the workdir, validate every plan sits at learn's entry status, then read the retrospective in full and each plan for context. |
| `learn/review-table` | Present the unified review table in the format the review-table doc owns — every candidate with its target and sweep verdict, conflicts flagged — and collect the user's accept / reject / add response in a single `AskUserQuestion` call, never per row; the recorded response is the run's consent to write. |
| `learn/transition` | Fire the exit transition from the workdir — `booping playbook-transition learn done` — whose hook moves every sibling plan to `done`, re-renders sprints.md and commits the vault including the written lessons and extensions; commit any repo `CLAUDE.md` addition separately in the repo working tree, then close on a report of items written per target. |
| `learn/write` | Write every accepted row in one pass per target type — new lesson files at the next free number, in-place updates to the file the sweep matched, `_booping/` extension edits, one-line bullets into the repo's `CLAUDE.md` — with table acceptance as the sole consent and never a write outside the vault and the attached repo. |

### playbook-authoring

| Step | Summary |
| --- | --- |
| `playbook-authoring/decompose` | Break the procedure into a light decomposition index — graph, step table, decisions, open questions — the user models against before any detail exists. |
| `playbook-authoring/fixtures` | Materialize the fixtures the confirmed test rows name, as real files the step's suite runs against. |
| `playbook-authoring/interview` | Infer the new playbook's slug, goal, success shape and artifact home from the user's description, asking only about real gaps. |
| `playbook-authoring/llm-tests` | Pin every check the step's suite will run as tiered table rows — success cases first, traps by offer. |
| `playbook-authoring/manifest` | Write the playbook's manifest early — identity, trigger, and the confirmed graph verbatim; body as a lean guide the renderer completes. |
| `playbook-authoring/record-decision` | Append every user decision the runner relays to _specs/DECISIONS.md, timestamped; bootstrap the file on first call. |
| `playbook-authoring/regress-optimizer` | Read the baseline judge failures and tune the prompt toward the confirmed rubrics — prompt edits only; the harness runs baseline and verify. |
| `playbook-authoring/smoke-optimizer` | Diagnose a red smoke report against the confirmed example and edit the guilty side — prompt or check; the harness runs the tier between invocations. |
| `playbook-authoring/states` | Design the playbook's persisted state machines from decompose's tier verdict — or skip on ephemeral — as a States chart the manifest translates verbatim. |
| `playbook-authoring/step-prompt` | Write one step's prompt body and Jinja wrapper from its confirmed spec — seed quality, refined later by the optimizers. |
| `playbook-authoring/step-spec` | Write one step's contract and a concrete example of its artifact — the example IS the shape the suite will pin. |
| `playbook-authoring/step-suite` | Implement the suite from the step's confirmed test plan — smoke rows as script asserts, regress rows as named rubrics. |

### retro

| Step | Summary |
| --- | --- |
| `retro/gather-feedback` | Take the user's raw open-ended take before any mined finding is mentioned: four questions asked verbatim, one at a time, each with a free-text option; then walk every mined item in batches for accept / dismiss / the user's own wording, and close by asking per plan whether the plan's goal was reached, the goal presented verbatim as written. |
| `retro/intake` | Settle the working set the run covers — validate that the plan the preamble resolved sits at retro's entry status, offer every other plan at that status as include / postpone / skip-and-mark-done, apply the skip moves via `booping transition done`, then read each adopted plan in full for context only: scope, story points, dates and decisions on record, never as a source of runner-derived findings. |
| `retro/prepare` | Read each adopted plan in full for context only, then build the issue list without showing it — session-log mining and a plan-stage lesson check delegated in parallel, the lesson set passed verbatim with each brief — and cross-check both returns against the lesson set and the project-local retro extension; the list is withheld until gather-feedback has the user's raw take. |
| `retro/research-issues` | Do focused root-cause work on each accepted issue: read only the files the trigger or the user's wording implicates, compare documented project conventions against what the code actually does where the issue is a convention drift, research current best practice for the underlying class of problem, and design concrete process-level prevention moves — for lesson-tagged issues also judge whether the lesson's wording, trigger or placement is what failed. |
| `retro/save` | Write the approved draft to the primary plan's directory as `retro.md` — frontmatter carrying the plans list, date, cross-plan goal summary and the per-plan verdicts — check it covers the working set, then fire the exit transition, whose hook stamps the retro reference and goal verdict on every plan and moves the siblings; close on the saved-retrospective report and the `/learn` offer, never launched. |
| `retro/synthesize` | Draft the retrospective against the retrospective template — wins, per-issue what-happened / root-cause / impact, lesson gaps, and action items split into one-time tasks and standing heuristics — run the template's self-review checklist and fix every `no`, then show the user a chat summary in the pre-save summary format while holding the full draft in context, unwritten. |

**Agents:**

- `agent:booping-researcher` — Phase 0 session-log search: scan ~/.claude/projects/ across all session logs for the plan's time window and aggregate into a structured summary of user questions, blockers, and detours

### user-stories

| Step | Summary |
| --- | --- |
| `user-stories/build-index` | Compose a feature table into the priority-tagged feature index, left unconfirmed for human review. |
| `user-stories/gherkin` | Specify one feature's stories as Gherkin — one `Feature:` per story, its behaviour rules and the examples illustrating them. Can be paralleled as one agent per feature. |
| `user-stories/reshake` | Transform a product doc (brief, specs, or grouped user stories) into a feature table — capabilities swept out of the input's grouping and regrouped into deliverable features. |
| `user-stories/stories` | Elaborate one mapped feature into its stories document — the feature's open questions and its user stories, drawn from the story map and the project material. Can be paralleled as one agent per feature. |
| `user-stories/story-map` | Map one confirmed-index feature into its epic story — value, scope boundary, and the story slots later steps fill. Can be paralleled as one agent per feature. |

## Step: Dedup Sweep
Before drafting the review table, check whether each candidate duplicates or conflicts with existing coverage:

The lookup set is:

- `{home_dir}/_lessons/` — global lessons, shared across projects (the vault-home base is `booping config-get home_dir`). Read-only here; a duplicate found in it still becomes an update to that file.
- `{vault}/_lessons/` — this project's lessons, shadowing a global lesson of the same filename. The only root this run writes new lessons into.
- The vault's `_booping/` extension files and the attached repo's `CLAUDE.md` — the non-lesson targets.
- The vault's legacy `lessons/`, if it still exists — **read-only, duplicate context only**. Never write here and never route a row to it; a candidate already covered there is reported as such and, if accepted, written into `{vault}/_lessons/` with `targets:`.

Skip silently when a directory is empty or a file is absent.

Record a sweep verdict per candidate as one of:

- `new` — no prior coverage at any target.
- `update existing at target X` — duplicate or refinement of a rule already written at `X`; the candidate becomes an update to `X`, not a fresh write at a different target.
- `conflict with existing at target X` — surface to the user in the review table as a visible flag.

## Step: Review Table
Render the review table using the format defined in [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md), with one added column: **Targets**.

Every row carries a Targets cell — comma-separated entries from the target space rendered in `extract-candidates`, using the three entry forms and exact names only, no globs or wildcards:

- `{playbook}` — the lesson applies to the whole playbook
- `{playbook}/{step}` — it applies to one step of it
- `agent:{id}` — it applies to one agent

A `lesson` row's Targets cell is written verbatim into the file's `targets:` frontmatter list, so it must be non-empty. Rows of any other type carry `—`: the file path is their routing.

Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.

## Step: Write
After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape inlined below. The `targets:` list is the row's Targets cell verbatim, one entry per line. The `retro:` frontmatter points at the run's retrospective, `plans/{primary-slug}/retro.md`.
- `_booping/skill_{name}.md` — per-skill extension in this project's vault.
- `_booping/agent_{name}.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target.


---
id: {{N}}                                      # monotonically-increasing integer; matches the filename prefix
title: {{One-sentence rule as a prescriptive statement}}
targets:                                       # what this lesson is injected into; exact names only, no globs
  - {{playbook}}                               # or {{playbook}}/{{step}}, or agent:{{agent-id}}
retro: retrospectives/YYYYMMDD-{{kebab-title}}.md   # the retro that surfaced this lesson
created: YYYY-MM-DD                            # date this lesson was extracted
---

{{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}}

**Example**: {{One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via `retro:` frontmatter.}}

## Step: Transition
# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Fired from the workdir, once every accepted item is written:

```bash
booping playbook-transition learn done
```

The command writes the primary plan's `status:`, then runs `close-working-set`, which moves every sibling in the retrospective's `plans:` list to `done`, re-renders the vault's `sprints.md`, and commits the plans together with the `_lessons/` and `_booping/` files this run wrote. Nothing here hand-edits plan frontmatter or runs `booping vault-commit`.

```
awaiting-learning → done
script close-working-set: ok
```

That report is authoritative — do not re-read the plans to verify the moves.

## 2. Repo `CLAUDE.md` commit

If `write` also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd {repo-path}
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## 3. Closing report

Post in chat: the plans closed with their new statuses, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/learn` re-offer; the working set is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a plan still at `awaiting-learning` takes the transition alone; a plan already at `done` is only re-reported, with the transition line reading `already at done — no transition taken`.
