

# booping — /retro

Produce a project- and plan-specific retrospective grounded in session logs, code diff, and user feedback — not vibes. No cross-project generalization, no candidate lessons.

## Project Context


```yaml
name: claude-booping
directory: /home/anton/Dev/@A/notes/projects/claude-booping
repo_directory: /home/anton/Dev/@A/claude-booping
git_commit: 4611dfe80ab77086598fbb9922f0dd30a566932c
```


On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## Plan Transitions

This table is the contract: the valid moves and their requirements — `Gates` (must hold before the move) and `On exit (auto)` (the mechanical mutations the move applies). When an internal action matches a `When` trigger, verify every `Gate` holds, then execute the move with one command — it applies every mechanical mutation (status, date stamps, commit snapshot, sprints.md, vault commit) deterministically:

```bash
booping transition <to-status> plans/<plan-file>.md [--also <artifact>...]
```

Pass every vault artifact the skill authored for this move (e.g. a retrospective file, a sibling stub plan) via `--also` so it lands in the same transition commit. Do not hand-edit `status:` or hand-run `git commit` — the command owns all of it. It prints a report of every mutation it applied (`<from> → <to>`, then one line per hook); the report is authoritative — do not re-read the plan to verify.

### `awaiting-retro` — All milestones done; waiting for /retro to write the retrospective.

| To | When | Gates | On exit (auto) |
|----|------|-------|----------------|
| `awaiting-learning` | Retrospective written and saved | Retrospective markdown saved to retrospectives/; Self-review checklist passed | sets `retro`, `goal` |
| `done` *(via review)* | User skips remaining review steps and marks the plan done | — | sets `goal`, `completed` |




## Available Agents

Always delegate to one of the agents listed below — never use any other agent
not on this list, and never do the work directly.


### `booping-researcher`

Invoke via the `Agent` tool with `subagent_type="booping:booping-researcher"`. Pass the briefing in the `prompt` arg.


**Good for:**
- Phase 0 session-log search: scan ~/.claude/projects/ across all session logs for the plan's time window and aggregate into a structured summary of user questions, blockers, and detours


**Bad for:**
- Single-file reads — call Read directly
- Phase 2 sprint analysis — stays in the orchestrator
- Phase 4 lesson cross-check — stays in the orchestrator using the in-context lesson set



## Plan editing

After modifying any plan's SPs or status, run:

```bash
booping render-sprints
```



## Lessons

The following 4 lesson(s) are loaded for the rest of the session. Keep them in context; never silently violate a loaded lesson. If one conflicts with a user request, plan decision, or in-progress task, stop and flag it before continuing.

### Index


- `0004_information-architecture-pattern.md` — Run every prompt artefact through the four-check information architecture pass

- `0005_stale-reference-cleanup-belongs-in-sprint.md` — Cleanup of references invalidated by a plan belongs inside the same sprint, not a follow-up sweep

- `0006_audience-scoped-content.md` — Scope generated content to its audience — exclude internal-only changes from user-facing output

- `0007_bound-agent-return-contract.md` — Bound an agent briefing's return contract to harness-needed output only



### 0004_information-architecture-pattern — Run every prompt artefact through the four-check information architecture pass

**Rule**: Before saving any prompt-bearing artefact (skill, agent, partial, template, briefing), every block must pass four checks:
- **Scoping** — does this component need this information to do its job? If it belongs to a higher-level orchestrator, move it up; if it's residue from a past correction ("never read any lessons") with no positive rule attached, delete it.
- **Duplication** — does the same block live in other components? Extract to a partial; a single source prevents drift.
- **Configurability** — is this behaviour a user might want to tweak? Partial it so the main flow stays readable and the knob is in one place.
- **Hierarchy** — does every block sit at the right level of detail? Top-level docs describe *what* and *when*; deeper docs describe *how*. A block whose detail doesn't match its level belongs one layer up or down.

