---
id: "01"
title: "Benchmark registry, guide updates and history seed"
sp: 2
status: done
plan: "vault/plans/202608141156_benchmark-scoring/index.md"
---

# M01: Benchmark registry, guide updates and history seed

Machine-readable benchmark registry exists, the guide covers venv prep and total failure, and the history table is seeded — every later milestone reads this data instead of restating it.

**Scope**: `vault/benchmarks/index.md` (new), `vault/benchmarks/guide.md`, `vault/benchmarks/history.md` (new). Read by `bench-score` (M02–M04) and the playbook steps (M05).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Registry `index.md`: frontmatter `benchmarks:` list with one entry `frontmatter-update-e2e` — `repo`, `baseline: e0d1796`, `plan`, `branch_scheme: bench/{model_slug}`, `worker: openrouter-developer`, `logs_dir: ~/.tmp/openrouter-developer`, `api_key_env: OPENROUTER_API_KEY`, `scope_allowlist` (glob list), `etalon_cases` (the 34 case names from the opus corpus at `dc0be24`/`0648787`), `gap_cases` (the 3 names from M03's cross-check table), `mutations_dir`, `weights` (code: gates 40 = ci 10 / determinism 10 / scope 10 / e2e 5 / unit-deleted 5, corpus 60 = mutation 25 / recall 15 / 4-channel 10 / gaps 5 / wildcard 5; agentic: attempts 30, rebaseline 20, tool-discipline 30, churn 20). Body: short table of registered benchmarks linking each runbook. | `vault/benchmarks/index.md` | 1 | done |
| 1.2 | Guide updates + history seed: add to `guide.md` a venv precheck step before development (run `uv sync` in both projects and verify console-script shebangs point at this tree — a copy dir ships stale venvs and fixing them is out of scope for the model under test) and a failed-all-restarts case (abort approved after attempts exhaust → outcome `fail@Mnn`, branch kept, measure/publish still run); link the registry. Seed `history.md` with the slim table header (`date, model, outcome, att, code, agentic, review, diff, tokens, cost, wall, run`) and a one-line column legend. | `vault/benchmarks/guide.md`, `vault/benchmarks/history.md` | 1 | done |

## Definition of Done

### Task 1.1
- [x] Registry frontmatter parses as YAML and carries every listed key for `frontmatter-update-e2e`; etalon list is exactly the 34 names on HEAD under `booping-python/e2e/cases/frontmatter-update/` plus the 3 gap names from the reference plan's M03 table.
- [x] Weights sum to 100 inside each composite.
- [x] No angle-bracket placeholders; body table links `guide.md`.

### Task 1.2
- [x] Guide's venv precheck sits before the develop invocation in run order and states the model never fixes venvs itself.
- [x] Failed-all-restarts case states `fail@Mnn` is a recorded result and measure/publish still run.
- [x] `history.md` has the header row and legend, no data rows.

## Verify

- `python -c "import yaml,sys; d=yaml.safe_load(open('vault/benchmarks/index.md').read().split('---')[1]); b=d['benchmarks'][0]; assert len(b['etalon_cases'])==34 and len(b['gap_cases'])==3"` exits 0.
- `ls booping-python/e2e/cases/frontmatter-update/ | sort` matches the registry's `etalon_cases` sorted.
- Read `guide.md` end to end: steps still coherent as a runbook, new cases in the right order.
