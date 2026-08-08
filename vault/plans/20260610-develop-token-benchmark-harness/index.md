---
title: Develop-Skill Token Benchmark Harness
type: feature
status: cancelled
sp: 37
split_from: null
created: 2026-06-10 00:00
planned: 20260610 11:37
commit: 4d075d4c05119552e925c1c632db1929d69f4fc4
started: null
completed: 2026-07-09 06:25
retro: null
goal: null
summary: "Harbor-based benchmark harness measuring /develop token cost and validity (CPCT) across skill variants"
---

# Develop-Skill Token Benchmark Harness

## Context

There is no way today to tell whether a change to the `/develop` skill (shorter prompt,
extracted partial, agent decomposition) made it cheaper or just made it worse. This plan
builds a Harbor-based harness that runs `/develop` on fixed inputs and records token cost,
gated on validity so a variant cannot "win" by producing broken code.

- **Input** (per fixture): an OSS repo pinned at a real PR's base commit + a frozen booping
  plan (hand-groomed from that PR) + the repo's test command + the real PR diff (judge
  reference). 10 fixtures listed in `_notes/benchmark-prs.md`.
- **Run**: `/develop` executes the frozen plan headlessly inside a Harbor-managed container;
  total token usage + cost are captured from `claude -p --output-format json`.
- **Validity gate**: the produced code must (1) pass the repo's tests and (2) satisfy an
  LLM-judge comparing the agent's diff against the real PR. Only valid runs count toward cost.
- **Output**: per skill-variant — valid-rate, mean tokens (valid runs), and **CPCT**
  (cost / valid-rate); paired deltas baseline-vs-variant across the same 10 fixtures.

This is **v1**: total tokens only. Per-agent attribution (orchestrator vs `booping-developer`)
is an explicit phase-2 follow-up (see Out of scope).

## Decisions

- **Runner = Harbor installed-agent.** — `booping` is a Claude Code plugin, not a standalone
  binary, so it runs as a Harbor *installed agent*: Claude Code + booping are installed into
  the task container in `install()`, then driven headless in `run()`. Harbor provides the
  per-fixture container isolation, the repeat mechanism, and the verifier/reward plumbing the
  validity gate needs. Fixtures are authored in Harbor task format.
- **Both arms are the same installed-agent class, differing only by the booping git ref +
  seeded `config.yaml`.** — Keeps the comparison honest: identical prompt and harness, one
  variable (the skill version under test).
- **Token capture = `claude -p --output-format json`.** — Verified: returns
  `usage{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}`
  + `total_cost_usd`. Parsed in `run()` / `populate_context_post_run()`. Per-agent split is
  absent here → deferred to phase 2 (needs OTel).
- **Validity = tests AND judge.** — Tests run as the Harbor task verifier (`test_cmd` →
  reward), pass/fail. The LLM-judge (reference = real PR diff + task description) is a second
  scorer catching gamed-test / incomplete work. A run is valid only if both pass.
- **Primary metric = CPCT; secondary = mean tokens (valid).** — CPCT exposes a variant that
  cheapens by failing. Variants compared paired across the same fixtures.
