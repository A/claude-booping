---
title: "Benchmark scoring — per-model scorecard for the fixed develop-sprint benchmark"
type: "feature"
status: in-progress
sp: 16
related_to: null
created: 2026-08-14 11:56
planned: null
started: 2026-08-14 12:40
completed: null
code_reviews: []
sessions:
- ae7739d5-fb40-4389-b0a9-37b87b6acc6a
- d7a6ef49-832f-4f31-9dd7-d3baad11a0b2
retro: null
summary: 'model-benchmark playbook: prepare/run/measure/publish, bench-score script,
  mutation set, scorecard history table'
commit: d654e175ecc9854fb76765bd068250f8c7d2d500
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a075d8d3a7c392512
  cross-review: a99335e13c68d04ac
reviewed_at: 2026-08-14 12:39
---

# Benchmark scoring — per-model scorecard for the fixed develop-sprint benchmark

## Context

`vault/benchmarks/guide.md` defines a fixed develop-sprint benchmark: every model runs the same groomed plan (`202608121417_frontmatter-update-e2e-migration`) from baseline `e0d1796` on its own `bench/{model_slug}` branch in `/home/anton/Dev/@A/claude-booping-local-bench`. Today a run ends in a hand-written report (PR #35 shape) — ad hoc, not comparable across models, recorded nowhere durable. Gates are taken from the run's own bookkeeping, corpus quality is unmeasured, process cost is assembled by hand from OpenRouter dashboards. After this plan: one `model-benchmark` playbook drives the full lifecycle — prepare → run → measure → publish — and every run appends one comparable scorecard row to `vault/benchmarks/history.md` backed by a full per-run detail report, with all mechanical metrics computed by a committed `bench-score` script.

## Decisions

- **Scorecard = composites over raw checks**: `history.md` rows carry `outcome`, `att` (attempts per milestone, e.g. `1/1/2`), `code /100`, `agentic /100`, `review /5`, plus raw `diff`, `tokens`, `cost`, `wall` and a detail link. All ~24 base checks and the composite math live in the per-run detail file `vault/benchmarks/runs/{ts}-{model_slug}.md` — every top-line number auditable. Weights are data in the registry, not code.
- **Benchmark registry**: `vault/benchmarks/index.md` frontmatter is the machine-readable registry — per benchmark: id, repo, baseline, plan path, branch scheme, worker agent, scope allowlist, etalon case list (34 names + 3 gap names, frozen from the opus corpus at `dc0be24`/`0648787`), mutation dir, composite weights. `guide.md` stays the default benchmark's runbook; `bench-score` reads only the frontmatter.
- **Cost from OpenRouter, not from Claude Code's pricing**: ndjson assistant `message.id` values are OpenRouter `gen-…` ids (verified live); `GET /api/v1/generation?id=…` with plain `OPENROUTER_API_KEY` returns exact `total_cost` and native prompt/completion/cached tokens. Dedupe ids, fetch, sum. Key named via the `api_key_env` convention — config never carries the secret.
- **Mutations hand-authored, not mutmut**: a fixed set of 10–15 patch files applied one at a time with `git apply`; corpus must fail each. Auto-generated mutant sets vary with code and tool version and kill cross-model comparability; a curated set is deterministic and identical for every model. Set validated against the opus etalon corpus (must kill all).
- **Reviews = fable + configured agent**: measure spawns two parallel detached diff reviews with one shared abstract rubric (correctness, test quality, code quality, scope discipline — survives swapping the reference plan for a coding-not-testing task): a generic `fable:medium` sub-agent and the agent named by `core.model_benchmark_playbook.review_agent` (`codex` in this vault); fable-only when the key is null. Grade /5 each, mean in the row, findings in the detail file.
- **run step is runner-driven, not detached**: no nested-playbook mechanism exists — the run step instructs the runner to drive `/playbook develop` inline in the same conversation under the guide's autonomy rules. A sprint that fails all restarts is a recorded result (`fail@Mnn`), not an abort: measure and publish still run.
- **Gates are re-run, not distrusted**: DoD checkboxes are runner-validated already; layer-1 gates re-run mechanically in a fresh worktree because it is cheap and makes the row self-contained, not because the run's bookkeeping is suspect.
- **Vault paths are repo content here**: this project's vault is checked into the repo, so milestones write `vault/…` files as ordinary repo files; run-state frontmatter stays hook-written only.

## Architecture

Assets live under `vault/benchmarks/`: `index.md` (registry, frontmatter = data), `guide.md` (default benchmark runbook, gains venv precheck + failed-all-restarts case), `history.md` (slim append-only table), `runs/` (per-run detail reports), `mutations/{benchmark-id}/` (patch set + manifest), `_scripts/bench-score` (uv inline-metadata Python, subcommands `gates`, `corpus`, `process`, `cost`, `mutations`, `report`; reads the registry frontmatter, works in a throwaway `git worktree` of the bench repo, emits JSON per layer and renders the history row + detail markdown). The playbook `vault/_playbooks/model-benchmark/` follows the docs-playbook local pattern: `playbook.md` + `playbook.yaml` (state machine `preparing → running → measuring → publishing → done`, `cancelled` off every status; artifact = the run's detail file) + one dir per step. prepare/run/measure/publish step prompts call `bench-score` and the two reviewers; nothing else computes metrics. Config surface: one new vault key `core.model_benchmark_playbook.review_agent`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Benchmark registry, guide updates and history seed](milestones/M01-registry-guide-history/M01-registry-guide-history.md) | 2 | done |
| 02 | [bench-score: gates and corpus quality](milestones/M02-bench-score-gates-corpus/M02-bench-score-gates-corpus.md) | 3 | done |
| 03 | [bench-score: process profile, cost and scorecard emit](milestones/M03-bench-score-process-cost/M03-bench-score-process-cost.md) | 3 | pending |
| 04 | [Fixed mutation set and kill-rate scoring](milestones/M04-mutation-set/M04-mutation-set.md) | 3 | pending |
| 05 | [model-benchmark playbook, reviews and docs](milestones/M05-model-benchmark-playbook/M05-model-benchmark-playbook.md) | 5 | pending |

## Final Verification

- [ ] `bin/booping render-playbook model-benchmark` renders clean — steps table shows prepare/run/measure/publish, no STOP notices, no placeholder leaks.
- [ ] `bench-score report --benchmark frontmatter-update-e2e --branch bench/deepseek-deepseek-v4-pro-0813` produces a full history row + detail file from the existing PR #35 branch, with cost within a few percent of the hand-computed $6.82.
- [ ] Every mutation patch applies clean on baseline `e0d1796` and is killed by the opus etalon corpus.
- [ ] `history.md` and `runs/{…}.md` render as tables in Obsidian — no angle-bracket placeholders, no hand-broken lines.

## Out of scope

- No actual benchmark run of a new model — the playbook is validated by rendering plus `bench-score` against the existing deepseek branch.
- No merging, deleting or pushing of `bench/*` branches; publish opens a PR against `bench/reference` and stops.
- No changes to the develop playbook, the openrouter-developer agent, or `~/.claude/bin/openrouter-milestone`.
- No second benchmark entry in the registry — schema supports it, only `frontmatter-update-e2e` ships.
- No LLM-judge beyond the two diff reviews and measure's case-mapping judge (a detached sub-agent mapping renamed branch cases onto etalon/gap names from programmatic lists; recall and gap scores use its mapped counts); the M03 cross-check table gets mechanical prechecks only.

## CLAUDE.md impact

The Vault section's directory list gains `benchmarks/` (registry, history, runs, mutations, bench-score) — owned by a task in M05. No other CLAUDE.md changes: the playbook is vault content, out of framework scope.
