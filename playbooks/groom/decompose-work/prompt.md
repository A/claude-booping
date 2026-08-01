---
summary: Refine the written plan against the sizing thresholds — re-decompose 
  every oversized task and re-sum the milestone and sprint totals, flag a split 
  candidate when the sprint passes the split threshold, and change nothing when 
  the plan is already right-sized.
detached: opus:medium
review_gate: "The user reworks and confirms the refined plan — milestones, tasks,
  estimates and any split candidate — explicit confirmation, silence never counts;
  the gate cannot clear while a task still sits at or over the re-decompose threshold
  or a milestone or sprint total does not sum from its parts; rework touching milestones,
  tasks or estimates comes back for another pass, rework that reopens an architecture
  call sends the run back to design; confirming a split candidate confirms the recommendation
  only — no sibling is created"
inputs:
- what: the written plan — its milestones, its tasks with their DoD and Verify, 
    and the story points per task, per milestone and for the sprint
- from: the attached project
  what: the re-decompose threshold, the split threshold, and the SP scale both 
    are measured on
- from: user
  what: on a loopback into decomposition, the rework and the estimate or 
    milestone it targets
outputs:
- _runs/groom/{slug}/decomposition.md — verdict first (`Refined` or `Skipped` 
  with the counts against both thresholds), then on the refined path what was 
  re-decomposed and the re-summed milestone and sprint totals, plus the split 
  candidate or the one line that none is recommended; written on every path
- "plans/{slug}.md — every oversized task replaced by tasks that stand alone with
  their own DoD and Verify, milestone and sprint totals re-summed and `sp:` set to
  the new sprint total; not opened for writing on the skip path"
- the harness return — the Changed entries annotated with the verdict and its 
  counts, Notes carrying the re-decomposition count, the largest surviving task,
  the re-summed sprint total and the split candidate, and Questions holding only
  the sizing calls that are the user's
reviewed_at: 20260731 20:19
---

{% include "opus-5.md" %}
