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