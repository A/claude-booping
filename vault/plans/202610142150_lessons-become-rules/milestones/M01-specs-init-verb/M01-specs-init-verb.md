---
id: "01"
title: "booping specs init creates a tier"
sp: 6
status: done
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M01: booping specs init creates a tier

`booping specs init --tier {global|project}` creates a specs tier root with its README, plus the vault symlink when the vault is outside the repo, and prints the tier root — the one mechanic `learn`, `setup` and the parked migration call.

**Scope**: `booping-python/src/booping/commands/specs.py` (new `init` verb beside `ls`/`next`/`check`), a new `booping-python/src/booping/specs/init.py` holding the logic, tier resolution reused from `booping-python/src/booping/specs/tiers.py` (`resolve_tiers`, `project_root`) — never re-derived; new e2e cases under `booping-python/e2e/cases/specs/`; one line in `src/specs/README.md` and the `specs` verb list in `CLAUDE.md`. Behaviour and exact output are locked in `clarifications.md` C3 and C4 — copy them, do not paraphrase.

Tests: the CLI surface through the txtar corpus (integration tier) — cases: project tier with the vault in the repo, project tier with the vault outside the repo (dir + symlink), global tier, a second run that changes nothing, an existing non-symlink `{vault}/specs` when the vault is outside the repo (exit 1, nothing written), `--tier core` rejected, an existing README left byte-identical.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `init` verb: resolve the tier root through `tiers.py`; create missing dirs, the tier README (C4 content, written only when absent), and for a vault outside the repo the symlink `{vault}/specs → {repo}/specs`; print one action line per change then the absolute tier root (C4); `--tier core` and a conflicting `{vault}/specs` → stderr `specs init: {message}`, exit 1, nothing written. Default tier `project`, like `ls`/`next`. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/init.py` | 3 | done |
| 1.2 | e2e cases, one per case named in Scope, expected output hand-written from C4. | `booping-python/e2e/cases/specs/init-*.txtar` | 2 | done |
| 1.3 | `src/specs/README.md` `## Tiers`: one sentence naming `booping specs init --tier global\|project` as how a tier is created. `CLAUDE.md` Commands: `specs` verbs list gains `init`. | `src/specs/README.md`, `CLAUDE.md` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `bin/booping specs init --help` lists `--tier` with choices and the default.
- [x] Root resolution calls `tiers.py`; no second copy of the in-repo / outside-repo rule.
- [x] A rerun on an initialized tier prints only the tier root and writes nothing.
- [x] Nothing is written before every check passes (a conflict leaves the filesystem untouched).

### Task 1.2

- [x] Every Scope case has its own `init-*.txtar`; expected stdout and stderr are literal text from C4, not produced by running the code first.
- [x] The symlink case asserts the link's target, not just its existence.

### Task 1.3

- [x] `src/specs/README.md` gains exactly one sentence; `CLAUDE.md` lists `init` among the `specs` verbs.

Return: the list of changed files, nothing else.

## References

- `booping-python/e2e/cases/specs/ls-tier-global-reads-the-home-dir-specs.txtar` — case shape for a global-tier fixture.
- `booping-python/e2e/cases/specs/next-on-an-empty-type-starts-at-one.txtar` — case shape for a project-tier fixture.
- `booping-python/src/booping/commands/scaffold.py` — `created dir` / `created file` wording precedent.

## Verify

`just e2e -k "specs and init"`
