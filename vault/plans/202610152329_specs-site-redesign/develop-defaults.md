# Develop defaults

## D1 — develop/provision — 2026-10-15

**Asked:** Sprint branch name confirmation

**Default:** Stay on `feat/specs`, no new branch

**Why:** Owner's run prompt fixes the branch: run in the feat/specs worktree, never switch branches

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15

**Asked:** Rule booping rule/0013 (snapshots accepted by user only) vs the run prompt's snapshot policy

**Default:** Follow the owner's standing permission for this feature (2026-10-14): `just snapshots-accept` only when every drifted hunk is a change the plan describes, each accepted report listed here; any other drift stops the run

**Why:** The owner's explicit instruction for this run narrows the rule; the plan's Decisions repeat the same permission

**Artifact:** [index.md](index.md)
