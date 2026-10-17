---
type: adr
title: Develop groups milestones per worker by story points, not by count
summary: Develop packs milestones per worker greedily within one wave under a max_sp cap of 15 instead of max_milestones_per_agent, and sp ≥ 5 is a hard groom gate.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
values: [value/0012, value/0002]
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/20260821-milestone-grouping-by-sp.md
---

## Context

Develop briefs one worker per group of milestones, capped by
`core.sprint.max_milestones_per_agent: 2`. A worker's real limit is its session
context; milestone count does not track it, story points roughly do and are the only
size signal already in the plan. Every clean comparison in `booping-benchmarks`
(one fixed 3-milestone, 8-SP refactoring plan, local Qwen3.8 27B, 2026-08..09) has one
delegation for the whole plan match or beat one delegation per milestone, in less time,
with fewer output tokens and a tighter spread:

| Date | Model | Whole plan (n) | Per milestone (n) | Output tokens | Report |
|---|---|---|---|---|---|
| 08-21 | 27B Q8 | 95.9 (3), spread 0.4 | ≈95.6 (8), spread 6.5 | 36–47k vs 55–80k | `reports/20260821-014756-qwen3-8-27b-q8.md` |
| 08-23 / 09-03 | 27B FP8 | 97.0 (3) | 91.9 (3) | 54–96k vs 74–76k | `reports/20260823-002017-…`, `reports/20260903-044651-…` |
| 09-13 | 27B, new template | 96.3 (1) | 91.1 (3) | 58k vs 75–88k | `reports/20260913-114521-qwen3-8-27b.md` |
| 09-16..17 | 27B | 93.8–97.2 (6) | 89.9–92.5 (09-12/13) | — | `reports/20260916-232343-qwen3-8-27b.md` |

The 09-03 against 09-12 pair changed the chat template together with the delegation
shape; the 09-13 control isolates the delegation and keeps the 5-point gap. Ten historical plans had a median of about 23 SP over 5–7
milestones; 13 of 59 milestones had sp ≥ 5, and groom ignored the redecompose
threshold in 5 of 10 plans.

## Decision

`core.sprint.max_sp: 15`
replaces `max_milestones_per_agent`. Milestones pack greedily and contiguously in
graph order while the group's `sum(sp) <= max_sp`, only within one topological
wave; a single milestone is always a valid group and is never split. Grouping
changes only the briefing; the runner still validates, commits and transitions per
milestone. Groom gets a hard gate: a milestone with `sp >= redecompose_threshold`
(5) does not leave grooming.

The cap measures review burden, not how hard the work is for the agent: it bounds how
much one briefing hands the human to check at once (owner, 2026-10-16), so it is tuned to
the reviewer, not to the model.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [SP cap of 15](#sp-cap-of-15) | accepted | low | high | Halves delegations on the median plan |
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

- `core.sprint.max_sp` (default 15) replaced `max_milestones_per_agent`, and groom keeps
  a milestone at or over `redecompose_threshold` from leaving drafting (BL-0015).
- Planned calibration: re-groom a 31-SP plan with sp-8 milestones and run it as a
  second benchmark in two groups of about 15.
