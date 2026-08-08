---
summary: >-
  Draft the retrospective against the retrospective template — wins, per-issue
  what-happened / root-cause / impact, lesson gaps, and action items split into
  one-time tasks and standing heuristics — run the template's self-review
  checklist and fix every `no`, then show the user a chat summary in the
  pre-save summary format while holding the full draft in context, unwritten.
review_gate: >-
  The run's single review gate — explicit user approval of the draft, asked for
  in prose in the same message as the summary, never via `AskUserQuestion`.
  "Save it" counts, silence never does; the approval is what `save` writes on
  and what the exit edge's first gate names. A refine request loops in place —
  adjust framing, wording or which issues land, re-post the summary whole with
  what changed marked as changed, and re-ask; the loop is unbounded, a refine
  needing new evidence stays in this step, and the run never advances to `save`
  on its own. A cancel drops the draft and ends the run: nothing written, no
  transition, the plan left at its entry status.
---

{% include "./base.md" %}
