---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# prepare

Built **exactly on the skill's Phase 1 Prepare** — the body carries its wording with the minimum
deviations a playbook step needs: the `Lessons` block is rendered in-step (the preamble does not
load it), the phase cross-references become step names, and "skill" becomes "step". It replaces
the former `mine-issues` and `triage-issues` pair; triage's duties moved into `gather-feedback`,
which now mirrors the skill's Phase 2 whole.

## Contract

- **Needs** —
  - each plan in the working set, read in full — for **context only**: scope, SP totals, dates,
    decisions on record; a reference for understanding issues that surface later, never a target
    for orchestrator analysis
  - the project's accumulated lessons, in full, to travel verbatim with each brief
  - the session record covering the plans' time window
  - the plan text as written — frontmatter, milestones, tasks, DoDs, Verify lines
  - `_booping/skill_retro.md`, for the cross-check
- **Value** — the run's raw material, built and withheld. Two briefs are dispatched **in
  parallel**, one agent each, the lesson set pasted verbatim into both:
  - **A. Session-log mining** — execution-stage extraction: user tensions, late change requests,
    code feedback, ignored / unapplied lessons. No other lessons loaded, no raw log text copied
    back.
  - **B. Plan-stage lesson check** — the plan(s) cross-checked against the same lesson set,
    returning plan-stage lesson gaps only; gaps reported, never fixed.

  The output is the **issue list**, held in context: every tension, late change, code-feedback,
  execution-stage ignored-lesson and plan-stage lesson-gap item, each carrying **source**,
  **trigger** and a **one-line orchestrator interpretation**. The orchestrator cross-check —
  still before `gather-feedback` — re-scans the lesson set and `_booping/skill_retro.md` against
  both agents' full output, adds what either missed, drops or corrects false positives, using
  only what is in context. Nothing else is derived from the plan — no "decisions deviated" /
  "tech debt" / "coverage gap" findings; the user owns issue identification.
- **Output files** —
  - none — the issue list is held in conversation and **not presented to the user**:
    `gather-feedback` runs first to avoid anchoring.
- **Harness return** — none: the step is runner-performed under `inline_steps`, so the list
  stays in the driving conversation; nothing from it is mentioned until after the open-ended
  round.
- **Review gate** —
  - none — nothing is presented at this point; the run's single gate sits on the draft at
    `synthesize`
- **Delegation** — assisted: the runner reads the plans and performs the cross-check itself;
  only the two briefs' heavy reads leave its context, to the researcher agent
  `config.research_agent` names, both spawned in one message so they run concurrently.