**Example**: A skill body contained the full roster of sub-components inline (hierarchy — belongs in a referenced doc), the same roster appeared verbatim in two sibling skills (duplication — extract), one entry was a negative rule with no positive counterpart (scoping — delete), and a threshold the user tunes was hard-coded in prose (configurability — move to config). Four-check pass caught all four in one sweep.


### 0005_stale-reference-cleanup-belongs-in-sprint — Cleanup of references invalidated by a plan belongs inside the same sprint, not a follow-up sweep

**Rule**: When a plan's work invalidates references — deleted partials, renamed agents, status-block lines in CLAUDE.md, broken doc links — the cleanups must be milestone tasks inside the same sprint, with their own DoD. A half-stale working tree at sprint close is itself the documentation gap; "we'll sweep this up after" leaves the repo inconsistent for hours or days and reliably gets dropped.

**Example**: M3 of the /retro template-pipeline migration made deleting `docs/partial_plan_transitions_retro.md` and updating the CLAUDE.md "Status (April 2026)" block its own milestone with explicit DoD checks; both landed inside the migration sprint instead of leaving stale references behind.


### 0006_audience-scoped-content — Scope generated content to its audience — exclude internal-only changes from user-facing output

When generating user-facing content (release notes, user docs, changelogs), filter by audience: include only what that audience interacts with, and drop internal-only churn (CLI internals, build plumbing, refactors users never touch). Audience-scoping is a generation-time decision, not a post-edit cleanup.

**Example**: Generated release notes listed internal `booping` CLI updates users never invoke directly; the same oversharing recurred in the May-21 cli-agent docs review ("no oversharing in docs … internal details of booping cli").


### 0007_bound-agent-return-contract — Bound an agent briefing's return contract to harness-needed output only

Every agent briefing must state the exact shape the agent returns, scoped to only what the orchestrator needs (e.g. "final reply MUST contain ONLY the list of changed files"). Delegation is lossy: an unbounded return contract lets the agent emit surplus prose that rots orchestrator context. Applies wherever briefings are authored — both groom (folding DoD into the brief) and develop (delegating a milestone).

**Example**: Mid-sprint the user had to constrain the agent ("agent just need to return list of changed files, nothing else") because the briefing never bounded the return shape; the fix codified an `OUTPUT_GUIDE`.




## Plans awaiting retro


status	sp	title	created	planned	completed	retro	path
awaiting-retro	34	Groom playbook respec — inline/assisted, plan-as-directory, single gate	2026-08-02	20260801 18:09	20260801 20:01		plans/20260802-groom-playbook-respec.md
awaiting-retro	24	Playbook-authoring into core + delegation-level model	2026-08-02	20260801 18:05	20260801 18:38		plans/20260802-playbook-authoring-core-delegation.md
awaiting-retro	8	File-target frontmatter-update hook syntax	2026-07-31	20260731 12:45	20260731 13:00		plans/20260731-frontmatter-update-file-target-hook.md
awaiting-retro	18	Playbook Lessons — scoped learning artifacts wired into playbook rendering	2026-07-31	20260731 10:28	20260731 11:13		plans/20260731-playbook-lessons.md
awaiting-retro	13	Metadata-driven playbook runner — steps fetch own bodies	2026-07-31	20260731 09:32	20260731 09:47		plans/20260731-playbook-metadata-runner.md
awaiting-retro	21	Playbook Frontmatter Graph — Parallel Step Execution	2026-07-24	20260724 15:21	20260724 15:58		plans/20260724-playbook-frontmatter-graph.md
awaiting-retro	16	Jinja Playbooks — Composed Step Rendering	2026-07-22	20260722 16:05	20260722 16:47		plans/20260722-jinja-playbooks-composed-step-rendering.md


## High-level workflow

1. Input — select / load the plan(s) for retrospective.
2. Prepare — review sessions and plan(s); extract the issue list.
3. User feedback — open-ended overall feedback first, then per-issue triage (refine / accept / dismiss).
4. Per-issue research and analysis — code reading, web research, prevention design for each accepted issue.
5. Synthesize — draft using the retrospective template; run lesson cross-check.
6. Save & transition — write retrospective; apply transitions per the transitions table above; commit.

