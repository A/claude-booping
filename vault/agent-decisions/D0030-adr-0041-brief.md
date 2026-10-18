---
step: "specs/guide"
asked: "ADR 0041 brief \u2014 the ADR scorer reads the specs guide and the tier\u0027s record inventory (accept?)"
decision: "accepted, no review key; score 3/3. Chosen C: guide excerpt + record inventory (values/rules/ADRs existing at write time) + primitives, Opus, tools: ListAgents, one-JSON-line reply, gate route != adr or alt_score \u003c= 1 blocks. Rejected: A/B rubric with or without guide (routes 0 / 2.5 of 6), D Sonnet (misses 3/6), E Opus with repo read (x6 cost, routes 1/6). Touches booping:rule/0036 (scorer step in the Record scenario), rule/0033. Decided alone: new ADR, not an amendment (no earlier scorer ADR exists); A and B merged into one row (table max 4); status accepted although the plan is not developed, since the ADR status set has no built/unbuilt axis and the owner chose C explicitly."
why: "Autonomous run: the Record scenario logs the brief instead of showing it and sets accepted without a review key; the owner\u0027s quote for C is in OI-0035."
state: open
session: "0c3f5735-fd95-5891-a767-80fb60a7872b"
logged_at: "2026-10-19 03:12"
artifact: "adr/0041-adr-scorer-reads-the-guide-and-the-record-inventory.md"
---
