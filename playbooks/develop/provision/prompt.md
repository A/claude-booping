---
summary: Set the sprint up — pick the branch from the plan's task type per the 
  branch conventions, propose a kebab-case name and create it off the repo's 
  current branch only after the user confirms; then settle the milestone groups 
  the briefings will cover, within the configured ceiling, and fire the 
  `ready-for-dev` → `in-progress` transition.
review_gate: "The user confirms the branch name before the branch is created — asked
  through `AskUserQuestion`, never as chat prose; a name the user rewrites is used
  verbatim, and nothing touches git until the answer arrives. The milestone groups
  are internal — settled by the step, reported in its return, never put to the user"
reviewed_at: 20260802 09:58
---

{% include "./base.md" %}
