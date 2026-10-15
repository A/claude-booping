# Develop defaults

Autonomous develop run, 2026-10-16. Every gate and question settled without the owner.

## D1 — intake drift

**Default:** proceed without revalidation. Drift 7d40232..fcb38e8 touches `.github/workflows/ci.yml`, `scripts/snapshots.py` and this plan's own files; no milestone names any of them.

## D2 — provision branch

**Default:** `feat/specs`, the current branch, no switch. The invocation fixes the branch ("never switch branches"); the provision gate's branch question is therefore not asked.

## D3 — milestone groups

**Default:** G1 `M01-root-landing`+`M02-export-builder`+`M03-comment-hooks`+`M04-comment-capture` (14 SP), G2 `M05-comment-panels`+`M06-comments-docs` (6 SP), greedy under the 15 SP cap.

## D4 — one repo commit for G1

**Default:** M01–M04 landed in one commit (`6fc1fb1`) instead of one per milestone. Their changes share files (`pages.py`, `src/config.yaml`, `comments.js`, `style.css`, `site_pages_test.py`) and the run cannot stage hunks interactively; splitting by file would have put later milestones' hunks into earlier commits.

## D5 — orphaned `.types` CSS and `marks` / `none` labels left in place

**Default:** not removed. M01 retired `ul.types`, so the `.types` rules in `style.css` and the `marks` / `none` labels have no reader; the plan names only `types_list` and `records` for removal, and the run makes no scope additions. Open issue for code review or a follow-up.
