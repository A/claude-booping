---
title: Benchmark framework core (claude-booping-bench) + develop reference case
type: feature
status: done
sp: 35
split_from: null
created: 2026-07-09 00:00
planned: 20260708 20:17
started: 20260708 20:20
completed: 2026-07-08 21:51
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "Score-based benchmark harness: docker runner, Agent SDK driver, deterministic
  scoring, fastify develop case"
commit: c6830c41a6bf9f545c3f90325803276786e689d8
sessions:
- 3135c084-871e-4681-860b-807c422a3b65
metrics_active_minutes: 144
metrics_models:
- claude-fable-5
metrics_tokens_input: 81601
metrics_tokens_output: 453110
metrics_tokens_cache_creation: 4372533
metrics_tokens_cache_read: 39623656
---

# Benchmark framework core (claude-booping-bench) + develop reference case

## Context

booping skills (rendered prompts) have no behavioral regression harness — template edits are verified only by render-layer tests in `booping-python/`. This plan creates **`claude-booping-bench`**, a private repo with a score-based benchmark framework: it runs booping skills headlessly against fixture OSS repos with injected faults, captures tool calls and side effects, scores them across dimensions, and emits per-run reports. Benchmarks are **score-based, not pass/fail** — used to compare models in orchestrator roles, and to measure quality/token deltas across booping prompt changes (e.g. the planned prompt-hacks split, see `notes/20260709-prompt-hacks-split.md`).

Priority order (user-set): extendible, simple framework first; exact benchmark cases second. One OSS fixture repo (fastify) and one develop-skill reference case in scope — the case exists to prove the pipeline end-to-end and to serve as the reference for authoring further cases cheaply.

Split: judge-based checks, the groom reference case, and compare/delta reports live in the sibling plan `plans/20260709-benchmark-judge-groom-case-reports.md` (13 SP, backlog).

## Decisions

- **Separate private repo `claude-booping-bench`**: keeps heavy fixtures and answer scripts out of the plugin repo and out of public training data (public benchmarks get scraped → future models memorize them → benchmark dies).
- **Agent SDK over raw `claude -p`**: the Python `claude-agent-sdk` wraps the claude CLI (same auth, same billing) but adds `PostToolUse` hooks (tool-call capture for assertions) and `canUseTool` (scripted `AskUserQuestion` answers). Skills are question-dense; scripted answers test the interaction points instead of bypassing them. No non-interactive mode is added to booping skills.
- **Docker isolation**: a container gets a *generated minimal* `~/.claude` (credentials mounted read-only or API key via env; booping plugin registered from a read-only mount). Never mount the user's real `~/.claude` — personal CLAUDE.md/hooks/settings would pollute runs.
- **Copy-on-run**: fixture repo and vault are built/copied into container scratch per rep; mounts are read-only; reps never see each other's mutations.
- **Fixtures are build scripts, not stored repos**: each fixture is a pinned upstream sha + a deterministic `build.sh` (fixed git author/dates) that manufactures history and injections. No nested `.git` checked in.
- **Deterministic checks only in this plan**: check kinds `bash_call`, `file_regex`, `frontmatter`, `forbidden_tool`, `command`. The `judge` kind (LLM rubric) is reserved in the schema but implemented in the sibling plan.
- **Scoring**: fixed dimensions `protocol`, `judgment`, `overreach`, `outcome` (sibling adds `coverage`). Each check carries `dimension` + `weight`; dimension score = Σ(passed·weight)/Σ(weight), range 0..1. Headline never replaces the per-dimension breakdown.
- **Run labeling via `--tag`**: freeform label recorded in results (e.g. `hacks-off`, `glm-4.7-trial`) instead of benchmark-specific flags — keeps the runner generic; behavior variants come from the case vault's `config.yaml` override and `--booping-ref`.
- **Auth pluggable**: mounted OAuth credentials (subscription limits, cheap local runs) or `ANTHROPIC_API_KEY` env (CI / parallel). Runner takes whichever is provided.
- **Runner stack**: Python uv project mirroring `booping-python` conventions (ruff, basedpyright, pytest, justfile). Console script `booping-bench`.

## Architecture

