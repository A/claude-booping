---
id: "03"
title: "bench-score: process profile, cost and scorecard emit"
sp: 3
status: pending
plan: "vault/plans/202608141156_benchmark-scoring/index.md"
---

# M03: bench-score: process profile, cost and scorecard emit

`bench-score` profiles the run from its ndjson logs, prices it from OpenRouter, folds every layer into the two composites, and renders the history row plus the detail report.

**Scope**: `vault/benchmarks/_scripts/bench-score` (extends M02's file). Inputs: the registry entry (M01), per-attempt log quadruples `{ts}-{model_slug}-{milestone}.{ndjson,out,err,status}` in the registry's `logs_dir`, the OpenRouter generation endpoint. ndjson schema: `system/init` line, `assistant`/`user` turns (`message.id` = OpenRouter `gen-…` id, `tool_use` items), final `result` line (`duration_ms`, `num_turns`, `stop_reason`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `process` subcommand: select the run's log files by model slug + benchmark window, then per milestone and aggregate — attempts (file count per milestone, cross-checked against `feedback.md` sidecars on the branch), wall clock from `result.duration_ms`, tool calls total and by name, malformed tool inputs (tool_result error payloads), degenerate loops (≥3 consecutive identical tool+input), context deaths (`stop_reason` / truncation errors), churn (lines pushed through Write/Edit inputs ÷ final diff size), blind rebaselines (`--txtar-update` bash invocations before the first green e2e run in log order). JSON out. | `vault/benchmarks/_scripts/bench-score` | 1 | pending |
| 3.2 | `cost` subcommand: dedupe `gen-…` ids across the run's ndjson files, `GET /api/v1/generation?id=…` each with bearer from the env var the registry's `api_key_env` names (absent env var → hard error naming it), sum `total_cost` and native prompt/completion/cached tokens; per-milestone and total. Transient failures (timeout, 429, 5xx) retry with backoff a bounded number of times; ids still failing after retries — and auth failures, and expired generations — are counted per class and reported, and the subcommand degrades to the ndjson `result.total_cost_usd` sum as a clearly labeled fallback figure instead of failing the run. | `vault/benchmarks/_scripts/bench-score` | 1 | pending |
| 3.3 | `report` subcommand: run gates+corpus+process+cost (or accept their JSON via flags), compute `code /100` and `agentic /100` from the registry's `weights` (attempts 30 first-pass, −10 per retry, abort 0; rebaseline −10 each; malformed −2, loops −5, deaths −10 within tool-discipline; churn full ≤1.5×, zero ≥4×), and write both surfaces: the one-line history row (append-ready markdown) and the detail report `vault/benchmarks/runs/{ts}-{model_slug}.md` — all base checks with evidence, composite breakdown math, review section left as a placeholder block the playbook fills. `--dry-run` prints instead of writing. | `vault/benchmarks/_scripts/bench-score` | 1 | pending |

Tests (lesson 0016): run against the real deepseek logs and branch; assert the emitted JSON/markdown against PR #35's hand-computed facts (wall 64m17s, cost ≈ $6.82, 0 malformed, 0 loops, attempts 1/1/1). Derived by hand, not from the script.

## Definition of Done

### Task 3.1
- [ ] Deepseek run: attempts 1/1/1, wall within a minute of 64m17s, zero malformed / loops / deaths — matching PR #35.
- [ ] Loop and malformed detectors demonstrated on committed synthetic ndjson fixtures under `vault/benchmarks/_fixtures/ndjson/` (one file per detector, hand-written) — not only on the clean run, and reproducible by any future session.
- [ ] Log files from other models/benchmarks in the same dir are excluded by the slug+window filter.

### Task 3.2
- [ ] Deepseek run total within a few percent of $6.82; native token totals reported with cached tokens separated.
- [ ] Missing env var → exit 2 with the variable name; retry/degrade path exercised (point the endpoint at an unroutable host via an override flag or env) and the fallback figure labeled in output — an API outage never fails the run.
- [ ] Requests are deduped — id count fetched ≤ unique ids, never one per ndjson line.

### Task 3.3
- [ ] Composites match a hand-computed value for the deepseek run (weights from the registry, arithmetic shown in the detail file).
- [ ] History row column order matches `history.md`'s M01 header exactly.
- [ ] Detail file renders in Obsidian: tables, no angle-bracket placeholders, one line per paragraph/row.
- [ ] Changing a weight in the registry changes the composite without a script edit.

## Verify

- `vault/benchmarks/_scripts/bench-score report --benchmark frontmatter-update-e2e --branch bench/deepseek-deepseek-v4-pro-0813 --dry-run` prints the full row + detail; numbers match PR #35 where PR #35 states them.
- `OPENROUTER_API_KEY= vault/benchmarks/_scripts/bench-score cost …` exits 2 naming the variable.
- Re-running `report` is idempotent under `--dry-run` (no files written, same output).
