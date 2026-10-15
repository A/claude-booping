# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — split — answered

**Asked:** 2026-10-15 — intake

**Question:** The request holds four parts (specs playbook, open items, corrections, autonomy modes), together well past the 35 SP threshold. Where is the seam, and which slice is this plan?

**Options:**

- This plan: parts 1 + 2 — the specs playbook and open items. Parked: part 3 corrections, part 4 autonomy modes (default applied)
- This plan: part 1 alone; parts 2–4 parked
- One plan over the threshold

**Answer:** First option — default applied. The playbook's open-items scenario is useless without the open-items store, and part 4 (autonomy) is defined over that scenario, so 1 + 2 is the slice the rest builds on; part 3 (corrections) is independent and parked as its own stub. Each parked part is a stub in `index.md` `## Out of scope`, groomed in its own run.
