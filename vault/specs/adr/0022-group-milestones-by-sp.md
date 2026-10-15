---
type: adr
title: Develop groups milestones per worker by story points, not by count
summary: Proposed — replace max_milestones_per_agent with a max_sp cap of 15, packing milestones greedily within one wave, and make sp ≥ 5 a hard groom gate.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: proposed
values: [value/0012, value/0002]
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/20260821-milestone-grouping-by-sp.md
---

## Context

Develop briefs one worker per group of milestones, capped by
`core.sprint.max_milestones_per_agent: 2`. A worker's real limit is its session
context; milestone count does not track it, story points roughly do and are the only
size signal already in the plan. Six benchmark runs of one 3-milestone, 8-SP plan on
a local 27B model: one delegation for the whole plan against one per milestone gave
the same code score (95.9 against 94.5), 16% less time, 36% fewer output tokens and
far less variance. Ten historical plans had a median of about 23 SP over 5–7
milestones; 13 of 59 milestones had sp ≥ 5, and groom ignored the redecompose
threshold in 5 of 10 plans.

## Decision

Proposed, decided in chat and not yet implemented: `core.sprint.max_sp: 15`
replaces `max_milestones_per_agent`. Milestones pack greedily and contiguously in
graph order while the group's `sum(sp) <= max_sp`, only within one topological
wave; a single milestone is always a valid group and is never split. Grouping
changes only the briefing; the runner still validates, commits and transitions per
milestone. Groom gets a hard gate: a milestone with `sp >= redecompose_threshold`
(5) does not leave grooming.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [SP cap of 15](#sp-cap-of-15) | proposed | low | high | Halves delegations on the median plan |
| [Count cap of two](#count-cap-of-two) | rejected | low | high | Cuts well below the measured floor |
| [A 10 to 15 band with rounding](#a-10-to-15-band-with-rounding) | rejected | low | high | Same group counts as the plain cap |

### SP cap of 15

One knob; greedy packing within a wave.

- **Pros:** simulation roughly halves the delegations on the median plan; a warm
  context avoids re-briefing and repeated repo reads.
- **Cons:** quality is measured only at 8 SP per delegation (n=3 against n=3, one
  plan, one task type); 15 is a ×2 extrapolation; SP measures human effort, not
  tokens.
- **Complexity:** low.
- **Reversibility:** high — the knob is cheap to lower.

### Count cap of two

The current rule: up to two milestones per briefing.

- **Pros:** not named in the source.
- **Cons:** unrelated to context use; more delegations than needed.
- **Complexity:** low.
- **Reversibility:** high.

### A 10 to 15 band with rounding

A cap range rather than one number.

- **Pros:** not named in the source.
- **Cons:** over the historical plans it gave the same group counts as plain
  `max_sp: 15`, so the simpler knob won.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Not implemented yet: `src/config.yaml` and develop's `provision` step still use
  `max_milestones_per_agent: 2`, and the groom gate is missing. The owner confirmed
  on 2026-10-14 that it must be done; a backlog task tracks it.
- Planned calibration: re-groom a 31-SP plan with sp-8 milestones and run it as a
  second benchmark in two groups of about 15.
