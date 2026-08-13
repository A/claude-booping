# Framing brief

## Request

> sounds good, can you 1. make a file somewhere in vault named test-strategy.md, and then groom refactoring of some pilot command into e2e tests, let's say scaffold or render.

(Context: follows a [CHAT] discussion validating that ~400 of 744 pytest cases are implementation-coupled — internal imports or exact-prose asserts. Agreed direction is written to `notes/test-strategy.md`: a language-neutral contract corpus run through the `bin/booping` subprocess boundary, unit tests kept only for algorithmic cores, prose owned by snapshots + mdcheck. Long-term drivers: possible Rust rewrite and a kubectl-style framework future, both needing behavior-level specs.)

## Task type

`refactoring` — internal test-structure change; observable CLI behavior identical before and after. Not `feature`: no new user-facing capability — the CLI's contract is unchanged, only how it is verified. Not `bug`: no observed-vs-expected divergence in the product; the defect is in test design, which is structure, not behavior.

## Problem

Today one pilot command's behavior is verified by tests that import Python internals and assert implementation-shaped details, so they break on refactors, and none of them would survive a rewrite of the CLI in another language. After this plan, that command's behavior is specified by a contract corpus — language-neutral case files (fixture tree + argv → stdout/exit code/file-tree delta) executed through `bin/booping` as a subprocess — plus a reusable corpus harness and a documented case format that later plans use to convert the remaining commands. The superseded internal tests for that command are deleted in the same sprint; coverage of the command's behavior is preserved or improved.

## Clarifications and Decisions

- Strategy doc: `notes/test-strategy.md` (written before this run; the plan implements its "Rollout step 1").
- Pilot command: `scaffold`.
- Goal confirmed: rewrite-portable behavior specs + fragility reduction; harness + case format reusable for later command conversions.
- Superseded internal tests (`commands/scaffold_test.py`, `context/scaffold_test.py`) deleted in this same sprint.
- Corpus format authority in scope: a folder of e2e cases — vault/config fixtures + expected result per case; writing a new case must be easy.
- No post-implementation reshape pass (reshape lesson pair 0008/0009 deleted at user request).
- Case container: txtar — one flat file per case (`-- cmd --`, `-- exit --`, `-- stdout --`, `-- fixtures/... --`, `-- expected/... --`), parser vendored (~50 lines), no YAML/schema dependency.
- Runner: standalone, **no pytest** — own script under `booping-python/e2e/` (runner + cases both live there); wired as a `just` target and into `just ci`.
- Output normalization: `{DEST}`/`{HOME}`/`{XDG}` tokens + `[..]` wildcard for volatile spans.
- Baseline regeneration: runner `--update` flag rewrites `stdout`/`expected/` sections from actual output.
- All scaffold unit tests dropped — tests guarantee behavior, not implementation; `Node` equality/repr coverage consciously abandoned.
