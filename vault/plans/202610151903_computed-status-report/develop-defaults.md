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

## D5 — idea status literal

**Step:** develop/develop-loop (M03)
**Asked:** `status.py` holds `IDEA_OPEN = "open"` — a record-status literal in code.
**Default:** accepted as delivered.
**Why:** C4 defines the section by `status: open` and the value is the idea schema's own enum member; M01's and M02's no-literal DoDs cover item and plan statuses only, and both hold.

## D6 — milestone commits

**Step:** develop/develop-loop
**Asked:** one commit per milestone, but the single G1 worker built M01–M03 into shared files (`status.py`, `e2e/cases/status/`) whose intermediate states no longer exist.
**Default:** one repo commit covering M01–M03, one for M04.
**Why:** recreating per-milestone intermediate states would be runner-authored code (rule/0019); the split commit history stays honest about what was built together.

## D7 — worker deviations accepted

**Step:** develop/develop-loop
**Asked:** the worker passed a `StatusContext` (wrapping `Context`) instead of `Context`, and rendered plan tables with `open_items.index_table` instead of `query.as_table`.
**Default:** accepted.
**Why:** `StatusContext` caches the once-per-call reads the architecture asks for; `as_table` appends a `slug` column and renders empty cells blank, breaking the I/O contract's "columns then `path`" and `—` cells.
