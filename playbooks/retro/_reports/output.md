Produce a project- and plan-specific retrospective grounded in session logs, code diff, and user feedback — not vibes. No cross-project generalization, no candidate lessons. One run produces one retrospective, grounded in the session record, the plan as written, and the user's own words — never in vibes, and never in cross-project generalization.

## Guidance

- Date & time: 1970-01-01 00:00
- The run's artifact is a standalone retrospective, `retrospectives/197001010000_{kebab-title}.md` — one file per run, whatever the size of the working set.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target retrospectives/{slug}.md`, since the machine declares no `artifact:`.
- The retrospective carries `plan:` (the primary plan's path); each covered plan is linked back by the `retro:` key the exit hook stamps. Plan `status:` is never touched here.
- Candidate plans are the ones the table below lists — the `core.retro_playbook.queries.candidates` query.

## Plans awaiting retro

| Status | SP | Title | Created | Completed | Path |
| --- | --- | --- | --- | --- | --- |
| done | 2 | Login timeout fix | 1970-01-02 | 19700102 10:00 | plans/19700102-login-timeout/index.md |
| done | 5 | Widget search | 1970-01-01 | 19700101 12:00 | plans/19700101-widget-search/index.md |



## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
| `booping:booping-researcher` | Phase 0 session-log search: scan ~/.claude/projects/ across all session logs for the plan's time window and aggregate into a structured summary of user questions, blockers, and detours | Single-file reads — call Read directly; Phase 2 sprint analysis — stays in the orchestrator; Phase 4 lesson cross-check — stays in the orchestrator using the in-context lesson set |



## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Settle the working set the run covers — validate that every named plan is in the preamble's candidate table, offer every other candidate as include / postpone / skip-retro, apply the skips via `_scripts/drop-plan` (which stamps the `retro: skipped` sentinel), then read each adopted plan in full for context only: scope, story points, dates and decisions on record, never as a source of runner-derived findings. | — |
| `prepare` | `intake` | Read each adopted plan in full for context only, then build the issue list without showing it — session-log mining and a plan-stage lesson check delegated in parallel, the lesson set passed verbatim with each brief — and cross-check both returns against the lesson set and the project-local retro extension; the list is withheld until gather-feedback has the user's raw take. | — |
| `gather-feedback` | `prepare` | Take the user's raw open-ended take before any mined finding is mentioned: four questions asked verbatim, one at a time, each with a free-text option; then walk every mined item in batches for accept / dismiss / the user's own wording, and close by asking per plan whether the plan's goal was reached, the goal presented verbatim as written. | — |
| `research-issues` | `gather-feedback` | Do focused root-cause work on each accepted issue: read only the files the trigger or the user's wording implicates, compare documented project conventions against what the code actually does where the issue is a convention drift, research current best practice for the underlying class of problem, and design concrete process-level prevention moves — for lesson-tagged issues also judge whether the lesson's wording, trigger or placement is what failed. | — |
| `synthesize` | `research-issues` | Draft the retrospective against the retrospective template — wins, per-issue what-happened / root-cause / impact, lesson gaps, and action items split into one-time tasks and standing heuristics — run the template's self-review checklist and fix every `no`, then show the user a chat summary in the pre-save summary format while holding the full draft in context, unwritten. | The run's single review gate — explicit user approval of the draft, asked for in prose in the same message as the summary, never via `AskUserQuestion`. "Save it" counts, silence never does; the approval is what `save` writes on and what the exit edge's first gate names. A refine request loops in place — adjust framing, wording or which issues land, re-post the summary whole with what changed marked as changed, and re-ask; the loop is unbounded, a refine needing new evidence stays in this step, and the run never advances to `save` on its own. A cancel drops the draft and ends the run: nothing written, no transition, the plan left at its entry status. |
| `save` | `synthesize` | Write the approved draft to `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — frontmatter carrying `plan:`, `plans:`, `title`, `created` and the per-plan `goal_verdicts:`, no `status:` — check it covers the working set, then fire the exit transition with `--target` on that file, whose hooks stamp the retro back-link and goal verdict on every plan; close on the saved-retrospective report and the `/playbook learn` offer, never launched. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state retro --workdir <run workdir> --target {path}
```

### State: run

- Referenced by: outer graph
- Artifact: named per run — pass `--target {path}` (relative to the run workdir) on every call
- Initial status: `awaiting-retro`
- Advance: `booping playbook-transition retro <to> --target {path} --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-retro` | `awaiting-learning` | save wrote the approved retrospective to `retrospectives/{slug}.md`, the run's `--target` | explicit user approval of the draft captured at synthesize — "save it" counts, silence never does; the retrospective's `plans:` list covers the whole working set and `goal_verdicts:` carries a verdict for each, since the hook script reads both |
| `awaiting-learning` | *(terminal)* | — | — |

## Step: Intake
The candidate plans are the **Plans awaiting retro** table of the preamble — the `core.retro_playbook.queries.candidates` query, SPs included.

Resolve `$ARGUMENTS` to plan paths.

**No plans provided**: present the list to the user via `AskUserQuestion` with `multiSelect: true` (one option per plan). The selected plans become the working set.

**One or more plans provided**:

1. Validate each provided plan is in the candidate table. A plan that is not there is either already retro'd or not finished; STOP with this verbatim error:

   > `retro playbook requires a finished plan with no retrospective yet; {plan-path} is not in the candidate list above. Use the list to pick a candidate.`

2. Identify *other* candidates (those in the table but not in `$ARGUMENTS`). If any exist, ask the user per other plan via `AskUserQuestion`:
   - **Include** — add to this retro run alongside the provided plans.
   - **Postpone** — leave the plan where it is (no-op).
   - **Skip retro** — exclude the plan from this run and from the queue for good.
3. Close each "skip retro" plan before moving to the next step, one `_scripts/drop-plan {slug}` invocation per plan — never a hand edit. The script stamps `retro: skipped` (the sentinel that drops the plan out of the candidates query) and `goal: skipped`, and commits the vault, one commit per plan.

## The report — posted in chat

```markdown
## Retro intake

{A table with columns: action (taken | postponed | skipped), plan path, plan description, SPs }
```

## Step: Prepare
Read each plan in the working set in full — for **context only**: scope, SP totals, dates, decisions on record. The plan is a reference for understanding issues that surface in the later steps, not a target for orchestrator analysis (no derived "decisions deviated" / "tech debt" / "coverage gap" findings — the user owns issue identification; the step does homework and suggests options).




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


The output of this step is the **issue list** — every tension, late change, code-feedback, execution-stage ignored-lesson, and plan-stage lesson-gap item from the agents' deliverables, held in context. Each item carries: source (tension / late change / code feedback / ignored lesson / plan-stage lesson gap), trigger, and a one-line orchestrator interpretation.

**Orchestrator cross-check** (still before `gather-feedback`): re-scan the lesson set and `_booping/skill_retro.md` against both agents' full output. Add any lesson-related item either agent missed; drop or correct any false positive. Use only what is in context — no additional loads.

Do **not** present this list to the user yet — `gather-feedback` runs first to avoid anchoring.

## Step: Gather Feedback
# Take the user's raw feedback

The mined issue list is in context and stays there: mention no finding, read none aloud, ask
nothing beyond the four questions below until all four answers are in. This is the user's raw
take, before any runner framing can anchor it.

## Per plan or once

Only when the working set holds more than one plan, ask up front whether to run the four
questions once across the set or once per plan — the user's call, on how closely related the
plans are. A single-plan run skips this and goes straight to the questions.

## The four questions

One `AskUserQuestion` call per question, one at a time, waiting for each answer before posing the
next. Ask each **verbatim**, in this order. No `"Free-text:"` prefix, no
`"(Skip if … use Other.)"` parenthetical, no rephrasing for tone:

1. *"How do you feel about the sprint overall?"*
2. *"How did the code review go?"*
3. *"What stood out as a win — any decision, moment, or move that worked notably well?"*
4. *"Any issues from this sprint you want to bring to the retro?"*

Each call offers a short set of neutral, generic takes on that question plus `Other` for free
text — so a quick answer is one click. The options are never derived from a mined finding and
never name a file, a commit or an issue from this sprint; the user's free text wins over any of
them. A declined question is recorded as no answer and the run moves on — never re-asked, never
pressed, never filled in.

A per-plan pass repeats the same four questions under a `### plans/{slug}/index.md` heading per
plan. Reading the answers waits until the mined items are on the table — the triage below.

## Issue triage

Walk every item from the issue list `prepare` withheld. Batch up to **5 items per
`AskUserQuestion` call** (one question per item within the call); split into multiple calls when
there are more than 5. For each item: cite the source + trigger, then the orchestrator's one-line
interpretation, then offer two options plus `"Other"`:

1. **Accept as-is** — keep the orchestrator's framing untouched; carry into `research-issues`.
2. **Dismiss** — drop from the retrospective; not a problem worth carrying forward.
3. **Other** — user types their own take; record their wording into the issue's notes and carry
   it into `research-issues`.

Mark each item with the user's choice and any free-text. Accepted and "Other" items are the
**accepted issues** for `research-issues`; dismissed items disappear.

After the issue walkthrough, ask the user explicitly per plan via `AskUserQuestion`: *"Was the
goal of this plan reached?"* — present the plan's stated goal verbatim from frontmatter (or the
plan's opening paragraph if no `goal:` field) so the user is judging against what was actually
planned. Options: `success` (goal reached), `partial` (partially reached), `fail` (not reached).
The user owns this call; the step does not derive it.

## The record — posted in chat

Nothing is written to disk and no plan is touched.

## Step: Research Issues
For each **accepted issue** from the triage at `gather-feedback`, do focused root-cause work:

1. **Code reading** — read the related files referenced by the trigger or the user's refinement. No broad scans; only the files specifically implicated. When the issue involves convention or pattern mismatches, also read the project `CLAUDE.md` and compare against what the code actually does — a stale or incomplete `CLAUDE.md` is a common root cause for convention drift.
2. **Web research** — `WebSearch` for current best practices for the underlying class of problem; `WebFetch` to pull a specific doc when a search result needs verification. For wide research that must aggregate across many sources, delegate per the agent roster above.
3. **Prevention options** — synthesize concrete, process-level moves that would have headed this off. Examples of the right shape: an extra planning step ("when env vars change, include a CI-config task in the plan"), a specific edge case to anticipate up-front, a user notification to surface at the right moment ("communicate which env vars need to be added in GitHub before merge"), a developer-workflow tweak ("run the formatter after every change"). For accepted issues tagged as ignored-lesson or plan-stage lesson gap, also review whether the lesson itself needs to change — sharper wording, a clearer trigger, a different placement (planning vs execution), or whether the process around enforcing it failed (lesson exists but never reached the right phase).

Each item ends with three deliverables in context, ready for `synthesize`:

- **Root cause** — what the underlying issue actually is (one to three sentences).
- **Prevention options** — one or more concrete moves that would have surfaced or prevented this.
- **Optional follow-up** — concrete next step the user might take, if any.

### Lesson gaps

Loaded lessons (from `~/Claude/{project}/lessons/` or project `CLAUDE.md` instructions) that should have prevented or caught one or more flagged problems but were not applied. For each:

- `lessons/XXXX_lesson-title.md` — rule was "...", but we did "..." instead, which caused [which issue(s)].

## Step: Synthesize
# Draft the retrospective and take the approval

Everything the run gathered arrives here: the accepted issues in the wording triage settled on,
each with its root cause, prevention options and any follow-up; the wins the user named and their
other open-ended answers, in their own words; the per-plan goal verdicts; and the sprint stats the
verdict line quotes — SP total, commit count and short SHAs, planned-to-completed elapsed time,
milestone DoD pass rate, Final Verification pass rate.

Nothing is written here. The draft is composed once, measured against its own checklist, and held
in context until the user approves — `save` owns the file. Holding it unwritten is what makes a
cancel cost nothing: no file, no transition, no cleanup.

An empty accepted set is a legal draft: the wins, the open-ended answers and the goal verdicts
carry it, and "What went wrong" says plainly that nothing survived triage.

## 1. Draft the body

Read the [retrospective template](${CLAUDE_PLUGIN_ROOT}/docs/retrospective_template.md) now and
compose the full body against its structure — wins, one `#### {Issue name}` block per accepted
issue with **What happened** / **Root cause** / **Impact**, the lesson gaps cited by path with the
rule quoted and the gap named, and the action items typed Task / Heuristic.

Draft the **body only**. The frontmatter — the plans list, the date, the per-plan verdicts — is
`save`'s. The one piece you do draft is the **cross-plan verdict sentence**: it is the summary's
verdict line, and `save` lifts it into `goal_summary:`.

## 2. Self-review — yours, not the user's

Run the template's self-review checklist against the draft and fix every `no` **before** anything
is posted. What
the user sees is a finished document, never a draft with caveats and never a list of pending
items.

## 3. Post the summary

The user reads a compact chat summary — enough to judge framing and decide, never the full body.
Follow the [retro pre-save summary format](${CLAUDE_PLUGIN_ROOT}/docs/retro_summary_format.md):
header, verdict line, what went well, the issue table (`#`, `Issue`, `Cause`, `Impact`,
`Lesson touched`), the action-item table (`#`, `Action`, `Owner`, `Status`), then the takeaways,
in that order and under ~40 lines. An empty table renders as `_No accepted issues._` /
`_No action items._`.

No frontmatter, no save path, no commit command, no candidate-lessons section — those are `save`'s
and `/playbook learn`'s surfaces.

## 4. Ask for the approval

This is the run's **single review gate**. The ask is **prose in the same message as the summary**,
never an `AskUserQuestion` call:

> Save this retrospective? Approving writes it to the plan directory and moves the plan on.
> Tell me what to change instead and I will re-draft, or say cancel and nothing is written.

**Approval** — "save it" counts, silence never does. Record it in the user's own words: `save`
clears the exit edge's first gate on it.

**Refine** loops in place, unbounded, and never advances on its own: adjust framing, wording or
which issues land, then re-post the summary **whole** with what changed marked as changed, and
re-ask. A refine that needs new evidence stays in this step — read the implicated file yourself and
re-draft. The graph has no loopback; the run never returns to `research-issues`.

**Cancel** drops the draft and ends the run — nothing written, no transition, the plan left at its
entry status.

## Step: Save
# Save the retrospective

The approved draft arrives from `synthesize` exactly as the user approved it, together with the working set, its primary plan, and the per-plan goal verdicts. Write it as approved — no re-drafting, no new findings, no wording the user has not seen.

The order below is fixed: write the file, check its frontmatter covers the working set, advance the run, report.

## 1. Write the retrospective

One file per run, whatever the size of the working set: `retrospectives/197001010000_{kebab-title}.md` under the vault root, which is the run workdir. The title is the run's own, kebab-cased. Plans are never given a copy — they are linked by the `retro:` stamp the exit hook applies.

The approved draft goes in verbatim, under frontmatter carrying exactly these keys:

- `plan:` — the primary plan's vault-relative path.
- `plans:` — always a YAML list, even for a single plan; every entry a vault-relative path, the primary included.
- `title:` — the retrospective's title, the same one the slug is built from.
- `created:` — `1970-01-01 00:00`.
- `goal_verdicts:` — those same plan paths mapped to the verdict the user gave at triage.

No `status:` and no `reviewed_at:` are written by hand: the exit transition bootstraps the one and stamps the other.

```yaml
---
plan: plans/20260728-09-15_playbook-run-state/index.md
plans:
  - plans/20260728-09-15_playbook-run-state/index.md
  - plans/20260729-11-40_playbook-reports/index.md
title: Playbook run state and reports
created: 2026-08-02 14:10
goal_verdicts:
  plans/20260728-09-15_playbook-run-state/index.md: success
  plans/20260729-11-40_playbook-reports/index.md: partial
---
```

## 2. Check the frontmatter against the working set

Before firing anything: every plan in the working set appears in `plans:`, and every entry in `plans:` has a verdict in `goal_verdicts:`. This is the exit edge's second gate, and it is checked against the file just written because the hook script reads both keys and aborts the transition on either gap.

## 3. Transition

Once the file is on disk, advance the run per the `## State` section — from the vault root, passing `--target retrospectives/{slug}.md` for the file just written. The exit edge's hooks stamp the `retro:` back-link and the goal verdict on every plan in the working set and commit the vault; nothing here hand-edits plan frontmatter.

## 4. Closing report

Post in chat: the retrospective's path, the plans covered with their verdicts, then a section per plan tabling the issues reported into the retro — each with its root cause and its action items — the issue and action-item counts, and the `/playbook learn` offer stated as a command the user may run. Offer it; never launch it.

```markdown
**Retrospective saved** — `retrospectives/202608021410_playbook-run-state.md`.

| Plan | Verdict |
| ---- | ------- |
| `plans/20260728-09-15_playbook-run-state/index.md` | success |
| `plans/20260729-11-40_playbook-reports/index.md` | partial |

### `plans/20260728-09-15_playbook-run-state/index.md`

| # | Issue | Root cause | Action items |
| - | ----- | ---------- | ------------ |
| 1 | Migrations shipped with the code they support | Lesson filed execution-stage; nothing reads it while a plan is drafted | Re-file the lesson as planning-stage |
| 2 | Verify commands ran only at sprint end | Plan put Verify at sprint level, not per milestone | Heuristic: every milestone carries its own Verify lines |

### `plans/20260729-11-40_playbook-reports/index.md`

| # | Issue | Root cause | Action items |
| - | ----- | ---------- | ------------ |
| 3 | Reports drifted from the fixture vault | Recipe renders against a vault no test pins | Task: pin the fixture vault in CI |

3 issues carried, 2 action items. Both plans link to the one shared retrospective.

Next, if you want the lessons absorbed: `/playbook learn retrospectives/202608021410_playbook-run-state.md`
```

## Replay

A replay that finds the retrospective already written re-fires nothing it does not need: a run still at the entry status takes the transition alone, a run already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
