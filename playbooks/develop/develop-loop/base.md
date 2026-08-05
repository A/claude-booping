# Run the sprint, group by group

Milestone groups run **sequentially** — never two workers on one sprint branch, and never edit
application code yourself. Don't use git worktrees.

Provision already fired the `ready-for-dev` → `in-progress` edge. On a resume that still finds the
plan at `ready-for-dev`, take that edge before the first delegation; otherwise never touch it.

For each confirmed milestone group, in order:

1. Open one tracking task for the group.
2. Compose **one** briefing covering every milestone in the group: per-milestone request, related
   files, DoD and Verify, plus the project conventions and the plan's scope boundary. Briefings
   carry no lesson paths — the worker gets its lesson context from its own extension file.
3. Delegate the briefing to the worker agent named in [Available Agents](#available-agents) —
   always delegate, even for a one-line change. 
4. Do not continue next milestone in the same agent by resurrecting it with ID. Always start a fresh agent with empty context.
5. When the worker reports done, for **each milestone** in the group:
   - Verify the output against the milestone's DoD and the resulting diff.
   - Run the milestone's plan-authored `Verify` command — the project's own guardrails all wait for
     `verify` at sprint end.
   - Flip each completed task's DoD checkboxes in the plan: `- [ ]` → `- [x]`.
   - Flip each task row in the milestone's status table: `pending` → `done`.
   - Flip the milestone status to `done`.
   - Commit in the attached repo, one commit per milestone, message format
     `{{ config.core.develop_playbook.git.commit_message }}`.
5. Commit the plan in the vault with `booping vault-commit in-progress {plan-path}`.
6. Report group completion to the user with a one-paragraph summary (what shipped, anything
   deferred) before starting the next group.

Plan edits here are bookkeeping only: no new milestones, no rewritten tasks, and never `status:`,
which the run machine owns.

## When a milestone does not close

A failing `Verify` or a wrong diff goes back to the worker as a fix briefing, and the attempt is
recorded under the milestone in the plan:

**Blocked (1/2)**: `{verify command}` failed on {what failed}; re-briefed the worker to {fix}.

After two recorded attempts on the same issue the blocker is unrecoverable: ask the user to approve
the abort, then take the `in-progress` → `fail` edge. No scope additions and no runner-authored fix
at any point.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/index.md — {groups closed, milestones flipped}
- repo commits: {one line per milestone commit}

## Notes:

- {per group: what shipped, anything deferred}
- {the Verify verdict per milestone, and any fix attempts spent}
```
