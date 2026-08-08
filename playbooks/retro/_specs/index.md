---
status: building-steps
reviewed_at: 20260802 14:26
playbook_yaml_reviewed_at: 20260802 14:43
---
# retro — Decomposition

Write one project- and plan-specific retrospective per run, grounded in the session record, the
plan as written and the user's own words — never in vibes, and never in cross-project
generalization. The **preamble resolves the plan** before the first step — the invocation
argument, else the candidate table of finished plans no retrospective covers yet (`status: done`
with `retro: null`). Intake then settles the working set: the queue membership validated, and
every other queued plan offered as include / postpone / skip. Prepare runs next — built exactly on the skill's
Phase 1 — reading each adopted plan for context only, building the issue list and **withholding**
it: `gather-feedback` asks the four open-ended questions verbatim before the user has seen a
single mined item, which is the whole reason the two are separate steps. Issue triage and the
per-plan goal verdict follow the open-ended round; research does per-issue root-cause and
prevention work on what survived; synthesize drafts against the retrospective template and holds
the draft in context; save writes it and takes the exit transition.

The run workdir is the **vault root** and the machine's artifact is a standalone retrospective,
`retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — one file per run, whatever the size of the
working set, addressed with `--target` because the machine declares no `artifact:`. Retro is a
**separate track from the plan lifecycle**: the plans it covers are already `done` and stay there,
joined to the run only by the `retro:` back-link the exit hook stamps on each of them. A run
resumes from the retrospective's own `status:`, and hands to `/learn` at the exit. The
canonical `/retro` skill is untouched and remains the default entry point; the step bodies carry
its existing wording rather than expanded prose, and every surface it loads — the retrospective
template, the session-log extraction and plan-lesson-check briefs, the pre-save summary format,
the agent roster and the transitions slice — is wired into the step that needs it.

## Graph

```yaml
graph:
  intake: []
  prepare: [intake]
  gather-feedback: [prepare]
  research-issues: [gather-feedback]
  synthesize: [research-issues]
  save: [synthesize]
```

A flat chain, no subgraph and no parallel wave. Multi-plan runs do not repeat the graph: one run
produces one retrospective across the whole working set, so the per-plan work (reading the plans,
mining their sessions, taking each plan's goal verdict) is internal to the steps that own it.
`prepare` runs *before* `gather-feedback` and deliberately shows nothing — the ordering is
what protects the open-ended answers from anchoring.

## Steps

| Step            | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Inputs                                                                                                                                                                                                                                                                                                   | Artifact                                                                                                                                                                                    | Gate                                                                                                                                                                                                               | Delegation                                                                                                                     | Model         | Spec                                   |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ------------- | -------------------------------------- |
| intake          | settle the working set the run covers: validate that the plan the preamble resolved sits at retro's entry status, offer every other plan at that status as include / postpone / skip-and-mark-done, and apply the skip moves — reading the adopted plans is `prepare`'s                                                                                     | the plan(s) named at invocation or picked from the candidate table; each plan's current lifecycle status and whether it is a valid entry point; the other plans sitting at the same status and what the user wants done with each | the working set and its primary plan, held in conversation; dropped plans moved to their own exit status                                                                                    | none — the include / postpone / skip questions are asked in-step; a plan at the wrong status stops the run                                                                                                         | inline                                                                                                                         | opus-5:medium | [spec](steps/intake/index.md)          |
| prepare         | built exactly on the skill's Phase 1 Prepare: read each adopted plan in full for context only — scope, SP totals, dates, decisions on record — then build the issue list without showing it: delegate two briefs in parallel — session-log mining for user tensions, late change requests, code feedback and ignored lessons, and a plan-stage lesson check for gaps in the plan as written — then cross-check both returns against the lesson set and `_booping/skill_retro.md`, adding what either brief missed and dropping false positives; each item carries source, trigger and a one-line orchestrator interpretation | the adopted plans read in full; the project's accumulated lessons, passed verbatim with each brief; the session record covering the plans' time window; the plan text as written; the project-local retro extension                                                                     | the issue list, held in conversation and withheld from the user                                                                                                                             | none — nothing is presented at this point                                                                                                                                                                          | assisted — two parallel briefs to the researcher agent from `config.research_agent`, one per brief                             | opus-5:medium | [spec](steps/prepare/index.md)     |
| gather-feedback | take the user's raw open-ended take before any mined finding is mentioned — four questions asked verbatim, one at a time, each with a free-text option — then walk every mined item in batches for accept / dismiss / the user's own wording, and close by asking, per plan, whether the plan's goal was reached, the goal presented verbatim so the verdict is judged against what was actually planned                                                                                     | the user's own experience of the sprint; how closely related the plans in the working set are; the mined issue list and each plan's stated goal, touched only after all four answers are in                                                                                                                                    | the user's open-ended answers, the accepted issues in the wording carried forward, and the per-plan goal verdicts, held in conversation                                                                                                                                         | none — the step is itself the elicitation; its rule is that no mined finding is mentioned before the open-ended round closes                                                                                                                     | inline                                                                                                                         | opus-5:medium | [spec](steps/gather-feedback/index.md) |
| research-issues | do focused root-cause work on each accepted issue: read only the files the trigger or the user's wording implicates, compare documented project conventions against what the code actually does where the issue is a convention drift, research current best practice for the underlying class of problem, and design concrete process-level prevention moves — for lesson-tagged issues also judge whether the lesson's wording, trigger or placement is what failed | the accepted issues with the user's wording; the files each issue implicates; the project's documented conventions versus what the code does; current external best practice for the underlying class of problem; for lesson-tagged issues, the lesson's rule, trigger and placement                     | per issue: root cause, prevention options and any follow-up, held in conversation                                                                                                           | none — the findings are reviewed as part of the draft                                                                                                                                                              | assisted — researcher agent for wide research that must aggregate many sources; the implicated-file reads stay with the runner | opus-5:medium | [spec](steps/research-issues/index.md) |
| synthesize      | draft the retrospective against the retrospective template — wins, per-issue what-happened / root-cause / impact, lesson gaps, and action items split into one-time tasks and standing heuristics — run the template's self-review checklist and fix every `no`, then show the user a chat summary in the pre-save summary format while holding the full draft in context, unwritten                                                                                  | the accepted issues with their root causes, prevention options and follow-ups; the user's wins and open-ended answers; the per-plan goal verdicts; the retrospective structure and its self-review checklist; the pre-save summary format                                                                | the retrospective draft, held in context; its summary posted in chat                                                                                                                        | the run's single review gate — the user approves the draft from the summary; a refine request loops the draft and re-presents it, a cancel drops the draft and ends the run with nothing written and no transition | inline                                                                                                                         | opus-5:medium | [spec](steps/synthesize/index.md)      |
| save            | write the approved draft to `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — frontmatter carrying the primary plan, the plans list, date, cross-plan goal summary and the per-plan verdicts — then take the exit transition against that file, whose hook stamps the retro reference and goal verdict on every plan in the working set, and report the saved retrospective and offer `/learn` without launching it                                                   | the approved draft; the retrospective's frontmatter shape — primary plan, plans list, date, goal summary, per-plan verdicts; the working set and which plan is primary; the exit transition and the stamps it applies                                                                                                  | `retrospectives/{slug}.md`; every plan in the working set carrying the retro reference and goal verdict, its `status:` untouched; the closing report in chat | none — the writes follow the approval already taken at synthesize                                                                                                                                                  | inline                                                                                                                         | opus-5:medium | [spec](steps/save/index.md)            |

