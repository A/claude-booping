---
type: adr
title: The ADR scorer reads the specs guide and the tier's record inventory
summary: The adr-scorer gets the specs guide excerpt, the tier's value/rule/ADR 
  inventory and the project's primitives, on Opus without tools, and answers 
  route, overlaps, alt_score and missing.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
values: [value/0010, value/0012, value/0002]
rules: [rule/0033]
sources: [vault/open-items/OI-0035.md, 
    vault/plans/202610190307_adr-scorer-v3/index.md]
review: accepted
review_evidence: «С, очевидно, надо брать» … «Ну все газ, вроде ок все» — 
  2026-10-19, chat
---

## Context

The specs playbook scores every drafted ADR with the `booping:adr-scorer` agent before its brief ([booping:rule/0036](../../specs/rule/0036-adr-accepted-after-a-brief.md)). Today the agent gets the ADR text and the rubric only, and scores the alternatives 0–3. On 2026-10-18 the owner deleted six ADRs as not-ADRs — records that were a rule, a value or nothing — which the scorer had not flagged: judging the text alone, it cannot tell that a record belongs to another type or restates a record that exists, and it cannot name a cheap option that is an existing primitive it has never seen.

The options were measured on 12 labelled ADRs, the 6 the owner deleted and 6 kept (private note, not published). Routing counts are the deleted ADRs sent to the type they fit, out of 6.

Cheap options: building nothing is option A; prose is option B, the guide's own tests pasted into the prompt; extending an existing primitive is the inventory, the `ref — title: summary` lines `booping specs ls` already prints.

## Criteria

- Routes a not-ADR to the type it fits, or to none.
- Names the cheap option an ADR left out.
- Cost per ADR, in tokens and in time.

## Decision

Option C (owner, 2026-10-19: "С, очевидно, надо брать"). The scorer's prompt carries, beside the ADR text and the rubric:

1. the specs guide excerpt — Types and When a record is worth writing;
2. the tier's record inventory — one `ref — title: summary` line per value, rule and ADR, holding only the records that exist when the ADR is written;
3. the project's primitives.

It runs on Opus and keeps `tools: ListAgents` — it reads nothing beyond its prompt; its body stops saying it has no tools. It replies with one JSON line: `route`, `route_why`, `overlaps` (at most 3 bare refs), `alt_score` (0–3), `missing` (at most 3, each naming the existing primitive or record).

The gate: route ≠ `adr` or `alt_score` ≤ 1 → block; otherwise pass, with `missing` in the brief as "Не взвешено:" and `overlaps` in "Задевает:". The list, not the score, is the signal: with one cheap option cut from a good ADR, the cut option was named in `missing` 4 times of 4 and the score dropped once of 4.

Cost per ADR is about 7K tokens in and 650 out on Opus.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Guide and record inventory on Opus](#guide-and-record-inventory-on-opus) | accepted | medium | high | Routes 4.5/6 and catches 6/6 at about 7K tokens an ADR |
| [The rubric, with or without the guide excerpt](#the-rubric-with-or-without-the-guide-excerpt) | rejected | low | high | Text alone cannot route; the guide alone routes 2.5/6 |
| [Guide and inventory on Sonnet](#guide-and-inventory-on-sonnet) | rejected | medium | high | Cheaper, but misses 3/6 |
| [Opus with read access to the repo](#opus-with-read-access-to-the-repo) | rejected | low | high | Costs about ×6 and routes 1/6 |

### Guide and record inventory on Opus

Option C: the decision above.

- **Pros:** routes 4.5/6 and catches all 6 deleted ADRs; names a cut cheap option 4/4; the inventory comes from a command that exists; the agent still reads nothing beyond its prompt.
- **Cons:** the prompt grows to about 7K tokens; the inventory must be rendered at the ADR's creation time, filtered by `created_at`, or later records leak in; the routing calls on the deleted set are still 4.5 of 6.
- **Complexity:** medium.
- **Reversibility:** high.

### The rubric, with or without the guide excerpt

Option A is today's scorer, the ADR text and the rubric: building nothing. Option B adds the guide's Types and When a record is worth writing, prose only.

- **Pros:** A costs nothing more; B is a pasted excerpt, no new input to render.
- **Cons:** A cannot route at all; B routes 2.5/6; neither knows which records and primitives exist, so neither can name an overlap or a missing primitive.
- **Complexity:** low.
- **Reversibility:** high.

### Guide and inventory on Sonnet

Option D: option C's input on Sonnet.

- **Pros:** cheaper and faster per ADR than Opus.
- **Cons:** misses 3 of the 6 deleted ADRs.
- **Complexity:** medium.
- **Reversibility:** high.

### Opus with read access to the repo

Option E: Opus finds the records and primitives itself with Read, Glob and Grep.

- **Pros:** no input to render; it sees whatever it reads.
- **Cons:** costs about ×6 of option C and routes 1/6; opens the agent's tool list, which today reads nothing beyond its prompt.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The specs playbook's Record scenario renders the inventory and the primitives into the scorer prompt, gates on `route` and `alt_score`, and adds "Не взвешено:" to the brief.
- The `adr-scorer` agent body and the rubric's output contract change to the JSON line; its eval fixtures stay booping-only, since the repo is public ([rule/0033](../rule/0033-private-sources-stay-in-vault-notes.md)).
- [clarify] The record is `accepted` on the owner's choice of option C; the plan that builds it, [adr-scorer v3](../plans/202610190307_adr-scorer-v3/index.md), is not yet developed.
