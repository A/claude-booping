---
type: adr
title: CLI behaviour is tested by a contract corpus, not by internal unit tests
summary: Each CLI subcommand is specified by language-neutral cases run through bin/booping; unit tests cover only algorithmic hotspots, and prose is owned by snapshots and mdcheck.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0010, value/0003]
sources: [CLAUDE.md]
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/test-strategy.md
---

## Context

The suite had 744 pytest cases, roughly 400 of them noise-prone: about 270 imported
`booping.*` internals and would die with any rewrite, and 131 cases in one file
grepped exact prose sentences out of a render — wording changes broke tests that
verified no behaviour. The rendered prose was already covered twice, by committed
snapshots and by mdcheck. Two futures were in view, both needing behaviour-level
tests: a Rust rewrite of the CLI, for which an end-to-end corpus doubles as a
parity harness, and a framework CLI whose product spec is the per-subcommand
behaviour contract.

## Decision

Three layers. A contract corpus — one case per language-neutral data file: an
inline fixture tree, argv, expected stdout or structural asserts, exit code and
file-tree delta — run only through the `bin/booping` subprocess boundary, living
beside the commands it specifies (`booping-python/e2e/`, `booping-tracker/e2e/`,
runner `pytest-txtar`). A small unit core for algorithmic hotspots only: wave
resolution, `--where` parsing, config deep-merge, frontmatter edges. Snapshots plus
mdcheck own rendered wording and structure. Tests assert structure — exit codes,
frontmatter keys, JSON, headings present — never exact prose; internal-import
tests are converted when their command is touched and deleted in the same change.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Contract corpus through the CLI](#contract-corpus-through-the-cli) | accepted | medium | medium | Survives a rewrite; reads as the spec |
| [Unit tests over internals](#unit-tests-over-internals) | rejected | low | high | Coupled to module structure and wording |

### Contract corpus through the CLI

Cases drive the real binary and compare its observable effects.

- **Pros:** the same corpus can run unchanged under a future Rust runner; cases are
  readable as the product spec without running them; refactors do not break them.
- **Cons:** a subprocess per case; a pilot and a harness to build first.
- **Complexity:** medium.
- **Reversibility:** medium.

### Unit tests over internals

Tests import modules and assert on functions and rendered strings.

- **Pros:** fast and precise for algorithms.
- **Cons:** dead weight on any rewrite; prose assertions break on wording and
  duplicate the snapshot coverage.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- `just e2e` runs both corpora; `--txtar-update` rebaselines the selected cases.
- `create` is verified in the corpus, not by the unit tests.
