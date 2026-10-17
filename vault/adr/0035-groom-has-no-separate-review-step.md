---
type: adr
title: Groom has no separate review step
summary: A fresh Opus review lifts plan quality but adds about 10 minutes a plan (4–5 at best); the one-pass draft already meets the goal, so groom has no review step.
created_by: owner
created_at: 2026-10-17
updated_at: 2026-10-17
status: accepted
supersedes: [adr/0016]
values: [value/0012, value/0008, value/0010]
issues: []
sources: [vault/reference/0007-groom-benchmark-2026-10.md]
---

## Context

The groom refactor set out to make grooming faster and better at once (idea/0003). The one-pass draft
(adr/0030) already did it: about 8 minutes a plan against 13–23 for the old groom, at equal or better
judged quality. Groom keeps a config-gated cross-review step (adr/0016); on the owner's machine it ran
codex. A benchmark then measured review as a separate step (`booping-benchmarks` `groom/xreview`,
2026-10-17): 36 plans (V2, V3, V3a, V5 on s1, m2, c1), each reviewed, folded in by Opus and judged
against a V3a reference by codex and a neutral `claude -p`, on readiness and on how well the plan
challenges the request; the codex judge scored 22 of 36 plans before its usage limit.

| Review | Readiness effect (codex / claude-p) | Challenge effect (codex / claude-p) | Verdict |
|---|---|---|---|
| Fresh Opus, plain "double-check" prompt | +1.77 / +1.22 | +2.27 / +1.42 | helps on challenge |
| Fresh Opus, cross-review prompt | +1.82 / +0.89 | +1.77 / +0.92 | no measurable effect |
| codex, cross-review prompt | +0.91 / +0.44 | +1.17 / +0.03 | no measurable effect |
| Gemini, cross-review prompt (8 plans) | +0.50 / +0.38 | +0.62 / −0.38 | no measurable effect |

Head to head on nine pairs, V3a plus a fresh Opus double-check beat V3 (self-review in the drafting
session) by +1.00 / +0.56 on readiness and +1.78 / +1.67 on challenge, and brought incident coverage
from V3a's 71% to V3's 79%. No reviewer found the hidden defect of task m2 (a 60 s gateway cap) on any
plan whose draft missed it. The review and its fold-in added 10.4 minutes a plan on average (review
4.6, fold-in 4.6 in a separate session); folding in inside the drafting session and reviewing without
reading the code could bring it to about 4–5 minutes, unmeasured.

## Criteria

- Groom stays fast: the point of the refactor was less time and better quality together.
- A step earns its time by what it changes in the plan the owner then executes.

## Decision

Groom runs no separate review step, and the cross-review step leaves the graph together with its `cross-reviewing` status and the `core.groom_playbook.cross_review_agent` key. The one-pass draft is the plan; its only check after drafting is the deterministic mdcheck milestone check (adr/0030, adr/0038). The measured gain of a fresh review is real but not worth 10 minutes a plan, and not worth 4–5 either: the refactor already reached its goal of shorter time at equal or better quality, and adding the review back would trade most of the time saved for a gain inside the plans' own spread (owner, 2026-10-17). The owner asked for no separate step; keeping the step behind its config key was a drafting addition, dropped on 2026-10-17 (owner).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [No review step](#no-review-step) | accepted | low | high | Keeps the time the refactor won |
| [Fresh Opus double-check](#fresh-opus-double-check) | rejected | low | high | Better plans, about 10 minutes more each |
| [Optimised fresh review](#optimised-fresh-review) | rejected | medium | high | 4–5 minutes, still too much for the gain |
| [Codex cross-review](#codex-cross-review) | rejected | low | high | No measurable effect |

### No review step

The decision above.

- **Pros:** about 8 minutes a plan; nothing to configure.
- **Cons:** forgoes about +1 point of readiness and +1.5 of challenge measured on 36 plans.
- **Complexity:** low.
- **Reversibility:** high — one config key turns a review back on.

### Fresh Opus double-check

A separate Opus session gets the request, the plan and the code, and lists what is wrong, missing or
will break; the drafting session folds the findings in.

- **Pros:** the only arm with a measured gain; challenges the request better than any other.
- **Cons:** 10.4 minutes a plan as measured; misses what the draft's research missed (m2's cap).
- **Complexity:** low.
- **Reversibility:** high.

### Optimised fresh review

The same review without reading the code, folded in by edits inside the drafting session.

- **Pros:** an estimated 4–5 minutes.
- **Cons:** unmeasured; part of the findings may come from the code; still half the draft's time.
- **Complexity:** medium.
- **Reversibility:** high.

### Codex cross-review

The step as it ran before the benchmark.

- **Pros:** fast (about 4 minutes with fold-in).
- **Cons:** no measurable effect on either metric; many CRITICAL findings to dispose of.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The cross-review step, the `cross-reviewing` status, its edges and `cross_review_agent` are removed from groom; the owner's machine config drops the key.
- adr/0016 is superseded by this record.
- adr/0030 stays: the one-pass draft without self-review is the groom.
