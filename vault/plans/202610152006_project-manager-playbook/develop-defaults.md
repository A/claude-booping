# Develop defaults — 202610152006_project-manager-playbook

Autonomous develop run, 2026-10-15. Every gate and unclear point settled without the owner.

## D1 — develop/provision — branch name

- **Asked:** which branch the sprint goes on (provision's AskUserQuestion gate).
- **Default:** stay on `feat/specs`, no branch created or switched.
- **Why:** the invocation fixes the worktree and branch and forbids switching branches.

## D2 — develop/provision — milestone groups

- **Asked:** briefing groups under the 15 SP cap.
- **Default:** G1 M01–M04 (13 SP), G2 M05–M08 (12 SP).
- **Why:** greedy packing in id order per provision; M05 would push G1 to 17 SP.

## D3 — develop/run — snapshot acceptance vs rule/0013

- **Asked:** rule/0013 forbids a run accepting snapshot baselines.
- **Default:** follow the owner's standing permission for this feature (2026-10-14): accept only when every drifted hunk is one the plan describes; list each accepted report below.
- **Why:** the owner's explicit run instruction is a scoped exception to rule/0013; the plan's Final Verification names the same policy.

## D4 — develop/develop-loop — M04 Verify red by contract ordering

- **Asked:** M04's Verify (`bin/booping render-playbook project-manager`) STOPs because the graph names `work`, whose `work/prompt.md` is M05's file.
- **Default:** not a failed attempt — no `feedback.md`, no blocked edge. M04's work stays uncommitted and `in-progress`; G2's worker builds M05 on top, then M04's DoD is re-checked and M04 committed before M05.
- **Why:** the worker built everything M04 names; adding `work/prompt.md` to M04 would be a scope move between milestones, and a placeholder file would be churn M05 overwrites.

## D5 — develop/develop-loop — M08 file list

- **Asked:** the M08 worker touched `documentation/install.md` (not in 8.2's Files) and documented the items verbs in `documentation/specs_playbook.md` instead of `documentation/specs.md`.
- **Default:** accepted into M08's commit.
- **Why:** M08's DoD requires every page listing the shipped playbooks to name `project-manager`, and `install.md` is one; the items verbs already live in `specs_playbook.md`, so that is the page the contract meant.

## D6 — develop/verify — snapshot drift, acceptance blocked

- **Asked:** `just snapshots` drifts in three reports; accept per D3?
- **Default:** all three hunks judged plan-described, but `just snapshots-accept` was denied by the Claude Code permission classifier, so nothing was accepted and no report was written by hand (rule/0013).
- **Why:** the hunks — `playbooks/project-manager/_reports/output.md` (missing; the new playbook), `playbooks/specs/_reports/output.md` (the `open → done` row of `open_item`), `playbooks/learn/_reports/output.md` (learn's playbook catalogue gaining the `project-manager` entry, a derived listing of the new playbook; not named in the plan's Final Verification) — are each a change the plan makes. Owner to run `just snapshots-accept` (one name per call, or none for all) before the branch ships.

## D7 — develop/wrap-up — run held at in-progress

- **Asked:** verify is green on lint, typecheck, pytest, mdcheck, specs-check, e2e and the Final Verification commands, red only on `just snapshots` (D6); wrap up?
- **Default:** no wrap-up and no `in-progress → done` transition; the plan stays `in-progress`. Docs already landed in M08, so wrap-up has only the transition left.
- **Why:** the `done` gate needs `just ci` green, and the one red check is an acceptance the run was not permitted to make — not a code fix for a worker, and not a blocker for the `fail` edge. After the owner accepts the three reports and `just ci` is green, take `bin/booping playbook-transition develop done --workdir vault/plans/202610152006_project-manager-playbook` and commit the vault.
