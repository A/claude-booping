# Take the user's raw feedback

The mined issue list is in context and stays there: mention no finding, read none aloud, ask
nothing beyond the four questions below until all four answers are in. This is the user's raw
take, before any runner framing can anchor it.

## Per plan or once

Only when the working set holds more than one plan, ask up front whether to run the four
questions once across the set or once per plan — the user's call, on how closely related the
plans are. A single-plan run skips this and goes straight to the questions.

## The four questions

Ask each in chat prose, one per message, waiting for each answer before posing the next. Ask
each **verbatim**, in this order, with its `[n/4]` counter. No suggested answers, no
parenthetical, no rephrasing for tone:

1. *"How do you feel about the sprint overall?"*
2. *"How did the code review go?"*
3. *"What stood out as a win — any decision, moment, or move that worked notably well?"*
4. *"Any issues from this sprint you want to bring to the retro?"*

The user answers in their own words, at any length. A declined question is recorded as no
answer and the run moves on — never re-asked, never pressed, never filled in.

A per-plan pass repeats the same four questions under a `### plans/{slug}/index.md` heading per
plan. Reading the answers waits until the mined items are on the table — the triage below.

## Issue triage

Walk every item from the issue list `prepare` withheld, in chat prose, one item per message
with a `[n/total]` counter: cite the source + trigger, then the orchestrator's one-line
interpretation and its proposal, and wait for the user's reply — they may ask back before
deciding. The reply settles the item as one of:

1. **Accept as-is** — keep the orchestrator's framing untouched; carry into `research-issues`.
2. **Dismiss** — drop from the retrospective; not a problem worth carrying forward.
3. **Own take** — record the user's wording into the issue's notes and carry it into
   `research-issues`.

Mark each item with the user's call and their words. Accepted and own-take items are the
**accepted issues** for `research-issues`; dismissed items disappear.

After the issue walkthrough, ask the user explicitly per plan, in chat prose, one plan per
message: *"Was the goal of this plan reached?"* — present the plan's stated goal verbatim from
frontmatter (or the plan's opening paragraph if no `goal:` field) so the user is judging against
what was actually planned. The reply maps to `success` (goal reached), `partial` (partially
reached) or `fail` (not reached).
The user owns this call; the step does not derive it.

## The record — posted in chat

Nothing is written to disk and no plan is touched.