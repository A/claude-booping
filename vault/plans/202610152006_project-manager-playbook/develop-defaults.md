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
