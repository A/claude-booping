---
title: File-target frontmatter-update hook syntax
type: bug
status: done
sp: 8
split_from: null
created: 2026-07-31 20:00
planned: 20260731 12:45
started: 20260731 12:50
completed: 2026-07-31 13:00
retro: null
goal: null
summary: "Support frontmatter-update <file> k=v hook form in playbook transitions,
  workdir-relative with {instance}"
commit: a52234536c753e9fcc5d52f8feb119ad65a65daf
sessions:
- e94730a4-c5d2-4cca-91ee-654735019c32
- 64cab6ba-1c29-4b9f-8911-e51255067a5b
metrics_active_minutes: 22
metrics_models:
- claude-fable-5
metrics_tokens_input: 7015
metrics_tokens_output: 124854
metrics_tokens_cache_creation: 727403
metrics_tokens_cache_read: 13361033
---

# File-target frontmatter-update hook syntax

## Context

`booping playbook-transition` dispatches `frontmatter-update` hooks via the shared `dispatch_frontmatter_update` (`booping-python/src/booping/commands/transition.py:84`). The parser treats **every** token after the hook name as a `key=val` pair; the hook can therefore only mutate the state machine's own artifact.

The `playbook-authoring` playbook (`~/Claude/_playbooks/playbook-authoring/playbook.yaml`) authors hooks in the form `frontmatter-update <file> <key>=<val>` — a file-target first argument (`_specs/brief.md`, `_specs/index.md`, `_specs/states.md`, `playbook.md`, `_specs/steps/{instance}/index.md`, `{instance}/prompt.md`). `_parse_pairs` hits the pathname, finds no `=`, prints `error: malformed key=value pair: '_specs/brief.md'` and exits 1. Every confirm-gate edge of that playbook fails.

**Reproduction**: from a `playbook-authoring` run workdir with `_specs/index.md` at `awaiting-brief-confirm` and `_specs/brief.md` present:

```bash
booping playbook-transition playbook-authoring decomposing --workdir <run-workdir>
# stderr: error: malformed key=value pair: '_specs/brief.md'
# exit 1
```

**Root cause**: hook vocabulary has no file-target form; `dispatch_frontmatter_update` assumes the machine artifact is the only legal target and parses all trailing tokens as pairs.

**After**: a first token without `=` after the hook name is a file target, resolved workdir-relative with `{instance}` interpolation; the hook updates that file's frontmatter instead of the artifact. No-target form unchanged. Plan `transition` vocabulary unchanged (file target there is a clear error).

## Decisions

- **Syntax**: `frontmatter-update [<file>] <key>=<val>...` — file target detected as "first token after hook name contains no `=`". No flag; matches what playbook-authoring already wrote, fully backward compatible (every `key=val` token contains `=`).
- **Resolution**: file target resolves against the run **workdir** (same anchor as the machine artifact). `{instance}` in the target interpolates the `--instance` slug; `{instance}` present with no instance in scope → error exit 2.
- **Missing file / no frontmatter block**: error, exit 2 — consistent with script-hook failure; the hook aborts the transition with clear stderr. No bootstrap. (User-confirmed.)
- **Plan transitions**: `booping transition` keeps artifact-only vocabulary. File target in a plan hook → `error: file-target frontmatter-update is not supported in plan transitions`, exit 2. No use case; config-owned hooks never need it.
- **Report line**: file-target form prints `frontmatter <rel>: k=v` (target between hook name and colon, path as written in the hook after `{instance}` interpolation, workdir-relative). No-target form stays `frontmatter: k=v`. (User-confirmed.)
- **Existing malformed-pair exit code**: `_parse_pairs` exit 1 untouched — changing the established contract is out of scope.
- **Error mechanism**: new failure paths use the dispatcher's existing pattern — `print("error: ...", file=sys.stderr)` + `sys.exit(2)` inside `dispatch_frontmatter_update`, exactly as the current `update_frontmatter` failure branch does. No new exception types.

## Architecture

