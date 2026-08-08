---
title: Bench scoring v2, judge kind, groom cases, compare reports
type: feature
status: done
sp: 36
split_from: plans/20260709-benchmark-framework-core.md
created: 2026-07-09 00:00
planned: 20260709 06:51
started: 20260709 06:57
completed: 2026-07-09 12:35
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "Bench v2: penalty scoring, judge kind, typer + groom cases, compare reports,
  parallel reps"
commit: c6830c41a6bf9f545c3f90325803276786e689d8
sessions:
- 3135c084-871e-4681-860b-807c422a3b65
- d6cbb722-83fa-4e20-93fd-7be5f4c8229c
metrics_active_minutes: 405
metrics_models:
- claude-fable-5
metrics_tokens_input: 149028
metrics_tokens_output: 656726
metrics_tokens_cache_creation: 5907193
metrics_tokens_cache_read: 66638574
---

# Bench scoring v2, judge kind, groom cases, compare reports

## Context

Follow-up sprint on the private benchmark repo `~/Dev/@A/claude-booping-bench` (framework core shipped in `plans/20260709-benchmark-framework-core.md`). The harness today: one develop case (`cases/fastify-naming-lesson/`), five deterministic check kinds, weighted-ratio dimension scoring, single-run markdown reports, sequential reps.

This sprint, in locked priority order: (1) penalty scoring v2 — predictable point deductions replace weighted ratios; (2) a second develop case (P2 buried-linter-break) on a second stack (typer); (3) the first groom case (G4 CLAUDE.md-convention, judge-free); (4) the `judge` check kind (LLM rubric via the Agent SDK); (5) the fastify groom case G1 (test-checklist coverage); (6) compare/delta report mode; (7) parallel container orchestration. Penalty-scoring spec, seedable problem library, and groom scenarios: bench repo `docs/case-backlog.md`.

## Decisions

