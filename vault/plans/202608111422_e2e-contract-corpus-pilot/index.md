---
title: "E2E contract-corpus pilot — convert one command's tests"
type: "refactoring"
status: done
sp: 18
related_to: null
created: 2026-08-11 14:23
planned: null
started: 2026-08-11 20:54
completed: 2026-08-11 21:31
code_reviews: []
sessions:
- c9c22604-b390-4be3-a830-639a07421c2e
- 7b90e3f9-ef02-4737-80c2-e908839b8f00
retro: null
summary: scaffold tests become a txtar contract corpus under booping-python/e2e/
  with a standalone runner; units deleted
commit: 5e3840e80ce06dc2731b4d204104f24bb08a7cdf
agents.research-codebase: a95aa90fffd2c764d
agents.research-web: a430d69c5f1cfa4e4
agents.cross-review: ae3c8b5f6f3703a7e
reviewed_at: 2026-08-11 14:59
agents.develop-loop-M01: ab402b07026d67523
agents.develop-loop-M02: acf93a809b39c64f5
agents.develop-loop-M03: a62f3f7f4632b9173
agents.develop-loop-M04: afea11248c691ee72
metrics_active_minutes: 53
metrics_models:
- claude-fable-5
- claude-opus-5
metrics_tokens_input: 954
metrics_tokens_output: 152651
metrics_tokens_cache_creation: 685826
metrics_tokens_cache_read: 17112642
---

# E2E contract-corpus pilot — convert one command's tests

## Context

The `booping scaffold` subcommand's behavior is verified by `booping-python/tests/commands/scaffold_test.py` (~27 subprocess-driven tests whose cases are Python-parametrized tuples and inline trees) and `booping-python/tests/context/scaffold_test.py` (~25 tests importing `booping.context.scaffold` internals and asserting `Node` object graphs, error object fields and exact message text). The internal tests break on refactors without a behavior change and none of the suite would survive a rewrite of the CLI in another language.

After this plan, scaffold's behavior is specified by a contract corpus: one txtar file per case under `booping-python/e2e/cases/scaffold/`, each carrying its fixture tree, the invocation, and the expected stdout / exit code / resulting files — executed by a standalone runner (`booping-python/e2e/run.py`, no pytest) that shells `bin/booping` as a subprocess. The corpus format and runner are the reusable harness later plans use to convert the remaining subcommands (rollout step 1 of `notes/test-strategy.md`). Both superseded test files are deleted in this sprint. No behavior of the `scaffold` command itself changes.

## Decisions

- **Case container — txtar, one file per case**: `-- section --` archive format (Go stdlib precedent): syntax-error-proof, comment-tolerant, git-diff-friendly, whole case reviewable as one unit; parser is ~50 lines vendored (the PyPI `txtar` port is unmaintained — not depended on). Rejected: YAML (schema + library dependency on both future runtimes), dir-per-case (one case scattered over ~6 files), trycmd/prysk/insta-cmd (no language-neutral runner, or no file-tree assertion).
- **Runner — standalone script, no pytest**: the runner is itself part of the spec a future Rust runner reimplements; the corpus needs no fixture/parametrize machinery, and a plain script keeps the authoring loop (`run.py --update`) trivial. Wired as `just e2e`, added to `just ci` and the CI workflow.
- **Location — `booping-python/e2e/`**: runner and cases together, outside `tests/` so pytest never collects them; inside the uv project so ruff/basedpyright cover the harness code.
- **Normalization — token substitution + wildcard**: sandbox-absolute paths are rewritten to `{CWD}`/`{HOME}`/`{XDG}` tokens before comparison; `[..]` matches a volatile span within a line (commit hashes, timestamps). Expected sections are written in normalized form.
- **Multi-command cases**: the `cmd` section may hold several lines run sequentially in the same sandbox; every line but the last must exit 0, the last must match `exit`, and `stdout` asserts the concatenated output. This keeps the existing scaffold→scaffold→query chain test expressible without a second format.
- **Core config is real**: the three-tier merge always loads the plugin's `src/config.yaml`, so cases exercising real trees (`core.groom_playbook.milestone_scaffold` etc.) need no fixture config; cases needing a custom tree ship one at `fixtures/xdg/booping/config.yaml`.
- **Unit remainder — none**: all scaffold unit tests are dropped. `Node.__eq__`/`__repr__` coverage is consciously abandoned (no external observer); declaration-order and error-message behaviors are re-expressed as CLI-observable cases (receipt order, stderr text).

