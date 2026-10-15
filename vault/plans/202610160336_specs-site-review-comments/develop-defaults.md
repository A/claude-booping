# Develop defaults

Autonomous develop run, 2026-10-16. Every gate and question settled without the owner.

## D1 — intake drift

**Default:** proceed without revalidation. Drift 7d40232..fcb38e8 touches `.github/workflows/ci.yml`, `scripts/snapshots.py` and this plan's own files; no milestone names any of them.

## D2 — provision branch

**Default:** `feat/specs`, the current branch, no switch. The invocation fixes the branch ("never switch branches"); the provision gate's branch question is therefore not asked.

## D3 — milestone groups

**Default:** G1 `M01-root-landing`+`M02-export-builder`+`M03-comment-hooks`+`M04-comment-capture` (14 SP), G2 `M05-comment-panels`+`M06-comments-docs` (6 SP), greedy under the 15 SP cap.
