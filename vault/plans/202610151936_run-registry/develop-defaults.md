# Develop defaults — 202610151936_run-registry

Autonomous develop run, 2026-10-15. Every gate or question the run settled itself.

- **D1 — provision / branch name.** Asked: which sprint branch. Default: stay on `feat/specs`, no branch created or switched. Why: the owner's invocation pins the worktree branch (`never switch branches`).
- **D2 — provision / milestone groups.** Default: one group G1 = M01+M02+M03+M04, 12 SP under the 15 SP cap. Why: greedy packing per the step; not a user question.
- **D3 — intake / drift.** Default: proceed without revalidation. Why: `fcfe362..8547dd7` touches only this plan's own vault files (groom commits), no code file a task names.
- **D4 — run / rule/0013 vs owner snapshot policy.** Default: the owner's standing permission for this feature (2026-10-14) overrides rule/0013 for this run — `just snapshots-accept` only when every drifted hunk is a change the plan describes, each accepted report listed here. Why: explicit owner instruction in the invocation.
- **D5 — develop-loop / per-milestone commits.** Default: M01's commit carries `runs.py` and `commands/run.py` whole, M02's code included; M02's commit holds its tests and ack cases. Why: one briefing built both milestones into the same two modules; splitting hunks by hand risks an uncompilable intermediate commit.
