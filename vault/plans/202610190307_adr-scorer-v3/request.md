# Request — ADR scorer v3

Source: [OI-0035](../../open-items/OI-0035.md)

## Request

> И пройдись по этим проектам, погоняй там вот эти эксперименты, вот, и заполируй промпт этого скорера, получается.

## Task type

`feature` — the scorer gains a user-visible capability: it routes a draft to the record type it belongs to, names the records it overlaps and the cheap options it misses, and the ADR brief shows those lists to the owner. Not `bug`: today's scorer does what its plan specified (score the text against a rubric); nothing diverges from its spec. Not `refactoring`: the reply contract, the gate and the brief all change visibly.

## Problem

Today `booping:adr-scorer` gets the ADR text and the rubric pasted into its prompt and answers `score: {0-3}` plus findings; the specs guide's `## Record` scenario redrafts on a score ≤ 1. The experiment (private note, not published) showed a text-only rubric cannot tell an ADR that should have been a rule, a value or nothing at all, and that the score barely moves when a cheap option is cut — the list of missing options is the signal. The scorer must get the specs guide excerpt and the tier's record inventory (existing values, rules, ADRs as `ref — title: summary`, plus the project's primitives), answer one JSON line (route, route_why, overlaps, alt_score, missing), block on `route ≠ adr` or `alt_score ≤ 1`, and otherwise feed `missing` and `overlaps` into the brief.

## Clarifications and Decisions

- Input = specs guide excerpt + the tier's record inventory (value/rule/adr `ref — title: summary`) + the project's primitives; model Opus, no tools (owner: "С, очевидно, надо брать").
- Reply = one JSON line: `route`, `route_why`, `overlaps` (≤ 3 bare refs), `alt_score` (0–3), `missing` (≤ 3, each naming the existing primitive or record) — prompt v3 from the experiment (owner).
- Gate: block when `route ≠ adr` or `alt_score ≤ 1`; otherwise pass and carry `missing` into the brief as "Не взвешено:" and `overlaps` as "Задевает:" (owner).
- The inventory holds only records that exist when the ADR is written — the ADR under review and anything newer stay out (owner).
- The agent keeps `tools: ListAgents`; its body stops claiming it has no tools (owner).
- Eval fixtures stay booping-only (public repo): deleted ADRs from git history (0012 → rule, 0013 → none, 0005 → value) and mutants of 0003/0007/0030/0033 (owner).
- Running the experiments across projects is done; this plan ships the result, it does not re-run the private experiment (proposal).
