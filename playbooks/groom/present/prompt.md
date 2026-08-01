---
summary: Assemble the approval summary — approach, milestones, SP totals, plan 
  path and every check outcome; recommend a split when the total passes the 
  threshold, offer a plan branch on a repo-local vault, and carry the approval.
agent: sonnet:medium
review_gate: "Explicit user approval — \"looks good\" counts, silence never does;
  on that word the run moves to `ready-for-dev`. A change request loops the run back
  to the status that owns what it touches — milestones, tasks or estimates reopen
  the refinement pass, architecture or scope reopens the design — and present never
  absorbs a change itself. A recommended split is acknowledged, not required: the
  user may approve the plan whole and park no siblings"
inputs:
- what: the drafted plan — its approach, its milestones, the per-milestone and 
    sprint SP totals, and the path it lives at
- what: the split threshold, and the split candidate the refinement pass flagged
    — its sibling shape and rough sizes — or the note that nothing was flagged
- what: the cross-review findings with the deferrals recorded against them, or 
    the note that no cross-review agent is configured
- what: the reference-verification results — what was checked, what was 
    corrected, what stayed unresolved
- from: runner
  what: whether the vault lives inside the repository being planned, and the 
    project's branch prefix for the plan's type
- from: user
  what: on a pass that follows an earlier presentation, the user's reply to it —
    a change request, an approval, or neither — and what changed in the plan 
    since that summary
outputs:
- "_runs/groom/{slug}/handoff.md — the approval summary: Approach, Milestones, Totals,
  Plan, Checks, Split recommendation (over threshold only), Branch (repo-local vault
  only), Next; no frontmatter authored, rewritten in place on a later pass"
- the sprint SP total against the split threshold and one line per check 
  outcome, in the harness return
- on a repo-local vault, the proposed `git switch -c` command for the driver to 
  run — never run by the step
- the approval question, plus the branch offer on a repo-local vault; empty once
  the user has approved or a change request is handed back
reviewed_at: 20260731 20:19
---

{% include "sonnet-5.md" %}
