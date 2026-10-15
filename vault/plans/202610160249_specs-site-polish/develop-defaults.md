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