---

## Phase 0 Input

The current set of plans in `awaiting-retro` is listed in the [Plans awaiting retro](#plans-awaiting-retro) block above (rendered at skill load).

Resolve `$ARGUMENTS` to plan paths.

**No plans provided**: present the list to the user via `AskUserQuestion` with `multiSelect: true` (one option per plan). The selected plans become the working set.

**One or more plans provided**:

1. Validate each provided plan's `status:` is `awaiting-retro`. On mismatch, STOP with this verbatim error:

   > `/retro requires a plan in status 'awaiting-retro'; got '<current-status>' for <plan-path>. Use the list above to pick a candidate.`

2. Identify *other* plans in `awaiting-retro` (those in the inlined list but not in `$ARGUMENTS`). If any exist, ask the user per other plan via `AskUserQuestion`:
   - **Include** — add to this retro run alongside the provided plans.
   - **Postpone** — leave in `awaiting-retro` (no-op).
   - **Skip retro and mark done** — apply the proper transition to the plan now (per the transitions table above) and exclude from this run.
3. Apply each "skip & mark done" transition before moving to Phase 1. One commit per plan.

## Phase 1 Prepare

Read each plan in the working set in full — for **context only**: scope, SP totals, dates, decisions on record. The plan is a reference for understanding issues that surface in Phase 2/3, not a target for orchestrator analysis (no derived "decisions deviated" / "tech debt" / "coverage gap" findings — the user owns issue identification; the skill does homework and suggests options).

In parallel, delegate two reads per the agent roster above. Pass the lesson set verbatim with each brief (use the `Lessons` block already loaded above).

**A. Session-log mining** — execution-stage extraction:

1. Locate sessions referencing each plan (search `~/.claude/projects/`).
2. Extract the user-side messages.
3. Return a structured summary per plan with four sections — what frustrated the user (implementation or planning misses), what the user changed (likely planning misses), what the user said about the code (taste / convention / quality misses), and where loaded lessons appear to have been ignored:
   - **User tensions** — frustration, disagreement, or pushback at the orchestrator's choices. Per item: description (one line), trigger (the orchestrator action, output, or omission that prompted it), optional sparing quote.
   - **Late change requests** — scope additions, reversed decisions, or requirements clarified mid-sprint. Per item: description, trigger (what surfaced the need + roughly when in the sprint).
   - **Code feedback** — comments the user made on the code itself: naming, structure, patterns, conventions, missing tests, dead code, etc. Per item: description, the file or symbol the comment was about, and what the user wanted instead.
   - **Ignored / unapplied lessons** — places where the session record shows behavior that contradicts a lesson included in the brief below. Per item: lesson path, the rule, what happened instead, and which session message(s) surfaced it.

The lesson set to cross-check against is included verbatim with this brief. Do not load any other lessons.

Drop items with low value for the retrospective. Do not copy raw logs into the summary.


**B. Plan-stage lesson check** — separate brief, run in parallel with A:

1. Read the plan file(s) listed in the brief in full — frontmatter, milestones, tasks, DoDs, Verify lines.
2. Cross-check the plan against the lesson set included verbatim in the brief.
3. Return a structured summary per plan with one section:
   - **Plan-stage lesson gaps** — places where the plan as written contradicts or omits a loaded lesson. Per item: lesson path, the rule, where in the plan it should have shown up (milestone / task / DoD / Verify), and what is there instead (or what is missing).

Do not load any other lessons or files. Do not propose fixes; only report gaps.


The output of this phase is the **issue list** — every tension, late change, code-feedback, execution-stage ignored-lesson, and plan-stage lesson-gap item from the agents' deliverables, held in context. Each item carries: source (tension / late change / code feedback / ignored lesson / plan-stage lesson gap), trigger, and a one-line orchestrator interpretation.

**Orchestrator cross-check** (still before Phase 2): re-scan the lesson set and `_booping/skill_retro.md` against both agents' full output. Add any lesson-related item either agent missed; drop or correct any false positive. Use only what is in context — no additional loads.

Do **not** present this list to the user yet — Phase 2a runs first to avoid anchoring.

## Phase 2 User feedback

Two strict sub-flows, in order.

### 2a Overall feedback

Four separate `AskUserQuestion` prompts, one after another, each with `"Other"` for free-text. **Do not** mention any Phase 1 findings yet — the point is the user's raw take before anchoring on the orchestrator's view.

Ask each question **verbatim** as written below. No `"Free-text:"` prefix, no `"(Skip if … use Other.)"` parenthetical, no rephrasing for tone. The `Other` option already signals free-text on its own. Ask in this order, one at a time, waiting for each answer before posing the next:

1. *"How do you feel about the sprint overall?"*
2. *"How did the code review go?"*
3. *"What stood out as a win — any decision, moment, or move that worked notably well?"*
4. *"Any issues from this sprint you want to bring to the retro?"*

Multi-plan: run the set per plan, or once across all plans when they are tightly related (user's call).

These are the only open-ended prompts in the skill — Phase 2b and beyond are targeted.

### 2b Issue triage

Walk every item from the Phase 1 issue list. Batch up to **5 items per `AskUserQuestion` call** (one question per item within the call); split into multiple calls when there are more than 5. For each item: cite the source + trigger, then the orchestrator's one-line interpretation, then offer two options plus `"Other"`:

1. **Accept as-is** — keep the orchestrator's framing untouched; carry into Phase 3.
2. **Dismiss** — drop from the retrospective; not a problem worth carrying forward.
3. **Other** — user types their own take; record their wording into the issue's notes and carry it into Phase 3.

Mark each item with the user's choice and any free-text. Accepted and "Other" items are the **accepted issues** for Phase 3; dismissed items disappear.

After the issue walkthrough, ask the user explicitly per plan via `AskUserQuestion`: *"Was the goal of this plan reached?"* — present the plan's stated goal verbatim from frontmatter (or the plan's opening paragraph if no `goal:` field) so the user is judging against what was actually planned. Options: `success` (goal reached), `partial` (partially reached), `fail` (not reached). The user owns this call; the skill does not derive it.

## Phase 3 Per-issue research and analysis

For each **accepted issue** from Phase 2b, do focused root-cause work:

1. **Code reading** — read the related files referenced by the trigger or the user's refinement. No broad scans; only the files specifically implicated. When the issue involves convention or pattern mismatches, also read the project `CLAUDE.md` and compare against what the code actually does — a stale or incomplete `CLAUDE.md` is a common root cause for convention drift.
2. **Web research** — `WebSearch` for current best practices for the underlying class of problem; `WebFetch` to pull a specific doc when a search result needs verification. For wide research that must aggregate across many sources, delegate per the agent roster above.
3. **Prevention options** — synthesize concrete, process-level moves that would have headed this off. Examples of the right shape: an extra planning step ("when env vars change, include a CI-config task in the plan"), a specific edge case to anticipate up-front, a user notification to surface at the right moment ("communicate which env vars need to be added in GitHub before merge"), a developer-workflow tweak ("run the formatter after every change"). For accepted issues tagged as ignored-lesson or plan-stage lesson gap, also review whether the lesson itself needs to change — sharper wording, a clearer trigger, a different placement (planning vs execution), or whether the process around enforcing it failed (lesson exists but never reached the right phase).

Each item ends with three deliverables in context, ready for Phase 4:

- **Root cause** — what the underlying issue actually is (one to three sentences).
- **Prevention options** — one or more concrete moves that would have surfaced or prevented this.
- **Optional follow-up** — concrete next step the user might take, if any.

## Phase 4 Synthesize

Draft the retrospective following the [Retrospective template](#retrospective-template) section embedded at the bottom of this skill. Follow its sections as written.

Run the template's inline self-review checklist. Any `no` → fix before proceeding.

Then **show the user a summary of the draft in chat** following the [retro pre-save summary format](${CLAUDE_PLUGIN_ROOT}/docs/retro_summary_format.md). Hold the full draft in context; do not write the file yet.

Ask via `AskUserQuestion`: *"Save this retrospective?"* with options:

1. **Save** — proceed to Phase 5 as-is.
2. **Refine** — keep chatting to adjust framing, wording, or which issues land. After each round of edits, re-show the summary and re-ask. Loop until the user picks Save or Cancel.
3. **Cancel** — drop the draft; do not write the file or transition the plan.

## Phase 5 Save & transition

Write the retrospective to `~/Claude/{project_name}/retrospectives/YYYYMMDD-{kebab-title}.md`.

Frontmatter always uses `plans:` as a YAML list (even for a single plan), and `goal_verdicts:` as a YAML mapping from plan path to the user's per-plan verdict captured in Phase 2b:

```yaml
plans:
  - plans/YYYYMMDD-{kebab-title}.md
date: YYYY-MM-DD
goal_summary: <cross-plan one-liner verdict>
goal_verdicts:
  plans/YYYYMMDD-{kebab-title}.md: success  # or `partial` or `fail`
```

Take the transition per the transitions table above for each plan in `plans:`, passing the retrospective file via `--also` so it is committed in the same transition commit:

```bash
booping transition <to-status> plans/YYYYMMDD-{kebab-title}.md --also retrospectives/YYYYMMDD-{kebab-title}.md
```

Then tell the user the retrospective is saved and offer `/learn` to absorb lessons. Do not auto-launch.

## What retro does NOT do

- Does **not** edit any files other than the retrospective itself; the plan transition is owned by `booping transition`. All findings stay in the retro body.






---

## Retrospective template

Follow the structure below when drafting the retrospective body.

### Frontmatter example

```yaml
plans:
  - plans/20260401-feature-x-implementation.md
  - plans/20260408-feature-x-integration.md
date: 2026-04-23
goal_summary: Feature X shipped on time with clean integration; auth layer needed pre-review validation.
goal_verdicts:
  plans/20260401-feature-x-implementation.md: success
  plans/20260408-feature-x-integration.md: partial
```

### What went well

Concrete wins. What was achieved, what worked as designed. Keep it brief — 3–5 bullet points with specifics, not vague praise (avoid "good communication"; say "API contract locked before implementation" instead).

- ...
- ...

### What went wrong

For each issue, include a subsection with this four-line format:

#### {{Issue name}}

**What happened**: Factual description of the problem.

**Root cause**: The underlying pattern or plan/decision blind spot — name it as a pattern, not a restatement of what happened.

**Impact**: What does this cost now (rework, tech debt, user confusion, process delay)?

### Lesson gaps

Loaded lessons (from `~/Claude/{project}/lessons/` or project `CLAUDE.md` instructions) that should have prevented or caught one or more flagged problems but were not applied. For each:

- `lessons/XXXX_lesson-title.md` — rule was "...", but we did "..." instead, which caused [which issue(s)].

### Action items & takeaways

Specific next steps that address the issues above. Two types in one table:

- **Task** — sprint-scoped, one-time work (a fix to ship, a follow-up plan to file, a doc to write). Has an owner and a clear definition of done.
- **Heuristic** — a standing behavioral change for this project, persists until explicitly retired (e.g. "when env vars change, include a CI-config task in the plan").

| # | Type | Item | Owner | Status |
|---|------|------|-------|--------|
| 1 | Task / Heuristic | ... | Next sprint / Person / standing | Planned |

### Self-review checklist

Before committing a retrospective, confirm all items below are true:

- [ ] Each "what went wrong" item has a named root cause (a pattern, not a restatement).
- [ ] Lesson gaps cite existing lessons by path and explain the gap.
- [ ] Items are specific with an owner (or "standing" for heuristics) and a clear next step.
- [ ] Heuristics are concrete enough that someone could apply them next sprint — not platitudes.
- [ ] "What went well" is honest, not inflated to balance criticism.
- [ ] No blame language — focus on decisions and processes, not people.