The run edits nothing but the retrospective: every finding lands in that one file, and all
plan-file mutation is the transition's, never a hand edit.

## States

One machine, `run` — an **artifact lifecycle**, not a procedure tracker: its statuses belong to
the retrospective the run writes, never to a plan, so the machine is one non-terminal status wide
(`awaiting-retro` → `awaiting-learning`ᵗ) and is addressed with `--target` from the vault root. The
single exit edge carries the run's one review gate, stamps `reviewed_at` on the approved
retrospective, and closes the whole multi-plan working set through the shared
`playbooks/_scripts/close-working-set` hook. Full chart —
inventory, transitions, script contract, sibling-move call, resume frontier:
[states](states.md).

## Questions

- [x] ~~Where do the issue walk and goal verdicts land after `triage-issues` retired?~~ —
      **`gather-feedback`**, which now mirrors the skill's Phase 2 whole: the open-ended round
      first, then the skill's 2b issue triage and per-plan goal verdicts in the same step,
      still behind the all-four-answers-in rule.

The user confirmed the brief and instructed the run to proceed without further
review gates. The calls the runner made in its place, each recorded so the later steps can
re-open one if it proves wrong:

- [x] ~~Where does plan resolution happen — preamble or intake?~~ — the **preamble**, as in
      `develop`: the invocation argument, else the candidate table of plans at retro's entry
      status. The workdir (the primary plan's directory) is therefore known before the first step
      and the machine is readable on entry; intake settles only the *working set* — sibling
      plans, and the wrong-status stop.
- [x] ~~One step for the two Phase-1 briefs, or two detached steps in a parallel wave?~~ — **one
      assisted step**. The lesson set must reach both briefs verbatim from the runner, and the
      post-brief cross-check is explicitly the runner's, not an agent's; a parallel wave would
      require both to be detached and would hand the vault lesson read to the agents.
- [x] ~~Are the open-ended questions and the issue triage one step or two?~~ — **two**. The
      skill's anti-anchoring rule (raw take before any finding is shown) becomes structural
      instead of a sentence a long step body can lose.
- [x] ~~Does the run persist intermediate findings so a resumed run keeps them?~~ — **no**. The
      issue list, the accepted issues and the draft live in conversation, as groom's research
      steps do; only the retrospective and the covered plans' frontmatter are written.
      Resumption granularity is therefore the whole run — a resumed run re-mines rather than
      picking up mid-analysis. Accepted deliberately: mining is the cheap part, and a finer
      run-local status set would name a frontier nothing on disk can be resumed from.
- [x] ~~How do plans get stamped, given they are not the machine's artifact?~~ — by script.
      **Settled in [states.md](states.md)** (runner's call): split by move — drops at intake take
      `_scripts/drop-plan {slug}`; the adopted working set at save folds into the exit edge's
      `script close-working-set`, because a file-targeted hook cannot carry a runtime slug.
- [x] ~~Does the retrospective keep the skill's `retrospectives/` home?~~ — **yes**, and no plan
      status moves with it. Superseded the authoring run's `plans/{primary-slug}/retro.md` answer:
      the retrospective is a standalone `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md`, the
      run's `--target`, and the plans it covers stay `done` with only a `retro:` back-link. The
      queue is `{status: done, retro: null}` rather than a status of its own.
