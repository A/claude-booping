---
id: "05"
title: "Learn eval suites on rules"
sp: 3
status: pending
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M05: Learn eval suites on rules

The `extract-candidates` and `write` eval suites assert rule output: candidates routed to `Rule` with targets and a brief, and written rule records in the C5 shape.

**Scope**: `playbooks/learn/extract-candidates/{tests.yaml,promptfooconfig.yaml,_fixtures/}`, `playbooks/learn/write/{tests.yaml,promptfooconfig.yaml,_fixtures/}`; shared asserts in `playbooks/_lib/` only if an existing one names lessons. Run tier: smoke only (C10).

Tests: smoke-tier deterministic asserts — extract: a candidate table with `Brief` column, no `_lessons/` path; write: a new record at `rule/{NNNN}-{slug}.md` with the C5 keys, an update-in-place keeps the untouched body byte-identical (the `refine-existing` fixture, now a rule record), a `covered` row writes nothing.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | extract-candidates: fixture target space and asserts move to rules (`Rule` destination, `Brief` column, no lesson path). | `playbooks/learn/extract-candidates/tests.yaml`, `playbooks/learn/extract-candidates/_fixtures/` | 1 | pending |
| 5.2 | write: `accepted-table.md` in C12 columns incl. one `covered` row; `refine-existing.md` becomes a project rule record; asserts on path, frontmatter keys, byte-identical untouched body, no file for `covered`. | `playbooks/learn/write/tests.yaml`, `playbooks/learn/write/_fixtures/` | 2 | pending |

## Definition of Done

### Task 5.1

- [ ] `rg -n '_lessons' playbooks/learn/extract-candidates` returns nothing.

### Task 5.2

- [ ] `rg -n '_lessons' playbooks/learn/write` returns nothing.
- [ ] `EVAL_PR=0 just smoke learn/write` and `EVAL_PR=0 just smoke learn/extract-candidates` pass.

Return: the list of changed files and the two smoke pass/fail lines, nothing else.

## References

- `playbooks/learn/write/tests.yaml` — current assert shapes.
- `vault/specs/runbook/0002-run-eval-suites.md` — how suites run.

## Verify

`EVAL_PR=0 just smoke learn/write`
