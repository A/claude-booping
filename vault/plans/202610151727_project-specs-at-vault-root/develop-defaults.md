# Defaults

Autonomous run (owner unavailable). File name `develop-defaults.md` per the owner's run instruction and the plan's Final Verification, in the `docs/defaults.md` shape.

## D1 — develop/intake — 2026-10-15 17:46

**Asked:** Plan `commit:` 0a3547f differs from HEAD e609bad — revalidate the plan?

**Default:** No revalidation; proceed

**Why:** the three commits since touch only this plan's own files; no plan-named code changed

**Artifact:** [index.md](index.md)

## D2 — develop/provision — 2026-10-15 17:46

**Asked:** Confirm the sprint branch name

**Default:** reuse `feat/specs` (current branch, 195 commits ahead of `master`), no new branch

**Why:** the owner's run instruction fixes the worktree's branch `feat/specs` and forbids switching branches

**Artifact:** [index.md](index.md)

## D3 — develop (whole run) — 2026-10-15 17:46

**Asked:** rule/0013 (never run `just snapshots-accept`) vs the owner's run instruction permitting it for described drift

**Default:** follow the owner's instruction: accept only drift whose every hunk the plan describes (M01 migrate survey row, M08 docs playbook record paths, M09 setup example line), each accepted report listed here; any other drift stops the run

**Why:** owner's standing permission of 2026-10-14 for this feature, restated in the invocation; the plan records the same departure (C12)

**Artifact:** [index.md](index.md)

## D4 — develop/provision — 2026-10-15 17:46

**Asked:** Milestone groups (cap 15 SP)

**Default:** G1 M01–M05 (15 SP), G2 M06–M09 (14 SP)

**Why:** greedy packing in id order per the step

**Artifact:** [index.md](index.md)

## D5 — develop/develop-loop — 2026-10-15 18:05

**Asked:** `just snapshots` after G1 drifts in `playbooks/migrate/_reports/output.md` (the `survey` row, M01) and `playbooks/specs/_reports/output.md` (tiers line `project — specs` → `project — .`, M02's default rendered under the hermetic fixture) — accept?

**Default:** both hunks judged plan-described (M01 summary; M02 "null path → the vault itself"), the specs report although the plan's Final Verification list did not foresee it. `just snapshots-accept` was then **denied by the harness permission classifier**; not worked around — both reports left unaccepted for the owner, so `just snapshots` (and `just ci`) stays red on them

**Why:** owner's snapshot policy for this run; a harness block is not something a run bypasses

**Artifact:** [index.md](index.md)
