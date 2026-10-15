---
id: "08"
title: "The alignment guide doc"
sp: 2
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M08: The alignment guide doc

`docs/specs-alignment.md` is the lazy-loaded interview the init and alignment scenarios link: values first, then the boundaries of how the model works follow from them (adr/0024).

**Scope**: one doc under `docs/`, ≤ 60 lines: the order (values and non-values → conflicts between them → rules that follow from each value → ADRs only for choices already made), one question pattern per stage, when to write a record (`value`, `conflict`, `rule`) and that each record states only what the user said ([rule/0002](../../../../specs/rule/0002-unknown-is-marked.md) — unknowns marked `[clarify]`), and that the interview is a guide the user can leave at any point. Types and frontmatter are linked to `src/specs/README.md`, never restated.

Tests: none — prose doc; M09's init case exercises the link.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Create the alignment guide. | `docs/specs-alignment.md` | 2 | done |

## Definition of Done

### Task 8.1

- [x] ≤ 60 lines, no restated type table or frontmatter list.
- [x] The link from `playbooks/specs/guide/prompt.md` resolves to it.

Return: the list of changed files, nothing else.

## References

- `docs/clarifications.md` — a lazy-loaded internal doc's tone and length.
- `src/specs/README.md` — the format it links, never copies.

## Verify

`bin/booping render-playbook specs --step guide`