- **Penalty scoring semantics**: `score = max(0, 100 − Σ penalties)`, integer. Each check carries exactly one of `penalty: <points>` or `penalty_each: <points>` + `cap: <points>` — `weight` is removed and rejected with a pointed loader error. Rep record gains `score` (int) and `deductions: [{check, points, evidence}]`. Standard tariff per `docs/case-backlog.md` — deviations only with a comment.
- **`scores{}` continuity**: the per-dimension floats stay in the record and report, re-derived as the points-kept ratio per dimension — `1 − (points deducted in dim / max deductible in dim)`, where a check's max deductible is `penalty` or `cap`. Same 0..1 range, same report columns.
- **No legacy-record support**: report v2 exits 1 on records without `score`. Old runs are cheap to regenerate; no dual-format rendering.
- **Reference case migrates in the same milestone** as the engine change — no weighted-ratio case left behind (lesson 0005).
- **Judge executor**: new `judge` check kind — params `target: file | transcript`, `path` (glob, required iff `target: file`), `rubric` (non-empty list of item strings), scored binary per item in one `claude-agent-sdk` query against `claude-haiku-4-5-20251001` (fixed default; no per-check model key this sprint). `occurrences` = failed rubric items → pairs naturally with `penalty_each`+`cap`. Runs in-container inside `score_case` (auth already mounted); SDK already a dep (`claude-agent-sdk>=0.2.113`). Parse failure retries once, then the check fails with the raw output as evidence — a judge error never crashes the rep.
- **G4 reuses the typer fixture** added for P2 — no third fixture this sprint.
- **Compare matching**: `report <run-a> --compare <run-b>` matches groups by `(case, model, tag)`; mismatched rep counts within a matched group → exit 1 on stderr. Unmatched groups listed below the table, never silently dropped.
- **Parallel orchestration**: `run --parallel N` (default 1 = today's sequential loop). N>1 requires `ANTHROPIC_API_KEY` (OAuth creds are subscription-rate-limited) — refused with exit 2 otherwise. Futures over reps; the main thread appends each completed record to `results/<run-id>.jsonl` (single writer, no lock).
- **Case prompts stay unbounded by design**: the `case.yaml` prompt and seeded briefs simulate a real user request to the skill under test. Lesson 0007 (bound return contracts) governs harness-authored delegation briefings, not the system-under-test's input — bounding the benchmarked skill's output there would contaminate the measurement. Scoring reads artifacts (plan file, repo, transcript), never the skill's prose reply.

## Risk register

- **Judge verdict flakiness** (cross-validation blind spot, mitigated): raw-JSON contract + fence-stripping + one corrective retry in task 4.2; residual per-item verdict instability across reps is measured at M5 calibration and recorded in the case's calibration block.
- **Parallel container collisions** (cross-validation blind spot, assessed non-issue): containers publish no ports and names are already rep-unique; noted in task 7.1.

## Architecture

All work lands in `~/Dev/@A/claude-booping-bench`. Touched modules: `case.py` (expect schema v2 + judge params), `checks.py` (occurrence counting, judge dispatch), new `judge.py` (SDK call + verdict parsing), `scoring.py` (deductions + score), `report.py` (tariff table, compare mode), `cli.py` (`--compare`, `--parallel`). New case dirs `cases/typer-buried-linter/`, `cases/typer-groom-claudemd-convention/`, `cases/fastify-groom-test-checklist/`; new `fixtures/typer.yaml`. Consumers are the operator (stdout markdown) and future CI; no other tool parses the report.

## Milestones

### M1: Penalty scoring v2 — 10 SP | done

**Goal**: every check carries a tariff; records carry `score` + `deductions[]`; the report renders the locked tariff table; the reference case is migrated.

**Verify**: `just lint && just typecheck && just test` green; `uv run booping-bench run --case fastify-naming-lesson --reps 1` then `uv run booping-bench report <run-id>` shows the `score` column and the tariff table per the I/O contract.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | expect.yaml schema v2 in the loader: common keys become `{id, kind, dimension}` + exactly one of `penalty` or `penalty_each`+`cap` (both int); `weight` rejected with `weight removed — use penalty (docs/case-backlog.md tariff)`; `judge` stays reserved-passthrough but must carry valid penalty keys | `src/booping_bench/case.py`, `tests/case_test.py` | 2 | done |
| 1.2 | `CheckResult` gains `occurrences: int`: `file_regex` w/ `absent` = count of matches; `bash_call`/`forbidden_tool` = count of matching calls; `file_regex` present-mode / `frontmatter` / `command` = 0 or 1 | `src/booping_bench/checks.py`, `tests/checks_test.py` | 2 | done |
| 1.3 | Scoring: per failed check, points = `penalty` or `min(cap, occurrences × penalty_each)`; assemble `deductions: [{check, points, evidence}]`, `score = max(0, 100 − Σ)`; `scores{}` floats re-derived as points-kept ratio per dimension; `RECORD_KEYS` += `score`, `deductions` | `src/booping_bench/scoring.py`, `tests/scoring_test.py` | 2 | done |
| 1.4 | Report v2 per locked I/O contract: `score` column (mean ± spread) leads the dimension table; per-check table becomes the tariff table (`check | dim | tariff | hit rate | mean lost | evidence (last failure)`); exit 1 on legacy records; regenerate golden fixtures | `src/booping_bench/report.py`, `tests/report_test.py`, `tests/fixtures/report_sample.jsonl`, `tests/fixtures/report_expected.golden` | 2 | done |
| 1.5 | Migrate `cases/fastify-naming-lesson/expect.yaml` to the standard tariff (lesson −15, sketch identifiers −5 each cap −20, protocol −10 each, overreach −5 each cap −20, outcome −20); update bench `README.md` (expect.yaml section + check-kind snippets), `CLAUDE.md` data contracts (expect schema, record schema, report shape), and `docs/case-backlog.md` scoring header (spec → shipped); 1-rep calibration probe | `cases/fastify-naming-lesson/expect.yaml`, `README.md`, `CLAUDE.md`, `docs/case-backlog.md` | 2 | done |

#### Task 1.1 DoD
- [x] v2 check parses; `weight` key exits 1 naming the file + key; missing/double penalty keys exit 1.
- [x] `penalty_each` without `cap` (and vice versa) rejected.
- [x] Reserved `judge` entry with penalty keys still parses with `reserved=True`.

#### Task 1.2 DoD
- [x] Each kind's occurrence semantics covered by a test (multi-match `absent` file, repeated forbidden calls).
- [x] Passing checks report `occurrences` consistent with pass (no phantom counts).

#### Task 1.3 DoD
- [x] `score` reconstructable by hand from `deductions[]` in the test fixture.
- [x] Cap honored: occurrences × penalty_each above cap deducts exactly cap.
- [x] Dimension with no deductions scores 1.0; untouched dimensions omitted as today.

#### Task 1.4 DoD
- [x] Golden test matches the locked format byte-for-byte (spread suppressed on single rep, as today).
- [x] Legacy record (no `score`) → exit 1 with the run-id and a re-run hint on stderr.

#### Task 1.5 DoD
- [x] `run --case fastify-naming-lesson --dry-run` passes; 1 live rep produces a record whose `score` + `deductions` match its check outcomes.
- [x] No `weight:` remaining anywhere under `cases/`; README/CLAUDE.md/case-backlog carry no weighted-ratio references.

---

### M2: typer fixture + P2 buried-linter-break case — 5 SP | done

**Goal**: second stack + second develop case, fully deterministic: a lint break buried under noise commits in a file the plan doesn't touch; the seeded lesson mandates fixing it.

**Verify**: `uv run booping-bench run --case typer-buried-linter --reps 3` completes; `report <run-id>` shows all dimensions populated; calibration comment recorded in `case.yaml`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `fixtures/typer.yaml` (url `https://github.com/fastapi/typer`, pin `0.26.8` — verified current 2026-07-09; `commands`: lint/typecheck/test as they exist at the pin) + `build.sh`: clone pin, install dev deps offline-ready, inject an unused `import string` at the top import block of `typer/utils.py` (ruff F401 — deterministic, tests untouched; deviates from the backlog's annotation-delete recipe for ruff determinism), commit, then 5 noise commits (README/docs edits) on top | `fixtures/typer.yaml`, `cases/typer-buried-linter/build.sh`, `cases/typer-buried-linter/case.yaml` | 2 | done |
| 2.2 | Vault seed: small `ready-for-dev` develop plan touching an unrelated module, lesson `run the linter during execution; fix errors you encounter`, `_booping/agent_booping-developer.md` extension, `answers.yaml` (specific patterns first, generic proceed fallback, every pattern duplicated) | `cases/typer-buried-linter/vault/**`, `cases/typer-buried-linter/answers.yaml` | 1 | done |
| 2.3 | `expect.yaml` on the standard tariff: `command` lint exit 0 (−20 outcome), `file_regex` `absent` on the injected `^import string$` in `typer/utils.py` (−5 judgment), protocol transition checks (−10 each), overreach scope + commit-cap checks (−5 each cap −20); calibrate: dry-run → 1 rep → 3 reps, record calibration block | `cases/typer-buried-linter/expect.yaml`, `cases/typer-buried-linter/case.yaml` | 2 | done |

#### Task 2.1 DoD
- [x] Two consecutive builds produce identical `git log` (determinism test pattern from `fixture_test.py`).
- [x] Lint at the pin fails only on the injected break; test suite at the pin is green.

#### Task 2.2 DoD
- [x] `run --case typer-buried-linter --dry-run` exits 0.
- [x] Plan frontmatter carries `commit: __PRE_DRIFT_SHA__`; placeholder resolves in the built vault.
- [x] Seeded prompt-bearing artifacts (lesson, `_booping/` extension, plan body) pass the lesson-0004 four-check IA pass.

#### Task 2.3 DoD
- [x] Every check verified to pass/fail for a real reason on the 1-rep probe transcript (calibration checklist step 2).
- [x] 3-rep report read; tariff untouched by calibration (patterns/answers/timeout only).

---

### M3: G4 groom case — CLAUDE.md convention in the plan — 5 SP | done

**Goal**: first groom case, zero judge dependency: repo CLAUDE.md mandates a `_spec` filename suffix for new test files; the groomed plan's Files/sketch must honor it.

**Verify**: `uv run booping-bench run --case typer-groom-claudemd-convention --reps 3` completes; `report <run-id>` populated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Case dir on the typer fixture: `build.sh` reuses the pin + injects a repo `CLAUDE.md` mandating the `_spec` suffix convention for new test files; vault seed with empty `plans/`; `case.yaml` prompt = `/booping:groom <brief asking for new tests for a named module>`; `answers.yaml` scripts groom's question flow through explicit approval (`looks good`), patterns duplicated | `cases/typer-groom-claudemd-convention/{build.sh,case.yaml,answers.yaml,vault/**}` | 3 | done |
| 3.2 | `expect.yaml`: `file_regex` on `vault/plans/*.md` — convention-B (`_spec`) path present (−15 judgment), convention-A form absent (−5 each cap −20); `frontmatter` status `ready-for-dev` after scripted approval (−10 protocol); `bash_call` transition evidence (−10 protocol); calibrate 1 rep → 3 reps | `cases/typer-groom-claudemd-convention/expect.yaml`, `case.yaml` | 2 | done |

#### Task 3.1 DoD
- [x] Dry-run exits 0; groom reaches plan draft + approval in the 1-rep probe without an unscripted-question abort.
- [x] Brief does not leak the convention (the signal must come from repo CLAUDE.md only).

#### Task 3.2 DoD
- [x] `file_regex` glob resolves the groom-created plan file (name unknown at authoring).
- [x] 3-rep calibration recorded in `case.yaml`.

---

### M4: `judge` check kind — 5 SP | done

**Goal**: `judge` executes: rubric items scored binary by haiku via the Agent SDK, feeding `penalty_each`+`cap`.

**Verify**: `just test` green (SDK mocked); a live 1-rep run of M5's case (or a judge smoke check added to an existing case run) produces a judge deduction with per-item evidence.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Un-reserve `judge` in the loader: params `target ∈ {file, transcript}`, `path` required iff `target: file`, `rubric` non-empty list of strings; unknown params rejected | `src/booping_bench/case.py`, `tests/case_test.py` | 1 | done |
| 4.2 | Executor `judge.py`: extend `score_case`/`run_check` signature with a `transcript: Path` param (`_exec_rep` passes `out_dir/transcript.jsonl`); `target: file` reads glob content from scratch, `target: transcript` extracts role-prefixed text blocks from the transcript JSONL; assemble artifact + rubric into one prompt; single `claude-agent-sdk` query via `asyncio.run()` (checks are sync; `run_skill`'s loop is closed by score time), model `claude-haiku-4-5-20251001`, no tools; verdict contract enforced: prompt demands raw JSON `{item_index: pass|fail}` with no code fences, parser strips fences defensively, one corrective retry appending the parse error, then the check fails with raw output as evidence; `occurrences` = failed items, evidence = failed item texts; register in `_HANDLERS`; delete `JudgeNotImplemented` + `JUDGE_PLAN`; tests with mocked SDK (pass/fail/fenced-output/parse-retry/error paths) | `src/booping_bench/judge.py`, `src/booping_bench/checks.py`, `src/booping_bench/scoring.py`, `src/booping_bench/cli.py`, `tests/judge_test.py`, `tests/checks_test.py` | 3 | done |
| 4.3 | Docs: README check-kind reference gains a working `judge` snippet (reserved note removed); `CLAUDE.md` data contracts updated; `docs/case-backlog.md` kind roll-up note updated | `README.md`, `CLAUDE.md`, `docs/case-backlog.md` | 1 | done |

#### Task 4.1 DoD
- [x] `target: file` without `path` exits 1; empty rubric exits 1; `target: transcript` with `path` exits 1.

#### Task 4.2 DoD
- [x] Mocked tests cover: all-pass, partial-fail (occurrences + evidence correct), malformed-then-valid retry, hard SDK error → check fails, rep survives.
- [x] No `JudgeNotImplemented` reference remains in src or tests.

#### Task 4.3 DoD
- [x] README snippet round-trips through the loader (copy-paste parses).

---

### M5: G1 groom case — test-checklist coverage on fastify — 5 SP | done

**Goal**: groom case scoring checklist recall: `build.sh` deletes one fastify module's test file; the groomed plan must preserve that coverage; `judge` grades recall per checklist item.

**Verify**: `uv run booping-bench run --case fastify-groom-test-checklist --reps 3` completes; `report <run-id>` shows judge deductions with per-item evidence.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Case dir: `build.sh` clones the fastify pin, deletes `test/reply-code.test.js` (self-contained reply status-code behaviors — verified present at v5.10.0); brief asks groom to plan a rework of reply status-code handling; checklist manually extracted from the deleted test's cases into `expect.yaml` rubric items; vault seed + `answers.yaml` through approval | `cases/fastify-groom-test-checklist/{build.sh,case.yaml,answers.yaml,vault/**}` | 3 | done |
| 5.2 | `expect.yaml`: `judge` `target: file` on `vault/plans/*.md`, rubric = checklist items, −5 each missed, cap −40 (coverage dimension); deterministic protocol checks as in M3; calibrate — verify judge verdict stability across the 3 reps and per-item evidence sanity | `cases/fastify-groom-test-checklist/expect.yaml`, `case.yaml` | 2 | done |

#### Task 5.1 DoD
- [x] Rubric items are behaviors ("covers rejection of duplicate header"), not test names — judgeable against a plan.
- [x] Dry-run exits 0.

#### Task 5.2 DoD
- [x] 1-rep probe: each judge item verdict matches a human read of the plan.
- [x] 3-rep calibration recorded; judge flakiness (item verdicts flipping across reps) noted in the calibration block if observed.

---

### M6: Compare/delta report — 3 SP | done

**Goal**: `booping-bench report <run-a> --compare <run-b>` renders the locked delta format.

**Verify**: two runs of the same case compared render the arrow-cell table; comparing runs with mismatched rep counts exits 1 naming both counts.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `--compare <run-b>` flag: load both JSONL, match groups by `(case, model, tag)`; per matched group one row, cells `a → b (Δ)` for score, dimensions, metrics per the locked I/O contract; unmatched groups listed under the table; mismatched rep counts in a matched group → stderr + exit 1; golden test | `src/booping_bench/report.py`, `src/booping_bench/cli.py`, `tests/report_test.py`, `tests/fixtures/*` | 3 | done |

#### Task 6.1 DoD
- [x] Golden compare fixture matches the locked format.
- [x] Δ formatting: score/tokens as signed ints, dimensions/cost signed 2-decimals, zero rendered `(0)`.
- [x] `--compare` with `--out` writes the compare report to the file.

---

### M7: Parallel container orchestration — 3 SP | done

**Goal**: `run --parallel N` executes reps concurrently under API-key auth.

**Verify**: `ANTHROPIC_API_KEY=... uv run booping-bench run --case fastify-naming-lesson --reps 3 --parallel 3` completes with 3 records; without the key, `--parallel 2` exits 2 before any container starts.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | `--parallel N` (default 1 → today's sequential path unchanged): ThreadPoolExecutor over reps, each rep keeps its own container + temp out-dir; container collision surface is already clean — names unique per rep (`bench-{run_id}-r{rep}`), no `-p` port mappings anywhere; main thread appends records to `results/<run-id>.jsonl` as futures complete; N>1 without `ANTHROPIC_API_KEY` → exit 2 with actionable message; timeout/kill semantics preserved per rep; tests with mocked subprocess (concurrency, record count, auth guard) | `src/booping_bench/cli.py`, `tests/smoke_test.py`, `tests/cli_test.py` | 3 | done |

#### Task 7.1 DoD
- [x] `--parallel 1` path byte-identical behavior to today (existing tests untouched).
- [x] 3 parallel mocked reps yield 3 distinct records, rep numbers 1..3, no interleaved/corrupt JSONL lines.
- [x] `--help` documents the flag + auth requirement.

---

## I/O contract

- **Arguments / flags**: `booping-bench run --case <name> [--reps N] [--model M] [--booping-ref R] [--tag T] [--parallel N] [--dry-run]`; `booping-bench report <run-id> [--compare <run-id-b>] [--out PATH]`.
- **stdin**: unused.
- **stdout**: markdown reports only (single-run and compare); `run` progress lines stay on stderr as today.
- **stderr**: diagnostics + all errors.
- **Exit codes**: `0` success; `1` user error (unknown case/run-id, contract violation, legacy records, mismatched compare rep counts); `2` auth (no credentials; `--parallel` >1 without `ANTHROPIC_API_KEY`).

**Single-run report v2 (locked 2026-07-09)** — per case: dimension table with leading `score` column, then the tariff table replacing the pass-rate table:

```markdown
## fastify-naming-lesson

| model / tag | score | protocol | judgment | overreach | outcome | tokens_in | ... |
|---|---|---|---|---|---|---|---|
| opus / hacks-off | 78 ±5 | 1.00 | 0.62 | 1.00 | 0.80 | 412k | ... |

| check | dim | tariff | hit rate | mean lost | evidence (last failure) |
|---|---|---|---|---|---|
| judgment-snake-case | judgment | -15 | 2/3 | -10.0 | lib/request-context.js:12 getRequestId( |
| overreach-scope | overreach | -5 each, cap -20 | 0/3 | 0 | |
```

**Compare report (locked 2026-07-09)** — one row per matched `(case, model, tag)` group, inline arrow cells; unmatched groups listed below; mismatched rep counts → exit 1:

```markdown
# Compare: 20260710-0900-x (A) vs 20260711-1400-x (B)

## fastify-naming-lesson

| model / tag | score | judgment | outcome | tokens_out | cost_usd |
|---|---|---|---|---|---|
| opus / base | 78 → 85 (+7) | 0.62 → 0.75 (+0.13) | 0.80 → 0.80 (0) | 31k → 28k (-3k) | 4.10 → 3.80 (-0.30) |
```

## Final Verification

- [x] `just lint && just typecheck && just test` green in the bench repo.
- [x] All four cases pass `--dry-run`; each new case has a recorded calibration block.
- [x] Live probe: 1 rep of `fastify-naming-lesson` post-migration; report renders both locked formats.
- [x] Failure paths verified: legacy-record report → 1; mismatched compare → 1; `--parallel 2` keyless → 2.
- [x] `--help` reflects `--compare` and `--parallel`.

## Out of scope

- Third fixture stack (zustand — P4/P5) and remaining problem-library cases (P3, P6–P10).
- Groom scenarios G2 (unbounded failure mode), G3 (output-format lock), G5 (acknowledged-lesson gate).
- Per-check judge model override / judge model config surface.
- Legacy-record back-compat in report v2.
- Parallelism across cases (only reps within a run).

## CLAUDE.md impact

Bench repo `CLAUDE.md`: Data contracts section rewritten for expect.yaml v2 (penalty keys, judge params), record schema (`score`, `deductions[]`), and both locked report shapes; CLI notes gain `--compare` + `--parallel` (M1.5 / M4.3 / M6 / M7 carry these edits). Plugin repo `CLAUDE.md`: no changes required — bench repo is externally documented via its own CLAUDE.md/README.
