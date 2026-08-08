---
status: awaiting-spec-confirm
---

# gather-feedback

[← index](../../index.md)

## Contract

- **Needs** —
  - the user's own experience of the sprint — the only source this step draws on
  - which plans the run covers and their titles, so a per-plan pass can name the plan it is
    asking about
  - how closely related those plans are, which is the user's call and decides whether the four
    questions run once across the set or once per plan
  - nothing from the mined findings until all four answers are in — then the issue list `prepare`
    withheld (each item's source, trigger and one-line interpretation) and each plan's stated
    goal, verbatim as written, for the triage close
- **Value** — the user's raw take on record before any runner framing can anchor it: the one
  place in the run where the user speaks first and unprompted. The four fixed questions keep
  answers comparable across runs, and the ordering inside the step keeps the anti-anchoring rule
  structural: no mined item is on the table until the open-ended round is closed. Then the
  skill's issue triage runs in the same step — every mined item walked in batches of up to five
  per `AskUserQuestion` call for accept as-is / dismiss / the user's own wording, followed by the
  per-plan goal verdict (`success` / `partial` / `fail`) against the goal presented verbatim.
- **Output files** —
  - none — the answers, the accepted issues in the wording carried forward, and the per-plan
    goal verdicts are held in conversation; nothing is written and no plan is touched
- **Harness return** — none: the step is runner-performed, so it runs in the driving
  conversation and returns no block. What it leaves behind is the four answers in the user's own
  words, recorded verbatim and attributed per plan when the pass ran per plan, plus which of the
  two passes was run; then the accepted issues and the per-plan goal verdicts from the triage
  close.
- **Review gate** —
  - none — the step *is* the elicitation, and the answers are their own confirmation
  - the one rule it enforces instead: no mined finding, no runner reading of one, and no
    question beyond the four is put in front of the user until all four answers are in
- **Delegation** — inline: the runner performs the step itself, in the main context. Nothing
  here is a read worth delegating, and the mined findings must not leave the runner's context.

Decisions this spec settles, which the source prose leaves open:

- **Channel** — one `AskUserQuestion` call per question, asked one at a time, waiting for each
  answer before posing the next. The question text is verbatim: no `"Free-text:"` prefix, no
  `"(Skip if … use Other.)"` parenthetical, no rephrasing for tone.
- **Options** — each call offers a short set of neutral, generic takes on that question plus
  `Other` for free text. The options exist so a quick answer is one click; they are never
  derived from a mined finding, never name a file, a commit or an issue from this sprint, and
  the user's free text wins over any of them when given.
- **Per plan or once** — asked once, up front, only when the working set holds more than one
  plan; a single-plan run skips the question and runs the four directly.
- **A declined question** is recorded as no answer and the run moves on — never re-asked, never
  pressed, never filled in by the runner.

## Example artifact

A two-plan run where the user chose to answer once across the set. The four questions as posed,
in order, and the record they leave in conversation:

```markdown
## Open-ended feedback

Asked once across the working set (`playbook-run-state`, `local-vault-directories`) — the
user's call: the two plans shipped in the same week against the same subsystem.

**How do you feel about the sprint overall?**
> Good but heavy. The run-state work was clean; the vault one dragged because I kept
> re-explaining what "local" meant.

**How did the code review go?**
> Fine. I only pushed back once, on the transition hook ordering.

**What stood out as a win — any decision, moment, or move that worked notably well?**
> Splitting the state machine out of the manifest before writing a line of it. Made the
> whole thing reviewable.

**Any issues from this sprint you want to bring to the retro?**
> The plan said "resolve the vault path" in three places and meant three different things.
> Also I want to talk about how long provisioning took.
```

Answers are kept in the user's words, character-for-character, with no runner gloss attached —
the triage of the mined items follows in the same step, once all four are in. The body pins no
record format beyond posting in chat; the block above is illustrative.

## Return Format

None — the step is runner-performed, so nothing is returned to the harness. The block above is
posted in chat and the run continues in the same conversation.

The one variant worth pinning is a per-plan pass, which repeats the same four questions under a
heading per plan:

```markdown
## Open-ended feedback

Asked per plan — the user's call: the two plans are unrelated.

### `plans/20260728-09-15_playbook-run-state/index.md`

**How do you feel about the sprint overall?**
> …
```