`dispatch_frontmatter_update(hook, target, project)` (`booping-python/src/booping/commands/transition.py:84`) gains keyword-only params `file_base: Path | None = None` and `instance: str | None = None`. Its return type changes from `dict[str, str]` to `tuple[str | None, dict[str, str]]` — `(file-target rel-path or None, resolved pairs)`. Exactly two call sites exist, both updated in this plan: `booping-python/src/booping/commands/transition.py:220` and `booping-python/src/booping/commands/playbook_transition.py:218` (both currently bind the bare dict — unpack the tuple there).

- `playbook-transition` passes `file_base=workdir, instance=instance`. When the hook carries a file target, the dispatcher interpolates `{instance}`, resolves `file_base / rel`, and applies `update_frontmatter` to that path instead of the artifact.
- `transition` passes neither; a file target with `file_base=None` → error exit 2.
- `update_frontmatter` (`booping-python/src/booping/context/_yaml.py:98`) is unchanged — its `ValueError` on missing/`---`-less file is caught and reported as hook failure exit 2.
- `format_frontmatter_line` (`booping-python/src/booping/commands/transition.py:154`) grows an optional `target: str | None = None` param producing the `frontmatter <rel>:` prefix.

Callers of the printed report (playbook driver via `_playbook_driving.j2`) treat the report as authoritative and never re-read — the new line shape is additive; existing lines are byte-identical.

## Milestones

### M1: File-target parsing + dispatch — 7 SP | done

**Goal**: `frontmatter-update <file> <key>=<val>...` hooks in playbook transitions update the named workdir-relative file (with `{instance}` interpolation); plan transitions reject the form; report line carries the target.

**Verify**: `cd booping-python && uv run pytest tests/commands/playbook_transition_test.py tests/commands/transition_test.py -q` — all green, including new file-target cases. Then a live check: author a temp playbook with hook `frontmatter-update _specs/brief.md reviewed_at=@now`, run `booping playbook-transition <pb> <to> --workdir <tmp>`, expect exit 0, report line `frontmatter _specs/brief.md: reviewed_at="<utc now>"`, and `reviewed_at` present in `_specs/brief.md` frontmatter.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Extend `dispatch_frontmatter_update` with optional file target (`file_base`/`instance` kwargs, `{instance}` interpolation, exit-2 error paths) + `format_frontmatter_line` target prefix | `booping-python/src/booping/commands/transition.py` | 3 | done |
| 1.2 | Wire `playbook-transition` (pass workdir + instance, print targeted report line) and `transition` (file target → exit-2 error) | `booping-python/src/booping/commands/playbook_transition.py`, `booping-python/src/booping/commands/transition.py` | 2 | done |
| 1.3 | Regression tests: file-target happy path, `{instance}` interpolation, `{instance}` without instance, missing file, no-frontmatter-block, plan-transition rejection, no-target backward compat, report-line shapes | `booping-python/tests/commands/playbook_transition_test.py`, `booping-python/tests/commands/transition_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] `frontmatter-update _specs/brief.md reviewed_at=@now` with `file_base=<dir>` updates `<dir>/_specs/brief.md` frontmatter, leaves artifact untouched.
- [x] `frontmatter-update reviewed_at=@now` (no target) behaves exactly as before against the passed target path.
- [x] `{instance}` in file target interpolates the passed slug; `{instance}` with `instance=None` → stderr message + exit 2.
- [x] File target with `file_base=None` → `error: file-target frontmatter-update is not supported in plan transitions`, exit 2.
- [x] Missing target file or `ValueError` from `update_frontmatter` → stderr + exit 2.
- [x] `format_frontmatter_line` with target renders `frontmatter <rel>: k=v` (quoting rule for spaced values unchanged); without target renders `frontmatter: k=v` byte-identically to today.

#### Task 1.2 DoD

- [x] `playbook-transition` passes `file_base=workdir, instance=instance` on every `frontmatter-update` hook; report line for file-target hooks shows the interpolated workdir-relative path.
- [x] Both call sites unpack the new `(target, resolved)` tuple return — no bare-dict binding remains.
- [x] `transition` passes no `file_base`; a file-target hook in a plan edge exits 2 with the defined message.
- [x] Bootstrap, idempotent, and script-hook paths of `playbook-transition` unchanged.

#### Task 1.3 DoD

- [x] A test fails on pre-fix code with `malformed key=value pair` for the file-target form, passes post-fix (regression test).
- [x] Each error path (missing file, no frontmatter block, `{instance}` sans instance, plan-transition rejection) asserted on exit code 2 + stderr substring.
- [x] Report-line assertions cover both `frontmatter <rel>: k=v` and legacy `frontmatter: k=v`.
- [x] `cd booping-python && uv run pytest -q` green; `just lint`, `just typecheck` clean.

---

### M2: Hook-vocabulary docs — 1 SP | done

**Goal**: every surface documenting the hook vocabulary describes the file-target form.

**Verify**: `grep -n "frontmatter-update" documentation/playbook.md CLAUDE.md` — vocabulary lines show `frontmatter-update [<file>] <key>=<val>...` with workdir-relative + `{instance}` semantics; no stale artifact-only claim remains.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Update hook-vocabulary wording: `documentation/playbook.md` (§ hooks, line ~289) + `CLAUDE.md` playbook section ("Hook vocabulary:" sentence) | `documentation/playbook.md`, `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] `documentation/playbook.md` hook bullet documents the optional file target, workdir-relative resolution, `{instance}` interpolation, and error-on-missing-file behavior.
- [x] `CLAUDE.md` playbook-section hook-vocabulary sentence updated to match.
- [x] No other repo surface still asserts frontmatter-update targets only the artifact (`grep -rn "frontmatter-update" docs/ documentation/ src/templates/ CLAUDE.md` reviewed).

