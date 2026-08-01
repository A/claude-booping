---
summary: Assemble the approval summary — approach, milestones, SP totals, plan 
  path and every check outcome; recommend a split when the total passes the 
  threshold, offer a plan branch on a repo-local vault, and carry the approval.
review_gate: "The run's only review gate — the summary and the full plan are approved
  together, and the plan reaches `/develop` through this gate and no other. Explicit
  user approval: \"looks good\" counts, silence never does; on that word the run moves
  to `ready-for-dev`. A change request loops the run back to the status that owns what
  it touches — milestones, tasks or estimates to `decomposing`, architecture or scope
  to `designing` — and present never absorbs a change itself. A recommended split is
  acknowledged, not required: the user may approve the plan whole and park no siblings"
reviewed_at: 20260731 20:19
---

{% include "sonnet-5.md" %}