```
host: booping-bench run --case fastify-naming-lesson --reps 3 --model <id> --booping-ref <ref>
  └─ per rep: docker run (mounts: creds ro | plugin repo ro | case dir ro)
       └─ entrypoint: generate ~/.claude (register plugin) → build fixture into scratch
            → seed vault + .booping marker → booping-bench exec-rep (in-container)
                 └─ claude-agent-sdk query("/booping:develop plans/<plan>.md")
                      • PostToolUse hook → captured tool calls (JSONL)
                      • canUseTool → answers.yaml scripted responses
            → score scratch state + captured calls against expect.yaml
            → write rep record JSON + transcript to the rw /out mount
  └─ host reads /out, appends records to results/<run-id>.jsonl, moves transcripts to transcripts/<run-id>/
booping-bench report <run-id> → markdown table (stdout)
```

The same package runs on host (orchestrates containers, sequential in this plan) and in-container (`exec-rep` internal subcommand).

### Data contracts (locked with user 2026-07-09)

**Case directory** — adding a case or fixture repo must require only these files, no framework changes:

```
cases/<case-name>/
  case.yaml        # skill: develop|groom; fixture: <name>; description; timeout_s; reps_default; prompt (skill invocation line)
  build.sh         # deterministic: clone pinned sha → inject faults → manufacture history → emit repo into $SCRATCH/repo
  vault/           # complete vault seed: plans/, lessons/, _booping/, optional config.yaml override
  answers.yaml     # ordered list: {match: <regex on question text>, answer: <option label or free text>}
  expect.yaml      # checks + scoring (below)
fixtures/<name>.yaml # shared per-repo: upstream url, pinned sha/tag, tooling commands (lint, test)
```

**expect.yaml**:

```yaml
checks:
  - id: <slug>
    kind: bash_call | file_regex | frontmatter | forbidden_tool | command   # `judge` reserved (sibling plan)
    # bash_call:      pattern (regex over captured Bash commands), optional min/max occurrence
    # file_regex:     path (glob within scratch), pattern, optional absent: true
    # frontmatter:    path (plan file), key, equals
    # forbidden_tool: tool (name), optional arg_pattern — any match fails the check
    # command:        run (shell, cwd=scratch), expect_exit (default 0), optional stdout_pattern
    dimension: protocol | judgment | overreach | outcome
    weight: <int>
```

**Result record** (one JSONL line per rep, append-only `results/<run-id>.jsonl`):

```json
{"run_id": "...", "case": "...", "skill": "develop", "model": "...", "booping_ref": "...",
 "tag": "...", "rep": 1,
 "scores": {"protocol": 1.0, "judgment": 0.66, "overreach": 1.0, "outcome": 0.8},
 "checks": {"<check-id>": true},
 "metrics": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "turns": 0, "tool_calls": 0, "wall_s": 0},
 "session_id": "...", "transcript": "transcripts/<run-id>/<case>-r1.jsonl"}
```

**Report** (`booping-bench report <run-id>`, markdown to stdout): per case, one table — rows = model/tag combos, columns = the four dimensions as `mean ± spread` over reps, then `tokens_in`, `tokens_out`, `cost_usd`, `turns`; below it a per-check table (check id × pass-rate across reps). Compare/delta mode is out of scope (sibling plan).

## Milestones

### M1: Bench repo scaffold — 2 SP | done

**Goal**: `claude-booping-bench` exists as a private GitHub repo with a working uv project skeleton and quality tooling.

**Verify**: `just lint && just typecheck && just test` all green in the new repo; `gh repo view A/claude-booping-bench --json visibility` reports `PRIVATE`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Create private repo `A/claude-booping-bench` (`gh repo create`). Scaffold uv project `booping_bench` mirroring `booping-python` conventions: `pyproject.toml` (runtime deps `pyyaml`, `python-frontmatter`; ruff, basedpyright, pytest dev-deps; console script `booping-bench`), `justfile` (`lint`, `typecheck`, `test`, `build-image`), package stub `src/booping_bench/__init__.py`, empty dirs `cases/`, `fixtures/`, `results/`, `transcripts/` (gitignored), seed `CLAUDE.md` describing layout + conventions | `pyproject.toml`, `justfile`, `src/booping_bench/__init__.py`, `CLAUDE.md`, `.gitignore` | 2 | done |

