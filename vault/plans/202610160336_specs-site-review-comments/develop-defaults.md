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

## D6 — Final Verification browser check

**Default:** passed, judged by the runner. `/tmp/cmt-check.py` against `bin/booping specs site --out /tmp/specs-site-booping`: a span comment under `## Decision` (selection → floating button) and a section-button comment on `## Alternatives`, both saved through the compose dialog; the record panel is a 448px right sheet at 1300 and a bottom sheet at 390 with 44px buttons and no horizontal scroll; `comments.html` lists both; the copied block matches C2 exactly; `claude-booping/index.html` shows callout, scenario cards and Recently updated, no marks. The callout's `need you → · N unreviewed` shape is the Overview's own, unchanged since before this plan. `just snapshots` is clean, so nothing was accepted.

## D7 — agent ids kept here, not in `agents:` frontmatter

**Default:** `frontmatter-update` takes scalar `key=val` only, so the run's agent ids are listed here instead of an `agents:` mapping: develop-loop G1 `a749da3da4c2a37db`, develop-loop G2 `ac2f9b63b297b8c4c`, verify `a249547f007720432`.

## D8 — wrap-up documentation

**Default:** no closing commit. M06 already documented the feature in `documentation/specs.md` (`d7162a5`); the plan states no CLAUDE.md impact, and the sprint invalidated nothing else.
