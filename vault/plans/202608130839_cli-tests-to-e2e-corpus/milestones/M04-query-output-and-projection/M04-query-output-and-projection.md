---
id: "04"
title: "query corpus — output formats, projection, frontmatter warnings"
sp: 3
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M04: query corpus — output formats, projection, frontmatter warnings

All four `--output` formats, `columns` projection and the unparseable-frontmatter warning are covered by txtar cases under `e2e/cases/query/`.

**Scope**: what `booping query` prints — the four formats, the row shape each carries, table escaping, and the stderr warning path. Carries `TestColumns` (3 library units) and the CLI output tests. Files: new `booping-python/e2e/cases/query/*.txtar`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Format cases: `table` is the default; `json` is an array of objects; `yaml` round-trips; `paths` emits one vault-relative path per line | `booping-python/e2e/cases/query/*.txtar` | 1 | done |
| 4.2 | Table-rendering cases: a value containing a pipe is escaped and a value containing a newline is collapsed to a space, so one row stays one line | `booping-python/e2e/cases/query/*.txtar` | 1 | done |
| 4.3 | Projection and warning cases: a declared `columns` list keeps its keys plus `path` and `slug`; declaring `path` does not duplicate it; an empty `columns` leaves only `path` and `slug`; a file with unparseable frontmatter is skipped with a stderr warning naming it while the run exits 0 and the other rows come back | `booping-python/e2e/cases/query/*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] A query with no `--output` prints a markdown table with a header row and a separator row.
- [x] `--output json` prints an array of objects, one per row, indented.
- [x] `--output yaml` prints a YAML sequence carrying the same keys and values as the JSON case over the same fixture.
- [x] `--output paths` prints one path per line, each relative to the query root and nothing else.

### Task 4.2

- [x] A frontmatter value containing `|` renders escaped in the table so the column count is unchanged.
- [x] A multi-line frontmatter value renders as a single line with the newline collapsed to a space.

### Task 4.3

- [x] `--columns status,title` returns rows carrying exactly those keys plus `path` and `slug`.
- [x] `--columns path,status` returns `path` once, not twice.
- [x] An empty `columns` list in a config spec returns rows carrying only `path` and `slug`.
- [x] A vault holding one file with broken frontmatter and two good ones exits 0, returns the two good rows on stdout, and prints exactly one `warning: skipping {path} — unparseable frontmatter ([..])` line on stderr.
- [x] A file with no frontmatter at all yields a row carrying `path` and `slug` only, rather than being skipped.

## Verify

```
cd booping-python && uv run pytest e2e -k query
```

Every case in this milestone passes with no `--txtar-update` needed.
