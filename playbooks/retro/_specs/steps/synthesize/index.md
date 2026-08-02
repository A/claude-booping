---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# synthesize

## Contract

- **Needs** —
  - the accepted issues in the wording triage settled on, each with its root cause, its
    prevention options and any follow-up the research pass produced
  - the wins the user named and their other open-ended answers, in their own words
  - the per-plan goal verdicts — one `success` / `partial` / `fail` per plan in the working set
  - the sprint's load-bearing stats the verdict line quotes: SP total, commit count and short
    SHAs, planned-to-completed elapsed time, milestone DoD pass rate, Final Verification pass
    rate
  - the retrospective template with its self-review checklist, read from
    `docs/retrospective_template.md` at draft time (lazy-loaded, no longer embedded in the body)
  - the pre-save summary format
- **Value** — the run's one piece of writing and its one decision point. Everything the run has
  gathered — mined items the user kept, the words they kept them in, their wins, the root causes
  and prevention moves, the verdicts — is composed once, against the retrospective's own
  structure: wins, a what-happened / root-cause / impact block per issue, the lesson gaps cited
  by path, and action items split into one-time tasks and standing heuristics. The draft is then
  measured against the template's self-review checklist and every `no` is fixed **before** the
  user sees anything, so what is presented is a finished document rather than a draft with
  caveats. The user reads it as a compact chat summary in the pre-save summary format — enough
  to judge framing and decide, never the full body — and the full draft stays in context,
  unwritten, until they approve. Holding it unwritten is what makes cancel cost nothing: no
  file, no transition, no cleanup.
- **Output files** —
  - none — the draft is held in context and nothing is written here; the file is `save`'s
  - the summary is posted in chat: header, verdict line, what went well, the issue table
    (`#`, `Issue`, `Cause`, `Impact`, `Lesson touched`), the action-item table
    (`#`, `Action`, `Owner`, `Status`) and the takeaways, in that order, under ~40 lines, with
    `_No accepted issues._` / `_No action items._` in place of an empty table. No frontmatter,
    no save path, no commit command, no candidate-lessons section — those are `save`'s and
    `/learn`'s surfaces
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the approved retrospective body,
  held in context section by section, and the approval itself, recorded in the user's own words
  so `save` can clear the exit edge's gate. The approval ask is **prose in the same message as
  the summary**, never an `AskUserQuestion` call — the driving protocol's gate rule.
- **Review gate** —
  - the run's **single review gate**: explicit user approval of the draft, asked for in prose
    from the summary — "save it" counts, silence never does. Approval is what `save` writes on
    and what the exit edge's first gate names
  - a refine request loops in place: adjust framing, wording, or which issues land, then
    re-post the summary whole with what changed marked as changed, and re-ask. The loop is
    unbounded and never advances to `save` on its own
  - a cancel drops the draft and ends the run — nothing written, no transition, the plan left
    at its entry status
- **Delegation** — inline: the composition is the runner's, over material already in its
  context, and the approval conversation is the runner's own. Nothing is delegated.

Four calls this spec settles, so a later run does not re-open them. The **self-review checklist
is the runner's, not the user's** — it is run and its failures fixed before the summary is
posted, never shown as a list of pending items. The **cross-plan verdict sentence** is drafted
here, as the summary's verdict line, and `save` lifts it into `goal_summary:`; the rest of the
frontmatter is assembled by `save`, which owns the plans list, the date and the per-plan
verdicts. A **refine that needs new evidence stays inside this step** — the runner reads the
implicated file itself and re-drafts; the graph has no loopback and the run never returns to
`research-issues`. And an **empty accepted set is a legal draft**: the wins, the open-ended
answers and the goal verdicts carry it, "What went wrong" says plainly that nothing survived
triage, and the summary renders `_No accepted issues._`.

## Example artifact

Posted in chat for the two-plan run triage left behind:

```markdown
Retro summary — playbook-run-state-and-reports

**partial** across the two plans — 31 SP, 14 commits (`a3f12c9`…`7b1e04d`), 4 days
planned-to-completed, milestone DoD 7/8, Final Verification 2/2.

**What went well**

- The state machine was split out of the manifest before a line of it was written, which made
  it reviewable on its own (`4eada8e`).
- `playbook-state` landed with the frontier report first, so resume was testable before any
  writer existed.
- The fixture vault kept the report renders deterministic — no clock, no project dependency.

**Issues**

| # | Issue | Cause | Impact | Lesson touched |
| - | ----- | ----- | ------ | -------------- |
| 1 | migration shipped with the code change | the plan never carried a migration task, so the lesson had nothing to fire on | `just test` broke mid-sprint; one session spent bisecting | `lessons/0007_migrations-before-code.md` |
| 2 | branch convention changed after three commits | the naming was never checked against `CLAUDE.md` before work started | three commits carried forward onto a renamed branch | — |
| 3 | four milestones reviewed in one pass | review was scheduled at sprint level, not per milestone | feedback arrived too late to change M1's shape | — |

**Action items**

| # | Action | Owner | Status |
| - | ------ | ----- | ------ |
| 1 | Add a migration task to the plan template's checklist when a model changes | User | Planned |
| 2 | Check the branch convention against `CLAUDE.md` at develop intake | Claude | Planned |
| 3 | Standing: request review at each milestone DoD, not at sprint end | standing | Planned |

**Takeaways**

- A lesson only fires where the plan gives it a task to attach to — a rule with no slot in the
  plan is a rule that will be missed.
- Review cadence belongs to the milestone, not the sprint: batched review arrives after the
  decisions it would have changed.
```

The full body stays in context, unposted, in the retrospective's own shape — wins, one
`#### {Issue name}` block per accepted issue with **What happened** / **Root cause** /
**Impact**, the lesson gaps cited by path with the rule quoted and the gap named, and the
action-item table typed Task / Heuristic:

```markdown
### What went wrong

#### Migration shipped in the same commit as the model change

**What happened**: M2 landed the model change and its migration together; the failing
`just test` run in session 3 was the first signal.

**Root cause**: the plan carried no migration task, so a lesson that names the right rule had
no point in the milestone to attach to. Pattern: rules without a slot in the plan do not fire.

**Impact**: one session of bisecting, and the migration was written under time pressure at the
end of the milestone rather than ahead of the code.

### Lesson gaps

- `lessons/0007_migrations-before-code.md` — rule was "write the migration before the model
  change", but M2's task list named only the model change, which caused issue 1.
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness. The summary above
is posted in chat and the approval ask follows it as prose, in the same message:

> Save this retrospective? Approving writes it to the plan directory and moves the plan on.
> Tell me what to change instead and I will re-draft, or say cancel and nothing is written.

A refine round re-posts the summary whole and re-asks; the run leaves the step only on the
user's approval, and on a cancel it ends there with nothing written.
