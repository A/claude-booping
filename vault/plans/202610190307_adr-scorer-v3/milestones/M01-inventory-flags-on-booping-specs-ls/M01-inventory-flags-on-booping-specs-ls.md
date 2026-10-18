---
id: "01"
title: "Inventory flags on booping specs ls"
sp: 5
status: done
plan: "plans/202610190307_adr-scorer-v3/index.md"
---

# M01: Inventory flags on booping specs ls

## Tasks

**Goal:** `booping specs ls` prints a tier's value/rule/adr inventory without the draft, with titles. **Scope:** `booping-python/src/booping/commands/specs.py`, its e2e corpus, `documentation/specs.md`; default output unchanged for every existing caller.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `--type` becomes repeatable (`action="append"`), each value checked as today; `--exclude REF` (repeatable, `{type}/{NNNN}`) drops those records; `--titles` prints `{type}/{NNNN}  {status}  {title}: {summary}`. Help line of `ls` names the `--titles` shape | `booping-python/src/booping/commands/specs.py` | 2 | done |
| 1.2 | e2e txtar case(s) under the existing specs cases: two types plus an exclude plus `--titles` over a small tier; an unknown type in a repeated `--type` still errors as today | `booping-python/e2e/cases/specs/` | 2 | done |
| 1.3 | The `specs ls` entry in the public docs names the three flags | `documentation/specs.md` | 1 | done |

Test surface: the `booping specs ls` CLI; cases — repeated type, exclude, titles line, unknown type; tier — e2e (txtar, integration).

Worker returns: the list of changed files and the Verify exit status.

## Definition of Done

Task 1.1
- [x] `booping specs ls --type value --type adr` lists both types, sorted by type then number.
- [x] `--exclude adr/0003` removes exactly that record; a ref not in the tier is ignored.
- [x] `--titles` line is `{type}/{NNNN}  {status}  {title}: {summary}`; without it output is byte-identical to today.

Task 1.2
- [x] New txtar case passes; existing specs cases pass unchanged.

Task 1.3
- [x] `documentation/specs.md` names `--type` (repeatable), `--exclude`, `--titles` and the titles line shape; no internal churn (rule booping:rule/0008).

## References

- `booping-python/src/booping/commands/specs.py` `_run_ls` (line ~215) and the `ls` parser (line ~46).
- An existing case in `booping-python/e2e/cases/specs/` for the txtar shape.

## Verify

`just e2e -k specs`
