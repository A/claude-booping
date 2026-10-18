---
title: "ADR scorer v3 — routing, overlaps and missing options from the guide and the
  record inventory"
type: "feature"
status: done
sp: 28
related_to: null
created: 2026-10-19 03:08
planned: null
started: 2026-10-19 03:35
completed: 2026-10-19 04:08
code_reviews: []
sessions:
- 0c3f5735-fd95-5891-a767-80fb60a7872b
- 8ad47d44-8fe9-5ed6-bf18-7c9966c47b57
retro: null
summary: 'ADR scorer v3: guide excerpt + record inventory in, one JSON line out; gate
  on route and alt_score, missing joins the brief'
commit: 22bd66ee450a0d362c8e2053045838cd7cc4f378
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-19 03:13
agents:
- develop-loop/G1:a01a7f26eee2c10e7
- develop-loop/G2:aa03af6d3ffcef7e2
- verify:a33d6e14dfba21445
metrics_active_minutes: 41
metrics_models:
- claude-opus-5-5
metrics_tokens_input: 118
metrics_tokens_output: 42325
metrics_tokens_cache_creation: 211016
metrics_tokens_cache_read: 5211484
---

# ADR scorer v3 — routing, overlaps and missing options from the guide and the record inventory

## Context

Request: [request.md](request.md), open item [OI-0035](../../open-items/OI-0035.md).

`booping:adr-scorer` today gets an ADR and the v1 rubric (`playbooks/specs/guide/adr-rubric.md`) pasted into its prompt and replies `score: {0-3}` plus findings; the specs guide's `## Record` scenario redrafts on a score ≤ 1. Judging the text alone, it cannot tell an ADR that should have been a rule, a value or nothing, and its score barely moves when a cheap option is cut. The owner's experiment (private note, not published) settled the fix: give the scorer the specs guide excerpt, the tier's record inventory and the project's primitives, ask it for route, overlaps, alt_score and missing in one JSON line, and gate on route and alt_score.

Outcome after it ships: when the owner records an ADR, a draft that is really a rule, a value or nothing is stopped before it is written as an ADR and routed where it belongs; a real ADR reaches the brief with the cheap options it never weighed listed under «Не взвешено:» and the records it touches under «Задевает:».

Values in play: value/0012 (quality at a rational cost — Opus with the inventory pasted, ≈ 7K tokens in, not repo read access at ×6), value/0002 (the scorer gets the guide excerpt and a one-line-per-record inventory, never the records themselves), value/0015 (the inventory is a slice of many files filled into a prompt, so a CLI produces it), value/0003 (the guide excerpt is pasted from `src/specs/README.md`, not copied into the rubric), value/0010 (an eval suite with labelled fixtures proves routing and missing). No departure from a value or rule.

## Decisions

