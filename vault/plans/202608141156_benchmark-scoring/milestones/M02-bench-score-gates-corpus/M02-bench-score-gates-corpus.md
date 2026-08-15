---
id: "02"
title: "bench-score: gates and corpus quality"
sp: 3
status: done
plan: "vault/plans/202608141156_benchmark-scoring/index.md"
---

# M02: bench-score: gates and corpus quality

`bench-score` exists and computes layer-1 gates and corpus-quality metrics for any `bench/*` branch, from a throwaway worktree, emitting JSON.

**Scope**: `vault/benchmarks/_scripts/bench-score` (new, uv inline-metadata Python single file). Reads the M01 registry frontmatter. The script is stack-agnostic about the bench repo: every command it runs on the branch comes from registry data, not hardcode — only the metric logic is code.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Script skeleton + `gates` subcommand: argv `bench-score <subcmd> --benchmark <id> --branch <name>` (registry path via `--registry`, default `vault/benchmarks/index.md`); loads the registry entry, creates `git worktree add` of the branch in a fresh `mkdtemp` dir whose name carries the branch slug — unique per invocation, so concurrent scorings never collide — always pruned, even on failure, runs the gate checks — milestone `status:` fields ×3 (`done` / `fail@Mnn`), `just ci` exit, clean e2e run exit, `--txtar-update` determinism (`git diff --quiet` after), unit file absent + repo grep empty, scope = `git diff {baseline} --name-only` ⊆ `scope_allowlist` — and prints one JSON object `{gate: {pass, evidence}}` on stdout, progress on stderr. | `vault/benchmarks/_scripts/bench-score` | 2 | done |
| 2.2 | `corpus` subcommand: parse the branch's `.txtar` cases (sections `cmd/exit/stdout/stderr/expected/*`) and emit per-case + aggregate JSON — asserted channels per case and the 4-channel %, `[..]` count per case and wildcarded-line ratio, etalon recall as exact-name matches n/34 with the unmatched etalon names and unmatched branch cases listed for runner mapping, gap cases n/3 by name. Pure parsing — no test execution. | `vault/benchmarks/_scripts/bench-score` | 1 | done |

Tests (lesson 0016): the script's own behavior is covered by running it against real branches — `bench/reference` (all corpus metrics zero-case, gates red) and the deepseek branch (known values from PR #35: 30 cases, 3 gaps, unit deleted, ci green). Assert the JSON, not internals; no separate unit suite for a vault tool.

## Definition of Done

### Task 2.1
- [x] `gates --branch bench/deepseek-deepseek-v4-pro-0813` reports all six gates pass with evidence strings (exit codes, diff-empty, grep-empty).
- [x] `gates --branch bench/reference` reports the corpus-dependent gates red without crashing.
- [x] Worktree is created fresh per invocation and pruned on every exit path; the bench repo's checked-out branch is untouched.
- [x] No registry value (repo path, baseline, allowlist, commands) appears as a literal in the script.

### Task 2.2
- [x] On the deepseek branch: case count 30, exact-name gap cases 0/3 and recall 4/34 (deepseek renamed its cases) with the unmatched etalon and unmatched branch names listed for the measure step's case-mapping judge, 4-channel % and wildcard ratios computed; numbers spot-checked by hand against 3 named `.txtar` files.
- [x] A case file with a missing optional section (no stdout, no stderr) parses without error and counts channels correctly.
- [x] JSON on stdout only; humans read stderr.

## Verify

- `vault/benchmarks/_scripts/bench-score gates --benchmark frontmatter-update-e2e --branch bench/deepseek-deepseek-v4-pro-0813 | jq .` — six gates, all pass.
- Same for `corpus` — aggregate block matches the branch's facts: 30 cases, exact-name gaps 0/3 and recall 4/34, unmatched lists present for runner mapping.
- `git -C /home/anton/Dev/@A/claude-booping-local-bench worktree list` shows no leftover bench-score worktrees after runs.
