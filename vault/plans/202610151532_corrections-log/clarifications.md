# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — which parked part, and split — answered

**Asked:** 2026-10-15 — intake

**Question:** The previous plan parked part 3 (corrections, adr/0026) and part 4 (autonomy modes, adr/0027). Which is groomed now, and together or apart?

**Options:**

- Part 3 alone; part 4 stays parked (default applied)
- Parts 3 + 4 in one plan
- Part 4 first

**Answer:** First option — default applied. Part 3 is first in the request's order and independent; part 4 is a separate config surface plus a manager path (adr/0028 is its own decision) and together they would pass the 35 SP threshold. Part 4 stays a stub in `index.md` `## Out of scope`.
