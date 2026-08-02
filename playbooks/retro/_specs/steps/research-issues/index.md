---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# research-issues

Built **exactly on the skill's Phase 3** — the body carries its wording with the minimum
deviations a playbook step needs: "Phase 2b" becomes the triage at `gather-feedback`, "Phase 4"
becomes `synthesize`. The former playbook-authored `## What the step leaves behind` report format
was removed; lesson-tagged findings take the short `### Lesson gaps` shape from the
retrospective template instead of the former "lesson verdict" machinery.

## Contract

- **Needs** —
  - the accepted issues in the wording carried forward, each with its source and its trigger
  - the files each issue's trigger or the user's refinement implicates
  - the project `CLAUDE.md`, compared against what the code actually does when the issue is a
    convention or pattern mismatch
  - current external best practice for the underlying class of problem an issue names
  - for lesson-tagged issues (ignored lesson / plan-stage lesson gap), the lesson's rule, its
    trigger and its placement — planning or execution
- **Value** — the homework behind every accepted issue, so the retrospective's action items are
  concrete process moves rather than sentiments. Three moves per issue, per the skill's Phase 3:
  code reading (only the files specifically implicated, no broad scans), web research
  (`WebSearch` for the class of problem, `WebFetch` to verify a specific doc, wide aggregation
  delegated per the agent roster), and prevention options (concrete, process-level moves; for
  lesson-tagged issues also whether the lesson itself needs to change — wording, trigger,
  placement — or whether the process around enforcing it failed).
- **Output files** —
  - none — the findings are held in context for `synthesize`, three deliverables per accepted
    issue:
    - **root cause** — what the underlying issue actually is, one to three sentences
    - **prevention options** — one or more concrete moves that would have surfaced or
      prevented it
    - **optional follow-up** — a concrete next step the user might take, if any
  - lesson-tagged issues additionally take the `### Lesson gaps` shape:
    `lessons/XXXX_lesson-title.md` — rule was "...", but we did "..." instead, which caused
    [which issue(s)]
  - nothing is written and no plan is touched
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block; the deliverables stay in context for `synthesize`.
- **Review gate** —
  - none — the findings are reviewed as part of the draft; the run's single gate is the draft
    approval at `synthesize`
- **Delegation** — assisted: the runner performs the step and owns every judgement in it — what
  each issue implicates, what the root cause is, which prevention move fits. The implicated-file
  reads stay with the runner; only research wide enough to need many sources aggregated goes to
  the researcher agent `config.research_agent` names.

Residual calls this spec settles: the issues are worked in the order triage left them, one at a
time; an issue whose root cause turns out to be another accepted issue is recorded as such
rather than researched twice — `synthesize` folds the pair; an **empty accepted set** is a legal
outcome — the step is a no-op and the run proceeds to `synthesize` with the wins, the open-ended
answers and the goal verdicts alone.

## Return Format

None — the step is runner-performed, so nothing is returned to the harness; the run continues in
the same conversation.
