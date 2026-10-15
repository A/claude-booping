# Develop defaults — autonomous run 2026-10-16

Every gate and question this autonomous develop run settled itself.

## D1 — Branch

- Step: develop/provision
- Asked: confirm the sprint branch name (AskUserQuestion gate)
- Default: stay on `feat/specs`, no branch created
- Why: the owner's invocation fixes the worktree branch — "never switch branches"; parts 1 and 2 of this feature shipped on the same branch.

## D2 — Milestone groups

- Step: develop/provision
- Asked: none (internal) — recorded for traceability
- Default: G1 `M01-heading-anchors`+`M02-toc-rail`+`M03-grouped-backlinks`+`M04-adr-option-cards` (13 SP), G2 `M05-search-data`+`M06-search-ui`+`M07-docs-and-fixtures` (9 SP), cap 15 SP
- Why: greedy packing in id order per the provision step; adding M05 to G1 would reach 16 SP.

## D3 — Snapshot baselines vs booping:rule/0013

- Step: develop/wrap-up
- Asked: rule/0013 says never run `just snapshots-accept`
- Default: the owner's standing permission for this feature (2026-10-14), restated in this run's invocation, overrides it: accept only drift every hunk of which the plan describes, listed below; any other drift stops the run.
- Why: explicit owner instruction for this run.

## D4 — One commit per group, not per milestone

- Step: develop/develop-loop
- Asked: one repo commit per milestone
- Default: one conventional commit per briefing group (G1 → `dbff741`)
- Why: the group's milestones share `pages.py`, `style.css`, `src/config.yaml` and the goldens, so per-milestone staging would mean hand-splitting hunks; parts 1 and 2 of this feature committed the same way, conventional format per rule/0022.

## D5 — M01 touched `pages.py` outside its contract

- Step: develop/develop-loop
- Asked: accept a file outside M01's task Files
- Default: accepted
- Why: `_render` must pass `labels` to `render_body`, or Russian pages get an English `aria-label`, failing M01's own DoD (`section_link` in `en` and `ru`); M02–M04 own `pages.py` anyway.

## D6 — M03/M04 golden diffs empty

- Step: develop/develop-loop
- Asked: DoD "goldens rebaselined; diff is Referenced by / ADR pages only"
- Default: satisfied vacuously — no golden fixture carries backlinks on an expected page or an ADR with `## Alternatives`; unit tests (`site_backlinks_test.py`, `site_adr_test.py`) and a runner render of `adr/0001` (chosen card first and open, two closed) cover the behaviour.
- Why: adding fixture cases is scope beyond the contract.

## D7 — G2 commits and worker calls

- Step: develop/develop-loop
- Asked: one commit per milestone; the worker's three open calls
- Default: G2 → `d833567` (feat: M05, M06 and M07's Russian fixture, which share `pages.py`, `style.css`, `src/config.yaml` and the goldens) and `5abf69f` (docs: M07's `documentation/specs.md`). `search.js` at ~190 lines accepted against C7's "~160" — an estimate, not a limit. `search.html` carries its own pre-filled results form beside the header combobox — accepted as C7's "same form" read. An Alternatives table cell with a status no record uses (`rejected`) renders as plain text while its card shows the label — M04 behaviour, left as an open issue, no scope added.
- Why: same reasoning as D4; the rest are within the plan's decisions.

## D8 — Snapshot drift not described by the plan: run stopped before wrap-up

- Step: develop/verify
- Asked: accept `just snapshots` drift under the standing permission
- Default: not accepted; the run stops at `in-progress`, no `done` transition
- Why: the only drift is one new `## Rules` bullet, `booping:rule/0032` (approval asked in prose), in `playbooks/code-review`, `develop` and `groom` `_reports/output.md` — from `specs/rule/0032-approval-asked-in-prose.md`, added in `915383a` before this plan; this plan edits no playbook source and describes no such drift, and the invocation says any other drift stops and is reported.
- Evidence: `just ci` run once by verify — lint, typecheck, pytest (694 + 12) green, `snapshots` red; then `just mdcheck`, `just specs-check`, `just e2e` (572 + 18) run separately, all green. Runner's Final Verification: two builds `diff -r` identical; headless Chromium from `file://` — chosen ADR card first and open, table link opens a closed card, rail marks the section in view, `§` sets the hash, `/` focuses search, `tiers` → `adr/0001`, Down + Enter opens it, `search.html?q=tiers` shows "12 results", no-JS cards, ToC links and form submit hold; swarmlight in `ru` — `даёт`/`дает` same 13 records, `логистик` finds «Логистика»; screenshots at 1280×900 and 390×844, light and dark, no horizontal scroll.
- To finish: the owner accepts the three reports (`just snapshots-accept code-review develop groom`), reruns `just ci`, then resumes `/playbook develop` on this plan for wrap-up.
