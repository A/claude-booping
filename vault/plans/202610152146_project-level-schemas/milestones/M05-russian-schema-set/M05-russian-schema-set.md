---
id: "05"
title: "Structural headings are English in every tier"
sp: 3
status: done
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M05: Structural headings are English in every tier

**Owner decision 2026-10-15 — replaces the Russian schema set.** No translated schema set is shipped. Records may be written in any language, but their structural headings, bold labels, table columns and frontmatter keys stay the shipped English ones, so one schema set serves every project.

**Scope**: state this in `src/specs/README.md` (one short paragraph under Files or Body: content in any language; headings, labels, columns and keys are the shipped English ones; a tier's own schemas are for its own types and fields, not for translation). No `src/specs/schemas-ru/`.

## Definition of Done

- [x] `src/specs/README.md` states the rule in ≤ 4 lines.
- [x] No `src/specs/schemas-ru/` exists.

## Verify

- `rg -n "schemas-ru" src/ documentation/ booping-python/ || true` prints nothing.
