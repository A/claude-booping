# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — split — answered

**Asked:** 2026-10-15 — intake

**Question:** The parked stub was estimated at ≈ 25 SP. Split again?

**Options:**

- One plan, as the stub was parked (default applied)
- Split migration 004 from rule-only injection

**Answer:** One plan — default applied, unless the estimate passes the 35 SP threshold at draft. Removing lesson injection before a migration exists strands any vault still holding lessons (its guidance would inject nowhere); shipping the migration while lessons still inject leaves two carriers. The two halves ship together or the intermediate state is broken.

## C2 — the owner's `<home_dir>` — answered

**Asked:** 2026-10-15 — intake

**Question:** Migration 004 converts `{home_dir}/_lessons/` too. Is it run on this machine's `<home_dir>`?

**Answer:** No — the request forbids it. The global half is shipped and exercised on fixtures only. On this machine `{home_dir}/_lessons/` does not exist (checked 2026-10-15) and the global tier already holds anton:rule/0001–0004, so a later `/playbook migrate` from another vault finds nothing global to convert.
