# Develop defaults — autonomous run 2026-10-16

Every gate and question this autonomous develop run settled itself.

## D1 — Branch

- Step: develop/provision
- Asked: confirm the sprint branch name (AskUserQuestion gate)
- Default: stay on `feat/specs`, no branch created
- Why: the owner's invocation fixes the worktree branch — "never switch branches"; parts 1–3 of this feature shipped on the same branch.

## D2 — Milestone groups

- Step: develop/provision
- Asked: none (internal) — recorded for traceability
- Default: G1 `M01-home-landing-column`+`M02-sidebar-tags`+`M03-record-reading-column` (8 SP), cap 15 SP
- Why: greedy packing in id order per the provision step.

## D3 — Snapshot baselines vs booping:rule/0013

- Step: develop/wrap-up
- Asked: rule/0013 says never run `just snapshots-accept`
- Default: the owner's standing permission for this feature (2026-10-14), restated in this run's invocation and in the plan's Decisions → Snapshots, overrides it: accept only drift every hunk of which the plan describes, listed here; any other drift stops the run.
- Why: explicit owner instruction for this run.

## D4 — One commit for the group, not per milestone

- Step: develop/develop-loop
- Asked: one repo commit per milestone
- Default: one conventional commit for G1 → `feabfe7` (`feat(specs): …`, rule/0022)
- Why: M01–M03 share `pages.py`, `style.css`, `site_pages_test.py` and the `site-*.txtar` goldens, so per-milestone staging would mean hand-splitting hunks; parts 1–3 of this feature committed the same way.

## D5 — M03's grep DoD line read by its intent

- Step: develop/develop-loop
- Asked: M03 DoD "`grep -rn 'class=\"relations\"\|section.relations\|\.relations\b' …` prints nothing"
- Default: satisfied — no `class="relations"`, no `section.relations`, no `.relations` CSS selector remains; the six remaining lines are the `\.relations\b` alternative matching the data attribute (`r.relations` in `record.html.j2`, `site.relations(...)` in `backlinks.py`, `machine.py`, `tests/specs/site_test.py`), which the same contract keeps ("`_relations` keeps its data shape") and which predate this plan.
- Why: the line exists to enforce booping:rule/0007 on the retired CSS class; renaming a data attribute to satisfy a regex is scope beyond the plan.

## D6 — Smaller contract deviations accepted

- Step: develop/develop-loop
- Asked: M02 scope names `style.css`; M03 DoD "relations and no facts still renders `dl.facts`"
- Default: accepted — `style.css` had no `.side` tag `code` rule, so M02 changed nothing there; the no-facts case is carried by the template condition `r.facts or r.relations`, without a dedicated test.
- Why: both DoD outcomes hold; a dedicated test is not a contract item.

## D7 — Visual check found a phone Recently-updated defect

- Step: develop/develop-loop (Final Verification visual check)
- Asked: M01 closed, but at 390px a long Recently-updated title wrapped under its ref and the date sat indented under nothing — C5 missed
- Default: a fresh worker fixed it inside the 760px block (`.recent li a { flex: 1 1 0; min-width: 0 }`), committed as `8640e2d` `fix(specs): …`; M01 stays `done` (terminal state), the fix recorded here
- Why: the plan's own Final Verification requires dates under titles at 390px; CSS only, within M01's scope.
- Evidence: Chromium `--headless=new` at 1300×2200 and 390×2400 of booping home, `claude-booping/adr/0001-specs-tiers.html`, swarmlight (`ru`, temp project `/tmp/specs-site-ru/` per C6) home and `adr/0003-robot-assembly.html`: home lead/callout/Recently updated share the 68ch column, narrower than the scenario grid; callout en «115 need you → · 115 unreviewed · 12 open questions», ru «74 записи ждут тебя → · 64 без ревью · 3 открытых вопроса»; no mark list; relation labels in the facts `dt` column inside the facts box; sidebar tags sans, no zero counts; 390px no horizontal scroll.

## D8 — "≤ 70 characters per body line" read against the prototype

- Step: develop/develop-loop (Final Verification visual check)
- Asked: Final Verification "record body lines hold ≤ 70 characters at 1300px"
- Default: passed on the plan's own decision — body lines run to ~80 proportional characters, because `68ch` is the width of 68 "0" glyphs; the prototype uses the same `.measure{max-width:68ch}`, and M01/C1 forbid redefining the token. No change.
- Why: the criterion's character count miscalibrates `ch`; the prototype and the single-source token win (value/0003). Listed as an open issue for the owner.

## D9 — Snapshots and wrap-up

- Step: develop/verify, develop/wrap-up
- Asked: snapshot drift acceptance; documentation scope
- Default: nothing accepted — `just snapshots` reported no drift inside the one green `just ci`; `documentation/specs.md` updated for the sidebar tags, the callout breakdown, the reading column and relations in the facts list, committed as `9622c19`.
- Why: the plan touched no playbook source; the docs sentences were made untrue by this sprint.
