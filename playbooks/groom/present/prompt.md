---
name: present
title: Present
summary: "Owns the present-and-iterate craft rule and the explicit-approval gate; fires the approval move per the Plan Transitions table."
agent: null
review_gate: "Ready for development, or want changes? Approval must be explicit — 'looks good' is enough, silence is not. On a change request: re-enter draft for wording, scope, milestone, or estimate changes, or re-enter design when the change needs re-research or re-design (move the plan back per the Plan Transitions table first); then present again."
---
## Present

Show the user, in this order:

1. **Approach summary** — the agreed design in a few lines.
2. **Milestones** — one line each, with per-milestone SP.
3. **SP total** for the sprint, and any split proposal that came out of drafting.
4. **Plan file path**.

Then ask: *"Ready for development, or want changes?"*

- **Explicit approval** → fire the approval move from the Plan Transitions table with `booping transition`, then re-read the plan frontmatter to confirm the new status.
- **Change request** → do not transition on approval. Route it: wording, scope, milestone, or estimate edits go back to `draft`; anything needing re-research or re-design goes back to `design`, moving the plan back per the Plan Transitions table first. Iterate and present again.
- **User shelves the work** → take the cancel move from the Plan Transitions table.

## Output

The plan file path and the status the plan ends in.
