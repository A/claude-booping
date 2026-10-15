# Develop defaults

Autonomous develop run, 2026-10-15. Every gate and unclear point the runner settled itself.

## D1 — sprint branch

**Step:** develop/provision
**Asked:** which branch the sprint goes on (gate: user confirms the branch name).
**Default:** reuse `feat/specs`, no branch created or switched.
**Why:** the owner's run instruction: run in the worktree on `feat/specs`, never switch branches.

## D2 — milestone groups

**Step:** develop/provision
**Asked:** how milestones pack into briefings.
**Default:** one group, G1 = M01–M04 (3+3+4+2 = 12 SP, under the 15 SP cap).
**Why:** the greedy packing rule; settled internally, never a user question.

## D3 — commit message format

**Step:** develop/develop-loop
**Asked:** the playbook's `<agent>: <plan title> <message>` vs rule/0022's Conventional Commits.
**Default:** both, as the repo's history already does: `booping-developer: {plan title} feat(scope): …`.
**Why:** satisfies the playbook format and rule/0022 at once; matches commits 66d9a16, 723c59b.

## D4 — snapshot acceptance

**Step:** develop/wrap-up
**Asked:** rule/0013 forbids a run accepting snapshots; the owner's run instruction grants standing permission for this feature when every drifted hunk is a change the plan describes.
**Default:** the owner's explicit instruction governs this run; the plan changes no playbook source (C10), so no drift is expected and nothing should need accepting.
**Why:** the owner's direct, dated permission for this feature.
