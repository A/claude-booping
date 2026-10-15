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
