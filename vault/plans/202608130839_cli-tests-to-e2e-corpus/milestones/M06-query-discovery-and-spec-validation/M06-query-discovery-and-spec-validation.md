---
id: "06"
title: "query corpus — discovery, slug identity, spec validation, root"
sp: 4
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M06: query corpus — discovery, slug identity, spec validation, root

Discovery, slug identity, spec validation and the `root: core` escape hatch are covered by txtar cases instead of direct `booping.query` calls.

**Scope**: the semantics `tests/query_test.py` asserts in `TestSlugFor` (3), `TestDiscover` (3), `TestRun` (6), `TestQuerySpec` (6) and `TestRoot` (5). Slug identity is observable because it drives both de-duplication across globs and the default row order. Files: new `booping-python/e2e/cases/query/*.txtar`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Discovery and slug cases: a pattern ending in a literal filename takes the directory name as slug, a wildcard final segment takes the file stem, a single-segment pattern takes the stem; one entry per slug with the earlier glob winning, and reversing the glob order flipping the winner; directories matching a pattern are not rows | `booping-python/e2e/cases/query/*.txtar` | 2 | done |
| 6.2 | Row-shape and ordering cases: rows carry their frontmatter plus `path` and `slug`, with `path` relative to the query root; rows come back slug-sorted when no `sort` is declared; one row per slug across overlapping globs | `booping-python/e2e/cases/query/*.txtar` | 1 | done |
| 6.3 | Spec-validation and root cases: an unknown spec key is rejected rather than silently dropped; an unknown `root:` names the value and the legal set; `root: core` globs the plugin root, needs no vault, and returns plugin-root-relative paths; omitting `root` keeps vault resolution | `booping-python/e2e/cases/query/*.txtar` | 1 | done |

## Definition of Done

### Task 6.1

- [x] A `plans/*/index.md` spec returns rows whose `slug` is the plan directory name, not `index`.
- [x] A `plans/*/*.md` spec returns rows whose `slug` is each file's stem.
- [x] A single-segment pattern (`*.md` at the vault root) returns rows slugged by stem.
- [x] A spec declaring two overlapping globs returns one row per slug, and the row comes from the earlier glob.
- [x] The same spec with its globs reversed returns the row from the other glob, proving order decides the winner.
- [x] A pattern that also matches a directory returns only the files.

### Task 6.2

- [x] `--output json` rows carry every frontmatter key of the file plus `path` and `slug`.
- [x] `path` is relative to the query root — the attached vault by default, the `--project` directory when one is pinned.
- [x] A spec with no `sort` returns rows in slug order rather than filesystem order.

### Task 6.3

- [x] A config spec carrying an unknown key exits 1 with a message naming the key, rather than running with it dropped.
- [x] A spec with `root: bogus` exits 1 and the message names both the value and the legal set.
- [x] A `root: core` spec runs outside any project, exits 0, and returns paths relative to the plugin root.
- [x] The same spec without `root` run outside any project exits 2 with the no-vault-resolved message, proving `root: core` is what lifts the requirement.

## Verify

```
cd booping-python && uv run pytest e2e -k query
```

Every case in this milestone passes with no `--txtar-update` needed.