- **Non-interactive `/develop` = vault-local `_booping/skill_develop.md` directive.** —
  `develop.md.j2:121` renders the `skill_develop` extension, which overrides the confirm
  gates at lines 38/76/80. The directive ("headless sandbox; auto-approve groupings, branch,
  drift; never pause") is seeded into every fixture vault — identical across variants, so it
  does not bias the comparison. No change to the shipped skill.
- **Location = top-level `benchmark/` dir.** — Standalone tooling (Harbor agent adapter, task
  fixtures, aggregator); not added to `booping-python`'s shipped CLI surface.
- **Frozen plans are fixture data, authored by the user via `/groom`.** — Plan authoring is
  manual prep, not develop-agent work. M1 ships one smoke fixture's plan to build against; the
  other 9 are authored before a full run (documented in the runbook).

## Architecture

`benchmark/` holds a Harbor installed-agent adapter, the 10 fixtures as Harbor tasks, and an
aggregator. The flow per `(fixture × variant × repeat)`, orchestrated by `harbor run`:

1. Harbor starts the task container (per-fixture `environment/Dockerfile`, node or python)
   with the repo at `base_commit`.
2. Adapter `install()`: install Claude Code + booping at the variant's git ref; seed a vault
   (`booping-create-project`), drop the frozen plan at `ready-for-dev`, attach the repo, seed
   the headless `_booping/skill_develop.md`.
3. Adapter `run()`: `claude -p "/develop plans/<plan>" --output-format json`; capture the
   result `usage` + `total_cost_usd`; leave the produced diff in the repo working tree.
4. `populate_context_post_run()`: record usage/cost + the `git diff` into the run context.
5. Validity: Harbor's task verifier runs `test_cmd` → reward (pass/fail); the LLM-judge scorer
   reads `(task_description, real_pr_diff, agent_diff)` → valid/invalid + rationale.
6. `bench aggregate` reads Harbor's per-trial job outputs into raw records, then reports
   per-variant valid-rate, tokens, CPCT, and paired baseline-vs-variant deltas.

Callers: human-run from the repo root via `harbor run` + `bench aggregate`. No skill inlines it.

## Milestones

### M1: Fixtures as Harbor tasks — 10 SP | pending

**Goal**: the 10 PRs become Harbor task directories the adapter can run.

**Verify**: `harbor tasks validate benchmark/fixtures/flask-5917` passes; the task dir holds
`task.toml`, `environment/Dockerfile`, `tests/`, `pr.diff`, and a vault/plan slot.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Harbor task schema + smoke fixture (`flask-5917`) authored end-to-end as the reference shape | `benchmark/fixtures/flask-5917/`, `benchmark/README.md` | 3 | pending |
| 1.2 | Materialize the other 9: resolve each PR's base commit (`git merge-base`), fetch `pr.diff` + body via `gh pr diff <n>` / `gh pr view <n> --json` (auth via `GITHUB_TOKEN`), write `task.toml` | `benchmark/fixtures/*/task.toml`, `benchmark/fixtures/build.py` | 3 | pending |
| 1.3 | Per-stack `environment/Dockerfile` + `tests/` verifier (node→`npm test`, python→`pytest`) wired as the reward | `benchmark/fixtures/*/environment/`, `benchmark/fixtures/*/tests/` | 3 | pending |
| 1.4 | Headless `_booping/skill_develop.md` directive seeded into each task's vault slot | `benchmark/fixtures/headless_develop.md` | 1 | pending |

#### Task 1.1 DoD
- [ ] `task.toml` schema documented (repo, base_commit, pr_url, test_cmd, base_image, plan path).
- [ ] `flask-5917` validates with `harbor tasks validate` and runs the oracle to green.
- [ ] Dir layout holds repo metadata, `pr.diff`, and a vault slot for the frozen plan.

#### Task 1.2 DoD
- [ ] `base_commit` = the PR's merge-base parent (state before the PR), for all 10.
- [ ] `pr.diff` + task description captured per fixture via `gh` (token-authed to avoid rate limits).
- [ ] Re-running `build` is idempotent.

#### Task 1.3 DoD
- [ ] Each fixture's `environment/Dockerfile` installs the repo's deps and runs its tests.
- [ ] `tests/` verifier maps `test_cmd` pass/fail to a Harbor reward.

#### Task 1.4 DoD
- [ ] Directive instructs headless/sandbox + auto-approve groupings/branch/drift + never pause.
- [ ] Seeded into every fixture vault at `install()` time.
- [ ] Four-check IA pass (lesson 0004) run on the directive before saving.

---

### M2: Harbor installed-agent — `/develop` run + token capture — 10 SP | pending

**Goal**: a `BoopingDevelopAgent` installed-agent runs `/develop` on a fixture and records the
run's token usage + diff.

**Verify**: `harbor run -d benchmark/fixtures --agent-import-path benchmark.agent:BoopingDevelopAgent --ak variant=HEAD` on the smoke fixture writes a trial with non-zero `usage.input_tokens`, `total_cost_usd`, and a captured diff.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | [SPIKE] Confirm Harbor API against the live repo: `BaseInstalledAgent` `install`/`run`/`populate_context_post_run` signatures, agent-kwargs (`--ak`), and the repeats mechanism; record findings | `benchmark/agent/NOTES.md` | 3 | pending |
| 2.2 | `install()`: install Claude Code (npm `-g @anthropic-ai/claude-code`); clone booping repo at `variant` ref + `just build` + register as a plugin (`claude plugin add <path>`); seed vault (`booping-create-project`, frozen plan at `ready-for-dev`, attach repo, headless directive); wire `ANTHROPIC_API_KEY` into the container via Harbor's task env config | `benchmark/agent/booping_develop.py` | 4 | pending |
| 2.3 | `run()` + `populate_context_post_run()`: headless `claude -p "/develop ..." --output-format json` with a wall-clock timeout + one retry on hang/non-zero/rate-limit; parse `usage` + `total_cost_usd`; capture the agent's full diff via `git add -A && git diff --staged` (includes new files) | `benchmark/agent/booping_develop.py` | 3 | pending |

#### Task 2.1 DoD
- [ ] Real `BaseInstalledAgent` method signatures confirmed from the installed Harbor package.
- [ ] Repeats mechanism (`--k` or equivalent) confirmed or a fallback loop chosen.
- [ ] `--ak variant=<ref>` plumbing confirmed for selecting the booping version.
- [ ] Verifier/reward I/O contract confirmed (reward file path + JSON schema vs exit code) — consumed by M3.1.
- [ ] Per-trial job output dir structure + file naming confirmed — consumed by M4.1.

#### Task 2.2 DoD
- [ ] Claude Code installed; booping cloned at the requested git ref, `just build` run, registered as a plugin so `/develop` resolves.
- [ ] Vault seeded; frozen plan present at `status: ready-for-dev`; repo attached at `base_commit`.
- [ ] Headless `_booping/skill_develop.md` present in the seeded vault.
- [ ] `ANTHROPIC_API_KEY` injected into the container through Harbor's task run config (host env does not cross the isolation boundary automatically); never baked into the image.

#### Task 2.3 DoD
- [ ] `/develop` runs to completion without pausing for confirmation.
- [ ] Timeout + single retry handle hang / non-zero exit / API rate-limit; an exhausted run is recorded as failed, not crashed.
- [ ] All four token fields + `total_cost_usd` parsed from the JSON result.
- [ ] The agent's full diff — **including newly created files** (`git add -A && git diff --staged`) — captured into the run context.

---

### M3: Validity gate — tests + LLM-judge — 7 SP | pending

**Goal**: a run is labelled valid/invalid by the Harbor test verifier and an LLM-judge scorer.

**Verify**: a known-good diff → `valid: true` (tests pass, judge pass); an empty diff → `valid: false`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Tests-as-verifier: the fixture `tests/` reward (from M1.3) surfaced into the run record as pass/fail + truncated output | `benchmark/validity/tests.py` | 3 | pending |
| 3.2 | LLM-judge scorer: `anthropic` SDK, model `claude-opus-4-8` (key from `ANTHROPIC_API_KEY`); prompt with `(task_description, real_pr_diff, agent_diff)` → strict JSON `{valid, rationale}`; record model + prompt version | `benchmark/validity/judge.py`, `benchmark/validity/judge_prompt.md` | 3 | pending |
| 3.3 | Combine: `valid = tests_pass AND judge_pass`; write into the raw record | `benchmark/validity/gate.py` | 1 | pending |

#### Task 3.1 DoD
- [ ] Test reward maps to pass/fail in the run record, using the verifier I/O contract confirmed in M2.1.
- [ ] Test output truncated and stored for debugging.

#### Task 3.2 DoD
- [ ] Judge sees task description + real PR diff (reference) + agent diff; returns strict-JSON valid + rationale.
- [ ] Judge model (`claude-opus-4-8`), SDK, and prompt version recorded for reproducibility.
- [ ] Four-check IA pass (lesson 0004) run on `judge_prompt.md` before saving.

#### Task 3.3 DoD
- [ ] `valid` true only when both gates pass.
- [ ] Gate result + both sub-verdicts written to the raw record.

---

### M4: Aggregator — valid-rate, CPCT, paired deltas — 7 SP | pending

**Goal**: `bench aggregate` turns Harbor trial outputs into a per-variant report and a
baseline-vs-variant comparison.

**Verify**: `python -m benchmark.aggregate <job-dir> --baseline v0 --variant v1` prints a table
with valid-rate, mean tokens (valid), CPCT, and per-fixture token deltas.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Raw-record schema + reader over Harbor trial outputs (fixture, variant, repeat, usage, cost, validity, judge meta) | `benchmark/record.py` | 2 | pending |
| 4.2 | Aggregate per variant: valid-rate, mean + CV tokens over valid runs, CPCT = mean cost / valid-rate | `benchmark/aggregate/stats.py` | 3 | pending |
| 4.3 | Paired report: per-fixture token/cost delta baseline-vs-variant + markdown summary table | `benchmark/aggregate/report.py` | 2 | pending |

#### Task 4.1 DoD
- [ ] One record per `(fixture, variant, repeat)` with all metric + provenance fields.
- [ ] Reader recovers records from a Harbor job dir using the structure confirmed in M2.1; schema documented.

#### Task 4.2 DoD
- [ ] Per variant: valid-rate, mean tokens (valid only), CV, CPCT computed.
- [ ] Invalid runs excluded from token/cost means but counted in valid-rate.

#### Task 4.3 DoD
- [ ] Paired per-fixture deltas printed (same fixture, two variants).
- [ ] Markdown summary emitted to stdout and an output file.

---

### M5: Runbook + CLAUDE.md — 3 SP | pending

**Goal**: a documented path to add a fixture and compare two skill variants.

**Verify**: a new contributor follows `benchmark/RUNBOOK.md` and reproduces a baseline-vs-variant
report on the smoke fixture.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Runbook: author a frozen plan via `/groom`, build a Harbor fixture, `harbor run` a variant, aggregate, compare | `benchmark/RUNBOOK.md` | 2 | pending |
| 5.2 | CLAUDE.md: add a `benchmark/` entry under Layout + a one-line note | `CLAUDE.md` | 1 | pending |

#### Task 5.1 DoD
- [ ] Steps cover: groom a frozen plan, materialize fixture, `harbor run`, aggregate, read CPCT.
- [ ] The 9 not-yet-authored frozen plans listed as a prep checklist.

#### Task 5.2 DoD
- [ ] `benchmark/` documented in CLAUDE.md Layout as standalone tooling (not shipped plugin),
      noting the Harbor dependency.

---

## I/O contract

- **Commands**:
  - `harbor run -d benchmark/fixtures --agent-import-path benchmark.agent:BoopingDevelopAgent --ak variant=<git-ref> [--k N]` — run `/develop` across fixtures.
  - `bench aggregate <harbor-job-dir> --baseline <ref> --variant <ref>` — report.
- **stdin**: none.
- **stdout**: Harbor progress (run); human tables (aggregate). Records under the Harbor job dir.
- **stderr**: container/install/test diagnostics.
- **Exit codes**: `0` success; `1` user error (bad fixture, missing key); `2` internal
  (container/install failure). A run that completes but is *invalid* is `0` — invalidity is
  data, not an error.

## Final Verification

- [ ] All 10 fixtures pass `harbor tasks validate`.
- [ ] `harbor run` produces a valid trial on the smoke fixture (non-zero tokens, captured diff).
- [ ] Validity gate labels a known-good diff valid and an empty diff invalid.
- [ ] `bench aggregate` emits CPCT + paired deltas for two variants.
- [ ] Repo's own `just lint && just typecheck && just test` green for any code added under `benchmark/`.

## Out of scope

- **Per-agent token attribution** (orchestrator vs `booping-developer`) — needs OTel
  (`agent.name`/`skill.name`); phase 2. v1 measures total only.
- **Statistical significance** beyond mean + CV (McNemar / paired bootstrap) — phase 2.
- **Quality scoring** beyond tests + binary judge — no rubric scoring, no `result` branch.
- **Authoring the 10 frozen plans** — manual `/groom` prep, fixture data, not dev work here.

## CLAUDE.md impact

- Add a `benchmark/` entry under **Layout** describing it as standalone, non-shipped tooling
  (Harbor-based) that measures `/develop` token cost (M5.2). No other sections change — the
  harness adds no skills, agents, config keys, or build steps to the plugin itself.
</content>