## Architecture

```
booping-python/e2e/
  run.py                    standalone runner (uv run python e2e/run.py)
  _txtar.py                 vendored txtar parse/serialize
  README.md                 case-format spec (the document a Rust runner is built from)
  cases/scaffold/*.txtar    the corpus

per case:  sandbox tmp dir { home/, xdg/, cwd/ }
           fixtures/home|xdg|cwd/** materialized → env HOME, XDG_CONFIG_HOME, cwd set
           cmd lines exec bin/booping (repo-absolute) → capture stdout/stderr/exit
           normalize → compare vs stdout/stderr/exit sections + expected/** files
```

Callers: `just e2e` (dev), `just ci` (gate), `.github/workflows/ci.yml` python job. Consumers of the format: this repo's future command-conversion plans and a potential Rust runner — `README.md` is the contract, `run.py` the reference implementation.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [txtar parser and case-format spec](milestones/M01-txtar-parser-and-format/M01-txtar-parser-and-format.md) | 3 | done |
| 02 | [Standalone corpus runner](milestones/M02-corpus-runner/M02-corpus-runner.md) | 6 | done |
| 03 | [Port scaffold behaviors to corpus cases](milestones/M03-scaffold-case-port/M03-scaffold-case-port.md) | 7 | done |
| 04 | [Delete superseded tests, wire docs](milestones/M04-delete-superseded-tests/M04-delete-superseded-tests.md) | 2 | done |

## I/O contract

Runner: `uv run python e2e/run.py [--update] [pattern...]`

- **pattern**: zero or more substrings matched against case paths relative to `cases/`; none = all cases.
- **`--update`**: rewrites each selected case's `stdout`/`stderr`/`exit`/`expected/**` sections in place from the actual (normalized) run; `cmd`/`fixtures/**` untouched; prints one `updated {case}` line per rewritten file; exit 0.
- **stdout**: one `PASS {case}` / `FAIL {case}` line per case; each FAIL followed by labeled unified diffs (`stdout`, `exit`, one per mismatched `expected/` file); final summary line `{N} passed, {M} failed`.
- **stderr**: runner diagnostics only (malformed case file: path + reason).
- **Exit codes**: `0` all selected cases pass; `1` at least one case failed; `2` malformed case file or no case matched a pattern.

Case file sections: `cmd` (required), `exit` (default `0`), `stdout` / `stderr` (asserted only when present), `fixtures/{home|xdg|cwd}/<path>`, `expected/{home|xdg|cwd}/<path>`.

## Final Verification

- [ ] `just e2e` green over the full scaffold corpus.
- [ ] `just ci` green — with `e2e` in the chain and both superseded test files deleted.
- [ ] Failure output verified: break one case's expected stdout on purpose, confirm the labeled diff and exit 1, restore.
- [ ] `--update` round-trip: run on an untouched corpus, confirm zero diff in git.
- [ ] No remaining import of `booping.context.scaffold` anywhere under `tests/`.

## Out of scope

- No conversion of any other subcommand — this plan delivers the harness and the scaffold corpus only.
- No strict tree assertion (extra files created beyond `expected/**` are not flagged) — receipts already assert created counts; revisit when a case needs it.
- No Rust runner, no CI matrix changes beyond adding the `e2e` step.
- No edits to `notes/test-strategy.md` (vault file — outside the sprint's repo scope).
- No behavior change to `booping scaffold` itself; a corpus case that exposes a real bug is reported, not silently baked into a baseline.

## CLAUDE.md impact

- **Commands** — add `just e2e` (runs the contract corpus; `e2e/run.py --update` regenerates baselines) and note `just ci` now includes it.
- **Layout** — `booping-python/` bullet gains the `e2e/` dir (corpus + runner; case format spec in `e2e/README.md`).
