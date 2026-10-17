# Develop defaults — 202610160504_specs-site-mobile-filters

Autonomous run (owner unavailable, invocation 2026-10-16). Every gate and question the run settled itself.

## D1 — provision: branch

- Asked: branch name confirmation (`AskUserQuestion`).
- Default: reuse `feat/specs`, the branch the invocation names; no branch created or switched.
- Why: the invocation forbids switching branches; the step reuses an explicitly given branch.

## D2 — provision: milestone groups

- Asked: none (internal), recorded for the record.
- Default: three groups, one per milestone (G1 M01, G2 M02, G3 M03), though greedy packing under the 15 SP cap would make one group of 11 SP.
- Why: all three milestones edit `style.css` and the `site-*.txtar` goldens; one uncommitted tree over the three could not be staged into one commit per milestone by path. All three milestones were moved to `in-progress` together before this was settled.

## D3 — rule/0013 vs. snapshot policy

- Asked: rule/0013 says a run never runs `just snapshots-accept`.
- Default: follow the owner's standing permission for this feature (2026-10-14, restated in the invocation and in the plan's Decisions → Snapshots): accept only drift the plan describes, each report listed below; any other drift stops the run.
- Why: explicit owner override, already recorded as a departure in the plan.

## D4 — M01: golden rebaseline was a no-op

- Asked: DoD says `site-*.txtar` rebaselined with the diff limited to the `style.css` and `site.js` bodies.
- Default: box ticked with an empty golden diff — `just e2e -k site --txtar-update` changed nothing, since the goldens do not hold the asset bodies.
- Why: the DoD bounds the golden diff; an empty diff is inside that bound.
