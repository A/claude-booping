---
id: "07"
title: "Docs for rule-writing learn, specs init and setup"
sp: 3
status: done
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M07: Docs for rule-writing learn, specs init and setup

User docs and the README describe learn writing rule records, `booping specs init`, and setup's specs tiers and namespace — and nothing internal beyond what a user runs or reads.

**Scope**: `documentation/learn.md`, `documentation/specs.md`, `documentation/project_config.md` (the `core.specs.tiers.global.namespace` key), `documentation/install.md` / `documentation/quick_start.md` (setup's new questions and created tiers, only where they describe setup), `README.md` (learn's destinations), `docs/how_to_initialize_project.md` if it lists what setup creates. Lesson-injection docs are out of scope (C11). Audience: users of booping (`vault/specs/reference/0001-audience.md`) — only commands they run and files they see; no module names, no partial paths ([rule/0008](../../../../specs/rule/0008-audience-scoped-content.md)).

Tests: none — prose; `just docs` builds.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | `documentation/learn.md` and README: destinations are a rule record in the project specs tier and the repo `CLAUDE.md`; review table columns per C12; what a learnt rule looks like (targets, brief, link to the record). | `documentation/learn.md`, `README.md` | 2 | done |
| 7.2 | `specs init` in `documentation/specs.md`; namespace key in `documentation/project_config.md`; setup's namespace question and tiers in install / quick_start / `docs/how_to_initialize_project.md` where they describe setup. | `documentation/specs.md`, `documentation/project_config.md`, `documentation/install.md`, `documentation/quick_start.md`, `docs/how_to_initialize_project.md` | 1 | done |

## Definition of Done

### Task 7.1

- [x] No sentence says learn writes a lesson or `_lessons/`.
- [x] No module, class, partial or template path appears in the user docs.

### Task 7.2

- [x] `just docs` builds without warnings about the touched pages.

Return: the list of changed files, nothing else.

## References

- `documentation/specs.md` — current page tone and depth.
- `vault/specs/reference/0003-documentation-surfaces.md` — surface depth ceilings.

## Verify

`just docs`
