# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — what is left, and what "a manager path" means — answered

**Asked:** 2026-10-15 — intake

**Question:** Parts 1–3 are done (plans 202610151409 and 202610151532); part 4 is the only parked stub. Part 4 says "a manager path honours it", and adr/0028 decides a core `project-manager` playbook. Does this plan build project-manager?

**Options:**

- No — the manager path here is the specs playbook's open-items scenario taking items through groom and develop (adr/0027's own confirmation line); project-manager stays its own request (default applied)
- Yes — build project-manager in this plan

**Answer:** First option — default applied. adr/0028 is a separate, high-complexity decision (item store, computed status, run registry, budget gates) not named in this request's parts; adr/0027's confirmation names only the specs playbook. project-manager will read the same config key when it is groomed.
