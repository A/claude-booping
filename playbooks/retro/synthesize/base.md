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