1. Scorer input = the v3 task text (the rubric file) + the format guide's `## Types` and `## When a record is worth writing` sections + the tier's value/rule/adr inventory + the project's primitives + the draft ADR; Opus, no tools beyond `ListAgents`. (user)
2. Reply = one JSON object on one line: `route` (`adr|rule|value|story|reference|idea|open-item|none`), `route_why` (one sentence), `overlaps` (≤ 3 bare refs), `alt_score` (0–3), `missing` (≤ 3, each naming the existing primitive or record when there is one) — the experiment's prompt v3 text, verbatim. (user)
3. Gate: `route ≠ adr` or `alt_score ≤ 1` blocks; otherwise the brief carries `missing` as «Не взвешено:» and `overlaps` inside «Задевает:». (user)
4. The inventory holds only records that exist when the ADR is written: live, that is every value/rule/adr record of the tier except the draft itself; in eval fixtures, the records whose `created_at` is not after the fixture ADR's. (user)
5. The agent keeps `tools: ListAgents`; its body stops claiming it has no tools. (user)
6. Eval fixtures are booping-only: ADRs deleted on 2026-10-18 recovered from git (0012 → rule, 0013 → none, 0005 → value), the kept 0019/0024/0003, and mutants of 0003/0007/0030/0033 with one cheap option cut. (user)
7. The inventory comes from `booping specs ls`, extended with a repeatable `--type`, `--exclude {ref}` and `--titles` (line `{type}/{NNNN}  {status}  {title}: {summary}`) — extending the existing primitive rather than a new command, and the title keeps the tested `title: summary` shape. (proposal)
8. The inventory's tier is the one the ADR is written to; other tiers stay out, as in the experiment. (proposal)
9. "The project's primitives" are supplied by the driver as prose: one line per command or building block the attached repo's `CLAUDE.md` names, nothing when it names none — only a model reads them, so prose (rule/0025). (proposal)
10. The guide excerpt is the README's two sections verbatim; the excerpt's one extra line (the `open item` bullet) is added to README's `## When a record is worth writing`, so the shipped guide and the scorer's input are the same text. (proposal)
11. `route ≠ adr` blocks the ADR outright: the material is recorded as the routed type instead (a value as an owner draft, `open-item` filed as an item, `none` dropped and reported) — supervised the route and `route_why` are shown to the user first, autonomous it is logged as an agent decision. `alt_score ≤ 1` keeps today's loop: redraft the alternatives from `missing`, at most two rounds, then the brief carries the score as it stands. (proposal)
12. The brief header keeps «оценка альтернатив {alt_score}/3»; «Не взвешено:» is a new line after «Ключевые моменты», omitted when `missing` is empty; `overlaps` refs merge into «Задевает:». (proposal)
13. Eval tiers: smoke asserts zero tool calls and the JSON contract; regress asserts `route` exactly, `alt_score` within ±1 on the kept fixtures, the 0019 < 0003 order on `alt_score`, and, per mutant, an llm-rubric judge that `missing` names the cut option. Eval runs stay advisory, never CI. (proposal)

## Architecture

- `playbooks/specs/guide/prompt.md` `## Record` is the only caller. It assembles the scorer prompt from: the rubric file's text, the two README sections, `booping specs ls --tier {tier} --type value --type rule --type adr --exclude adr/{NNNN} --titles`, the primitives list, the ADR text — all pasted, no paths, under fixed headings.
- `agents/adr-scorer.md` — static body (no render line), reads the five pasted parts and replies per the rubric's contract.
- `playbooks/_agents/adr-scorer/agent_provider.py` mirrors the caller: `config.paste` gains section extraction (`{file}#{heading}`), and per-test vars `inventory` and `primitives` are pasted under the caller's headings, so each fixture carries its own frozen inventory.
- `booping specs ls` stays one command; the flags are additive, default output unchanged.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Inventory flags on booping specs ls](milestones/M01-inventory-flags-on-booping-specs-ls/M01-inventory-flags-on-booping-specs-ls.md) | 5 | done |
| 02 | [Scorer v3: rubric, agent body, the guide's Record scenario](milestones/M02-scorer-v3-rubric-agent-body-the-guide-s-record-scenario/M02-scorer-v3-rubric-agent-body-the-guide-s-record-scenario.md) | 10 | done |
| 03 | [Scorer eval suite on v3](milestones/M03-scorer-eval-suite-on-v3/M03-scorer-eval-suite-on-v3.md) | 11 | done |
| 04 | [Stale descriptions of scorer v1](milestones/M04-stale-descriptions-of-scorer-v1/M04-stale-descriptions-of-scorer-v1.md) | 2 | done |

## Groups

| group | milestones | sp |
| --- | --- | --- |
| G1 | M01, M02 | 15 |
| G2 | M03, M04 | 13 |

## Final Verification

- [ ] `just ci` passes, except `just snapshots` reporting drift in `playbooks/specs/_reports/output.md` limited to the guide step — the owner accepts it.
- [ ] `bin/booping render-playbook specs --step guide` renders clean, no `{{placeholder}}` leaks.
- [ ] `just smoke _agents/adr-scorer` and `just smoke specs/guide` pass; regress run reported, advisory.

## Out of scope

- Re-running the private cross-project experiment.
- Scoring records other than ADRs; cross-tier inventories.
- Any caller of the scorer besides the specs guide's `## Record`.

## CLAUDE.md impact

Layout bullet on `agents/adr-scorer.md` — M04 task 4.1.