---

## I/O contract

- **Hook string**: `frontmatter-update [<file>] <key>=<val>...` — `<file>` = first post-name token without `=`; workdir-relative; may contain `{instance}`. Values keep `@now`/`@today`/`@head` interpolation.
- **stdout** (report, authoritative): no-target `frontmatter: k=v`; file-target `frontmatter <rel>: k=v` — `<rel>` is the hook's path after `{instance}` interpolation. Values with spaces double-quoted, as today.
- **stderr**: all diagnostics. New messages: `error: file-target frontmatter-update is not supported in plan transitions`; `error: frontmatter-update target <rel> carries {instance} but no instance is in scope`; missing-file / parse failures via the existing `error: frontmatter-update failed: ...` shape.
- **Exit codes**: 0 success; 1 existing malformed `key=val` pair (unchanged); 2 all new file-target failure modes (unsupported context, `{instance}` sans instance, missing file, no frontmatter block) — consistent with hook-failure = 2.

## Final Verification

- [x] `cd booping-python && uv run pytest -q`, `just lint`, `just typecheck` — green.
- [x] Live repro from Context now succeeds: `booping playbook-transition playbook-authoring decomposing --workdir <run-workdir>` exits 0 with `frontmatter _specs/brief.md: reviewed_at=...` in the report.
- [x] Failure path verified live: same hook with `_specs/brief.md` deleted → exit 2, stderr names the file.
- [x] Plan-transition surface unaffected: `booping transition` on a normal edge produces a byte-identical report to pre-change.

## Out of scope

- No bootstrap/auto-create of target files or frontmatter blocks.
- No file-target support in plan (`booping transition`) hook vocabulary beyond the explicit rejection.
- No change to the standalone `booping frontmatter-update` CLI (already file-positional).
- No path-escape guarding (`../`) on file targets — playbooks are trusted local content.
- No change to `_parse_pairs` exit-1 contract for malformed pairs.
- No hook transactionality/rollback — hooks already run in order with abort-on-failure and no undo (script hooks included); unchanged.
- No error-handling refactor of the dispatcher (exceptions instead of `sys.exit`) — existing pattern kept for a minimal bug fix.

## CLAUDE.md impact

`CLAUDE.md` playbook section, "Hook vocabulary:" sentence — extend `frontmatter-update <key>=<val>...` to `frontmatter-update [<file>] <key>=<val>...` with workdir-relative + `{instance}` semantics (Task 2.1).
