---
id: "03"
title: "Scorer eval suite on v3"
sp: 11
status: done
plan: "plans/202610190307_adr-scorer-v3/index.md"
---

# M03: Scorer eval suite on v3

## Tasks

**Goal:** `playbooks/_agents/adr-scorer/` proves routing, overlaps-free contract, alt_score and missing on booping-only fixtures. **Scope:** the suite directory only.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Provider: a `config.paste` value may be `{file}#{heading}[,{heading}]` and pastes those H2 sections; per-test vars `inventory` and `primitives` are pasted under the headings `## Record` uses, in its order; config preamble and headings mirror `## Record` | `playbooks/_agents/adr-scorer/agent_provider.py`, `playbooks/_agents/adr-scorer/promptfooconfig.yaml` | 2 | done |
| 3.2 | Fixtures from git: ADRs 0012, 0013, 0005 at `19a984f^`; each fixture's inventory = `bin/booping specs ls --type value --type rule --type adr --titles --exclude adr/{NNNN}` run against a worktree of the commit that holds the ADR, lines whose record `created_at` is after the ADR's dropped; same for the kept 0019/0024/0003; one primitives file from this repo's CLAUDE.md `## Commands` per Decisions 9. A header comment in `tests.yaml` names the commit and the command | `playbooks/_agents/adr-scorer/_fixtures/` | 3 | done |
| 3.3 | Mutants of 0003, 0007, 0030, 0033: each with one cheap-option row (prose, an existing primitive, or building nothing) cut, and its Context line about it; its inventory as in 3.2; the cut option named in the test's metadata | `playbooks/_agents/adr-scorer/_fixtures/` | 3 | done |
| 3.4 | Asserts and tests: `contract` (one JSON line, the keys, enum, ≤ 3 lists, `alt_score` 0–3), `route` (exact), `alt_score` (±1), `order` on `alt_score`; smoke = tools + contract on every fixture; regress = route on all, alt_score on the kept, order 0019 < 0003, an llm-rubric judge per mutant "`missing` names {cut option}"; the old `score` check goes | `playbooks/_agents/adr-scorer/asserts.js`, `playbooks/_agents/adr-scorer/tests.yaml` | 3 | done |

Test surface: the `booping:adr-scorer` agent through the live caller's prompt shape; cases — deleted ADRs route to rule/none/value, kept route to adr, alt_score ±1, order, mutants' missing; tier — promptfoo smoke (deterministic) + regress (llm-rubric), integration against the real agent, no mocks.

Worker returns: the list of changed files, the smoke result line, and whether regress ran.

## Definition of Done

Task 3.1
- [x] Provider builds the prompt in `## Record`'s order with the two README sections, the fixture's inventory and primitives; stdlib-only, `call_api` never raises.

Task 3.2
- [x] Each fixture has its frozen inventory with no record newer than the ADR and without the ADR itself; no fixture or inventory names another project (rule/0033).

Task 3.3
- [x] Four mutant fixtures, each with exactly one cheap option cut and the cut named in metadata.

Task 3.4
- [x] No assert parses `score: N`; `just smoke _agents/adr-scorer` passes.

## References

- `playbooks/_agents/adr-scorer/tests.yaml`, `asserts.js` — today's shape.
- `playbooks/_lib/grader.yaml` — llm-rubric judge config.

## Verify

`just smoke _agents/adr-scorer`