#### Task 1.1 DoD

- [x] `uv run booping-bench --help` exits 0 and prints subcommand list (stubs acceptable).
- [x] `just lint`, `just typecheck`, `just test` pass (empty test suite counts).
- [x] Repo is private on GitHub; `results/` contents and `transcripts/` are gitignored (keep `.gitkeep`).
- [x] `CLAUDE.md` documents the case/fixture directory contract from this plan's Data contracts section.

---

### M2: Docker runtime — 7 SP | done

**Goal**: a container image + entrypoint that runs the claude CLI with the mounted booping plugin registered, isolated from the host user's config.

**Verify**: `docker run --rm -v <booping-repo>:/plugin:ro -e ANTHROPIC_API_KEY=... booping-bench:dev claude --version` exits 0; `docker run ... claude -p "reply PONG" --output-format json` returns a result envelope; a probe run confirms the booping plugin's skills are listed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `Dockerfile`: node LTS base + python 3.12 + uv + git + jq; install claude CLI (`@anthropic-ai/claude-code`, version pinned via build arg after verifying current release); copy `booping_bench` package; non-root user | `Dockerfile`, `justfile` (`build-image`) | 2 | done |
| 2.2 | Entrypoint: generate minimal `$HOME/.claude` at container start — fresh `settings.json` registering the plugin from `/plugin` mount, no other config; auth wiring: mount `credentials` file read-only OR `ANTHROPIC_API_KEY` env passthrough, fail fast with a clear stderr message when neither present (exit 2). Verify the exact plugin-registration mechanism for local paths against current Claude Code docs during implementation and record it in the bench `CLAUDE.md` | `docker/entrypoint.sh`, `src/booping_bench/container.py` | 4 | done |
| 2.3 | Mount + scratch contract: `/plugin` ro, `/case` ro, creds ro; scratch workdir on container tmpfs (`/scratch`) where fixture repo + vault land; nothing writes to any mount except the single rw output mount `/out` (rep record JSON + transcript). Host launches containers with `--user <host-uid>:<host-gid>` so `/out` files are host-owned — no root-owned artifacts | `docker/entrypoint.sh`, `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] `just build-image` builds `booping-bench:dev` cleanly.
- [x] `docker run --rm booping-bench:dev claude --version` prints the pinned version.
- [x] Pinned claude CLI version recorded in `Dockerfile` build arg (verified against current npm release at implementation time).

#### Task 2.2 DoD

- [x] Container with `ANTHROPIC_API_KEY` runs `claude -p "reply PONG" --output-format json` → valid JSON result envelope.
- [x] Container with mounted OAuth credentials achieves the same (documented invocation in `CLAUDE.md`).
- [x] Booping skills resolvable in-container (probe: plugin skill listed / loadable).
- [x] No file from host `~/.claude` other than the credentials file is visible in-container.
- [x] Missing auth → exit 2 with actionable stderr message.

#### Task 2.3 DoD

- [x] All mounts read-only except `/out`; a write attempt to `/plugin` or `/case` fails.
- [x] Rep artifacts (result JSON, transcript) appear under `/out` only, owned by the host uid (verified with `stat` after a probe run).

---

### M3: Runner core — 9 SP | done

**Goal**: `booping-bench run` executes a case end-to-end — loads case, builds fixture, drives the skill via Agent SDK with scripted answers, persists captured calls + transcript.

**Verify**: `uv run booping-bench run --case <ref-case> --dry-run` validates case + builds fixture without invoking claude (exit 0); driver unit tests green with a mocked SDK.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Case loader: parse + validate `case.yaml`, `fixtures/<name>.yaml`, `answers.yaml`, `expect.yaml` against the Data contracts; unknown keys / unknown check kinds → exit 1 with the offending path + key named on stderr | `src/booping_bench/case.py`, `tests/case_test.py` | 2 | done |
| 3.2 | Fixture builder: execute `build.sh` with a controlled env (`GIT_AUTHOR_*`, `GIT_COMMITTER_*`, fixed dates exported; `$SCRATCH` set), verify it produced `$SCRATCH/repo` with a git history; copy `vault/` to `$SCRATCH/vault`, write `.booping` marker (`project_name` + `vault_path`) pointing at it; init vault git repo | `src/booping_bench/fixture.py`, `tests/fixture_test.py` | 2 | done |
| 3.3 | SDK driver: `claude-agent-sdk` (PyPI, pin current version at implementation) `query()` invoking `case.yaml`'s `prompt` (e.g. `/booping:develop plans/<plan>.md`), cwd=`$SCRATCH/repo`; `PostToolUse` hook appends every tool call (name + input) to a captured-calls JSONL; `canUseTool` answers `AskUserQuestion` from `answers.yaml` — entries are ordered and single-use: first unconsumed entry whose regex matches the question text wins and is consumed; no match → record + fail rep with exit 3 "unscripted question"; persist full transcript + result envelope (tokens, cost, turns, session_id) to `/out` | `src/booping_bench/driver.py`, `tests/driver_test.py` | 4 | done |
| 3.4 | `run` CLI: `booping-bench run --case <name> [--model <id>] [--booping-ref <git-ref>] [--reps N] [--tag <label>] [--dry-run]`; container orchestration via `subprocess.run(["docker", "run", ...])` — no docker PyPI dependency; sequential reps, each in a fresh container (checkout of `--booping-ref` into a temp plugin dir when given, else the mounted plugin as-is); **timeout enforced host-side**: `case.yaml`'s `timeout_s` as the subprocess timeout, on expiry `docker kill` the container and mark the rep `timeout: true` (an in-container SDK hang cannot defeat it); `--dry-run` stops after fixture build; reads rep records from `/out`, appends to `results/<run-id>.jsonl` (run-id: `<date>-<slug>`) | `src/booping_bench/cli.py` | 1 | done |

#### Task 3.1 DoD

- [x] Valid reference-shaped case parses; each contract violation (bad kind, missing file, malformed answers) exits 1 with a specific message.
- [x] Unit tests cover happy path + 3 malformed inputs.

#### Task 3.2 DoD

- [x] Two consecutive builds of the same fixture produce identical `git log --format=%H` output (determinism).
- [x] `.booping` marker resolves the scratch vault (`booping render-sprints` equivalent path check).

#### Task 3.3 DoD

- [x] Captured-calls JSONL contains every Bash invocation from a scripted probe run (mock-SDK unit test).
- [x] Unscripted `AskUserQuestion` fails the rep with exit 3 and the question text on stderr; consumed entries are not reused (unit test with two identical questions).

#### Task 3.4 DoD

- [x] `--dry-run` exits 0 without invoking claude; `--reps 2` produces 2 records in one JSONL file.
- [x] `--booping-ref` runs against a clean checkout of that ref (verified by a probe reading the plugin path).
- [x] Host-side timeout kills a deliberately-hung container (probe with `sleep`) and records `timeout: true`.
- [x] Exit codes: 0 = all reps executed; 1 = user error (unknown case/flag); 2 = internal/env error; 3 = rep aborted (unscripted question / timeout) — recorded per rep, run continues remaining reps.

---

### M4: Scoring engine + result records — 4 SP | done

**Goal**: post-run scratch state + captured calls are scored against `expect.yaml` into dimension scores and a result JSONL record.

**Verify**: `just test` — scoring unit tests cover all five kinds against synthetic scratch/calls fixtures, including weight math and the `absent`/`max`/`expect_exit` variants.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Check kinds `bash_call`, `file_regex`, `frontmatter`, `forbidden_tool`, `command` per the Data contracts; each returns pass/fail + evidence string (matched line / command output snippet) stored in the rep record; `judge` kind parses but exits 1 "not implemented — see sibling plan" if used | `src/booping_bench/checks.py`, `tests/checks_test.py` | 3 | done |
| 4.2 | Dimension scoring (Σ passed·weight / Σ weight per dimension; dimension absent from checks → omitted from record, never 0) + result-record assembly per the Data contracts + JSONL append | `src/booping_bench/scoring.py`, `tests/scoring_test.py` | 1 | done |

#### Task 4.1 DoD

- [x] Each kind has ≥2 unit tests (pass + fail path); `command` honors `expect_exit` and `stdout_pattern`; `file_regex` honors `absent: true`; `bash_call` honors `min`/`max`.
- [x] Evidence string present on every failed check in the record.

#### Task 4.2 DoD

- [x] Weight math verified against a hand-computed fixture.
- [x] Emitted record validates against the Data-contracts JSON shape (schema test).

---

### M5: Develop reference case (fastify) — 8 SP | done

**Goal**: `cases/fastify-naming-lesson/` runs end-to-end and scores the lesson-vs-plan naming conflict + ambient stale-commit drift; serves as the authoring reference.

**Verify**: `uv run booping-bench run --case fastify-naming-lesson --reps 3 --model <default>` completes ≥2/3 reps without exit-3 aborts; `results/<run-id>.jsonl` holds records with all four dimensions populated.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Fastify fixture: `fixtures/fastify.yaml` (upstream url, pin current release tag at implementation, `npm test`/lint commands); `build.sh` clones the pin, then injects exactly 3 drift commits with fixed authors/dates: (1) append one sentence to `README.md`, (2) add `docs/benchmark-note.md` with one sentence, (3) append one comment line to `.gitignore`. No drift commit touches `lib/` or `test/` (where the plan's Files point) — `npm test` must stay green after all three | `fixtures/fastify.yaml`, `cases/fastify-naming-lesson/build.sh` | 2 | done |
| 5.2 | Vault seed: reference plan (small — 1 milestone, 2 tasks: add a helper module + its unit test to fastify, camelCase identifiers in the plan's code sketch and Files column), `commit:` set to the pre-drift sha by `build.sh`; lesson `lessons/1_snake-case-identifiers.md` (all new JS identifiers snake_case, with reason); minimal `_booping/agent_booping-developer.md` naming node/npm stack | `cases/fastify-naming-lesson/vault/**`, `build.sh` (commit-sha interpolation) | 2 | done |
| 5.3 | `case.yaml` (skill: develop, prompt, timeout, reps_default 3), `answers.yaml` (plan selection, grouping confirm, branch confirm, drift acknowledgement), `expect.yaml`: protocol — entry+exit transitions via `frontmatter` + `bash_call` on `booping transition`, vault-commit check; judgment — `file_regex` new files use snake_case, `absent` camelCase in new code; drift handled without revalidate question (`bash_call` absence of full-range diff); overreach — `forbidden_tool` Edit on pre-existing fastify files outside plan scope, commit-count `max`; outcome — `command` node test invocation for the new unit test exits 0 | `cases/fastify-naming-lesson/case.yaml`, `answers.yaml`, `expect.yaml` | 1 | done |
| 5.4 | Calibration: run `--reps 3` on the default model. Weights stay fixed as authored in 5.3. Calibration may adjust only `answers.yaml` regexes, `timeout_s`, and expect *patterns* — and a pattern may change only when the transcript shows the check failed for pattern-noise reasons (regex too strict / wrong path glob), never to make a legitimately-failed check pass. Document per-rep cost + wall time in `case.yaml` comments | case files above, `results/` (gitignored) | 3 | done |

#### Task 5.1 DoD

- [x] Fixture build deterministic (identical history across two builds).
- [x] `npm test` baseline passes on the pinned tag inside the container.

#### Task 5.2 DoD

- [x] Plan validates against booping's frontmatter shape (`booping render-sprints` runs clean on the seeded vault).
- [x] `commit:` lands on the pre-drift sha automatically during build.
- [x] Seeded lesson + `_booping/agent_booping-developer.md` pass the four-check IA pass (lesson 0004: scoping, duplication, configurability, hierarchy) — recorded as a one-line note per file in the case README section.
- [x] The seeded plan's task DoDs bound the worker's return shape (lesson 0007) — report format stated in the plan, not left to the worker.

#### Task 5.3 DoD

- [x] Every check maps to one of the four dimensions; weights sum documented in a comment per dimension.
- [x] `answers.yaml` covers every `AskUserQuestion` the develop skill can raise on this path (plan pick, grouping, branch, drift) — no unscripted-question aborts in dry calibration.

#### Task 5.4 DoD

- [x] ≥2/3 calibration reps complete without exit-3 aborts.
- [x] All four dimensions populated in every completed rep record.
- [x] Per-rep cost and wall time recorded in `case.yaml` comments.

---

### M6: Run report — 2 SP | done

**Goal**: `booping-bench report <run-id>` renders the locked markdown report from a results JSONL.

**Verify**: `uv run booping-bench report <calibration-run-id>` prints the per-case dimension table (mean ± spread) + per-check pass-rate table; unit test diffs report output against a fixture JSONL.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `report` subcommand: read `results/<run-id>.jsonl`, group by (case, model, tag), render dimension table (mean ± min/max spread over reps) + metrics columns + per-check pass-rate table, markdown to stdout; `--out <path>` writes file; unknown run-id → exit 1 | `src/booping_bench/report.py`, `src/booping_bench/cli.py`, `tests/report_test.py` | 2 | done |

#### Task 6.1 DoD

- [x] Report renders columns exactly per Data contracts (dimensions, tokens_in, tokens_out, cost_usd, turns).
- [x] Spread shown as `mean ± (max−min)/2` over reps; single-rep groups render without spread.
- [x] Fixture-based output diff test green.

---

### M7: Authoring docs + extensibility validation — 3 SP | done

**Goal**: a new case or fixture repo is authorable from the README alone; the check vocabulary is desk-validated against the full future-case backlog.

**Verify**: README walkthrough cross-checked against the actual `fastify-naming-lesson` files (no undocumented steps); appendix table maps every backlog case to concrete check kinds with zero framework changes required.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | `README.md` in the bench repo: quickstart (auth, build image, run reference case, read report), case-authoring guide (each contract file, check-kind reference with one example per kind, answers-script guide, calibration checklist), fixture-adding guide | `README.md` | 2 | done |
| 7.2 | Extensibility desk-check: for each case in this plan's Appendix, record in `docs/case-backlog.md` the target skill, fixture shape, and the check kinds it needs; any case needing a new kind is flagged with the proposed kind (expected: only `judge`, already reserved). Add one line to the booping repo's `CLAUDE.md` Layout section pointing at `claude-booping-bench` (private) as the benchmark harness | `docs/case-backlog.md` (bench repo), `<booping-repo>/CLAUDE.md` | 1 | done |

#### Task 7.1 DoD

- [x] A reader can author a new case using only README + reference case (walkthrough validated against `cases/fastify-naming-lesson/`).
- [x] Every implemented check kind documented with a working example snippet.

#### Task 7.2 DoD

- [x] All appendix cases mapped; zero require framework changes beyond the reserved `judge` kind.
- [x] booping `CLAUDE.md` gains the one-line pointer (committed in the booping repo).

---

## Autonomous execution

This sprint runs unattended (user offline). /develop executes with these pre-approved decisions instead of mid-sprint questions:

- **Milestone groupings**: one briefing per milestone, M1→M7 in order (config caps bundling at 1 anyway) — treated as user-confirmed.
- **Branches**: bench repo (`claude-booping-bench`) is fresh — work lands on its `master` directly. The booping repo's single change (T7.2 CLAUDE.md line) goes on branch `docs/bench-crossref`, committed, **not pushed, no PR** — surfaced in the final report.
- **Auth for calibration/probe runs**: mount the local OAuth credentials read-only (subscription billing). API-key fallback only if the user later provides one — do not wait on it.
- **Cost cap**: claude-invoking runs limited to M2 probes + M5.4 calibration (≤ 3 full reps + dry runs). No matrix runs this sprint.
- **Escalation policy** — contact the user (PushNotification + chat message) only on: (a) auth/credentials blocker that no pre-approved path resolves, (b) the standard failure exit (two failed fix attempts on the same issue → `fail` transition), (c) sprint end (Final Verification report — the single planned wake-up). Everything else: decide per this plan and record the decision in the milestone commit message.
- Any `AskUserQuestion` a skill would normally raise on this path is answered by this section; if a question arises that this section does not cover, prefer the conservative option that keeps all changes local (no pushes, no deletions) and note it in the final report.

## I/O contract

- **Arguments / flags**: `booping-bench run --case <name> [--model <id>] [--booping-ref <git-ref>] [--reps N] [--tag <label>] [--dry-run]`; `booping-bench report <run-id> [--out <path>]`; `booping-bench exec-rep` (internal, in-container only, not documented for users).
- **stdin**: unused.
- **stdout**: `run` — progress lines (one per rep: case, rep, status, wall time) plus final run-id; `report` — markdown report.
- **stderr**: diagnostics, contract-violation messages, unscripted-question text, auth errors.
- **Exit codes**: `0` = success (all reps executed; scores are data, never failures); `1` = user error (unknown case/run-id/flag, contract violation); `2` = internal/environment error (docker, auth, SDK); `3` = one or more reps aborted (unscripted question, timeout) — partial results kept.

## Final Verification

- [x] `just lint && just typecheck && just test` green in `claude-booping-bench`.
- [x] `uv run booping-bench run --case fastify-naming-lesson --reps 3` end-to-end: ≥2/3 reps complete, JSONL written, all four dimensions populated. (M5 calibration run: 3/3.)
- [x] `uv run booping-bench report <that-run-id>` renders both tables.
- [x] `--dry-run` and each documented failure path exit with the contracted code + stderr message.
- [x] README walkthrough matches the shipped reference case file-for-file.

## Out of scope

- `judge` check kind implementation, groom reference case, checklist extraction, compare/delta reports → sibling plan `plans/20260709-benchmark-judge-groom-case-reports.md`.
- Parallel container orchestration (sequential reps only) → sibling plan.
- CI workflows in either repo; scheduled benchmark runs.
- Additional fixture repos (python, react) and the researcher's backlog cases — authored later against the README.
- Any change to booping skills/templates themselves (incl. the prompt-hacks split — separate track).
- Model-matrix studies (GLM/Fable/Opus comparisons) — usage of the framework, not framework work.

## CLAUDE.md impact

- Bench repo: `CLAUDE.md` seeded in M1 (layout, contracts, conventions) — owned by that repo.
- booping repo: one line added to `CLAUDE.md` Layout in T7.2 pointing at the private bench repo. No other booping-repo changes.

## Appendix: future case backlog (mined from project retros, 2026-07-09)

Source: cross-project retro mining (aurora-api, claude-booping, metagame, box, cat-game). Each maps to check kinds; details in `docs/case-backlog.md` after T7.2.

| Pattern | Skill | Freq | Kinds |
|---------|-------|------|-------|
| Follows existing code pattern over explicit CLAUDE.md convention | develop | 3 projects | `file_regex` (filename check) |
| Same, groom variant: plan sketches/Files must follow CLAUDE.md convention | groom | 3 projects | `file_regex` on plan file |
| Literal-but-hollow deliverable (implicit quality bar not in DoD) | develop | 3 projects | `command` + `judge` |
| Plan accepts unbounded failure mode — groom must force a bound | groom | 3 projects | `judge` |
| CLAUDE.md not updated after sprint ships new infra | develop | 2 projects | `command` (grep) |
| Lesson acknowledged in plan Decisions, still violated | groom+develop | 2 projects | `file_regex` (groom) / `judge` (develop) |
| Plan code sketch propagates type error into implementation | develop | 2 retros | `command` (typecheck) |
| Bulk-refactor removes import still used elsewhere | develop | 3 instances | `command` (typecheck/import) |
| Pre-existing failure silently dismissed during verification | develop | 2 retros | `command` + `judge` (transcript) |
| Later milestone sketch references symbol removed by earlier milestone | develop | 2 retros | `command` (typecheck/grep) |
| Worker self-attests audit without verifier output | develop | 2 retros | `command` (injected ref) + `judge` (transcript) |
| Wrong-argument Verify command in plan | develop | designed | `bash_call` + `frontmatter` |
| Buried linter break + fix-lint lesson | develop | designed | `command` (lint) |
| Wrong file path in task Files list | develop | designed | `bash_call` + `judge` |
| Test-checklist extraction (deleted tests) coverage | groom | designed | `judge` (coverage) |
