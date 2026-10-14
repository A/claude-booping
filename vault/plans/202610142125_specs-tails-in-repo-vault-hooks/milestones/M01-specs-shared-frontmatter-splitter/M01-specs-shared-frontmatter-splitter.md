---
id: "01"
title: "Specs records load frontmatter through the shared splitter"
sp: 2
status: done
plan: "vault/plans/202610142125_specs-tails-in-repo-vault-hooks/index.md"
---

# M01: Specs records load frontmatter through the shared splitter

`booping specs` splits record frontmatter with `booping.context._yaml.split_frontmatter` and catches its `UnclosedFrontmatterError`; the private copy in `records.py` is gone and `booping specs check` output is unchanged.

**Scope:** `booping-python/src/booping/specs/records.py` only. Remove `_FRONTMATTER_RE` (line 16), `_UnclosedFrontmatterError` and `_split_frontmatter` (lines 50–61); `load_record` calls `split_frontmatter` and catches `UnclosedFrontmatterError`, setting `error = str(exc)` (the shared error's message is the same text the check prints today, `frontmatter block is not closed`). `_frontmatter_error` and its line arithmetic stay as they are — the shared regex also hands YAML the text after the opening line, so `frontmatter_error_line` keeps its meaning. Keep `import re` only while `_FILENAME_RE` / `_REF_RE` use it.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Replace the private splitter with the shared `split_frontmatter` / `UnclosedFrontmatterError` | `booping-python/src/booping/specs/records.py` | 2 | done |

## Definition of Done

### Task 1.1

- [x] `rg -n "_FRONTMATTER_RE|_UnclosedFrontmatterError|_split_frontmatter" booping-python/src/booping/specs` prints nothing.
- [x] `records.py` imports `split_frontmatter` and `UnclosedFrontmatterError` from `booping.context._yaml`.
- [x] The five `booping-python/e2e/cases/specs/check-frontmatter-*.txtar` cases pass unmodified — they pin the unclosed-block message, the YAML error messages and their line numbers, and a `---` inside a value not closing the block. Tests: no new test; these existing e2e cases are the regression contract (integration tier).
- [x] No `.txtar` file is rebaselined (`git diff --stat booping-python/e2e` empty).
- [x] Worker's final reply: only the list of changed files.

## References

- `booping-python/src/booping/context/_yaml.py` — `split_frontmatter`, `UnclosedFrontmatterError` (the shared helper; do not modify it).
- `booping-python/e2e/cases/specs/check-frontmatter-unclosed-block.txtar` — the pinned unclosed-block output.

## Verify

```
just e2e -k check-frontmatter
```
