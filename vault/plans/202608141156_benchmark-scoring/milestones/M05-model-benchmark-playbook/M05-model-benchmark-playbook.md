---
id: "05"
title: "model-benchmark playbook, reviews and docs"
sp: 5
status: pending
plan: "vault/plans/202608141156_benchmark-scoring/index.md"
---

# M05: model-benchmark playbook, reviews and docs

`/playbook model-benchmark` drives the whole lifecycle — prepare, run, measure, publish — with two detached diff reviews inside measure, and the repo docs name the new vault surface.

**Scope**: `vault/_playbooks/model-benchmark/` (new: `playbook.md`, `playbook.yaml`, step dirs `prepare/ run/ measure/ publish/` each with `prompt.md`, `review-rubric.md` beside the measure step), `vault/config.yaml` (one key), `CLAUDE.md` (vault section). Follows the docs-playbook local pattern (`vault/_playbooks/docs/` is the structural reference). Consumes M01's registry, M02–M04's `bench-score`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Manifest: `playbook.md` (name, title, summary, trigger "benchmark a model / score a bench branch", `requires_project: true`; preamble names the registry as the source of benchmark ids, default = its only entry) and `playbook.yaml` — flat graph `prepare → run → measure → publish`, `states.run`: artifact `runs/{ts}-{model_slug}.md` under `vault/benchmarks/` (the detail report is the run artifact), `preparing → running → measuring → publishing → done`, `cancelled` off every non-terminal status; sprint failure is data in the artifact (`outcome: fail@Mnn`), not a state — `running → measuring` fires on sprint end either way. | `vault/_playbooks/model-benchmark/playbook.md`, `…/playbook.yaml` | 1 | pending |
| 5.2 | Step prompts. `prepare`: resolve model + benchmark id against the registry, hard-stop without a model name; preflight — bench repo tree clean, branch unborn, `OPENROUTER_API_KEY` present, worker logs dir writable; cut `bench/{model_slug}` off baseline; venv refresh per the guide's precheck. `run`: drive `/playbook develop {plan}` inline in the same conversation under the guide's autonomy rules (auto-answered gates recorded; abort after attempts exhaust → `fail@Mnn`, continue). `measure`: run `bench-score report`; spawn the two reviewers of task 5.3 in parallel and fold their grades/findings into the detail report's review section. `publish`: append the row to `history.md`, commit vault artifacts, then PR idempotently — `gh pr list --head bench/{model_slug}` first, existing PR → update its body, else `gh pr create` against base `bench/reference` with the detail report as body; a failed push/PR is reported with the vault artifacts already committed locally, never rolled back; never merge/delete `bench/*`. | `vault/_playbooks/model-benchmark/{prepare,run,measure,publish}/prompt.md` | 2 | pending |
| 5.3 | Reviews: `review-rubric.md` — benchmark-agnostic diff-review rubric (correctness, test quality, code quality, scope discipline; grade /5 with a one-line justification each + findings list; no praise, no restating the diff) reused verbatim by both reviewers; `vault/config.yaml` gains `core.model_benchmark_playbook.review_agent: codex`; measure's prompt spawns `fable:medium` generic + the configured agent, both detached, fable-only when the key is null. | `vault/_playbooks/model-benchmark/measure/review-rubric.md`, `vault/config.yaml` | 1 | pending |
| 5.4 | Docs: CLAUDE.md vault bullet gains `benchmarks/` (registry, guide, history, runs, mutations, `_scripts/bench-score`); `vault/benchmarks/index.md` body links the playbook as the way to run a benchmark. No README change — local playbooks are not plugin surface. | `CLAUDE.md`, `vault/benchmarks/index.md` | 1 | pending |

## Definition of Done

### Task 5.1
- [ ] `bin/booping render-playbook model-benchmark` renders: 4 steps in order, `## State` table matches the machine, no STOP/Note notices.
- [ ] `booping playbook-state model-benchmark --workdir …` runs against a scratch workdir without error.

### Task 5.2
- [ ] Each prompt passes the information-architecture pass (lesson 0004): no restated registry data, no duplicated guide prose — steps reference `guide.md` and the registry instead of copying them.
- [ ] `prepare` refuses to proceed on: no model given, dirty tree, existing branch, missing key env — each with a one-line reason.
- [ ] `run`'s autonomy block matches the guide's (auto-answer gates, approve abort, never `AskUserQuestion`) by reference, not by copy.
- [ ] `publish` states the PR base is `bench/reference`, the branch is left in place, and a re-run updates the existing PR instead of erroring on a duplicate.

### Task 5.3
- [ ] Rubric contains no benchmark-specific nouns (no "txtar", no "frontmatter-update") — it must survive a coding-task reference plan.
- [ ] Reviewer return contract bounded (lesson 0007): grade + justification + findings list, nothing else.
- [ ] Null `review_agent` → measure spawns fable only, no error.

### Task 5.4
- [ ] CLAUDE.md builds its vault bullet without breaking the section's one-line style.
- [ ] Registry body links `_playbooks/model-benchmark` and `guide.md`.

## Verify

- `bin/booping render-playbook model-benchmark` — clean render, step table as designed.
- `bin/booping render-playbook model-benchmark --step prepare` (and each other step) — bodies render with lessons injected, no placeholder leaks.
- `grep -n "txtar\|frontmatter" vault/_playbooks/model-benchmark/measure/review-rubric.md` — empty.
- `bin/booping config-get core.model_benchmark_playbook.review_agent` prints `codex`.
