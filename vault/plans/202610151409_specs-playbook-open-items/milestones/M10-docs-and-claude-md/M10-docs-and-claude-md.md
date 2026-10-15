---
id: "10"
title: "Docs, README and CLAUDE.md name the specs playbook and open items"
sp: 3
status: pending
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M10: Docs, README and CLAUDE.md name the specs playbook and open items

The public docs, the README and CLAUDE.md describe `/playbook specs` and open items as shipped.

**Scope**: public docs, audience = booping users ([booping:rule/0008](../../../../../specs/rule/0008-audience-scoped-content.md) — what they call and see, no internal churn): `documentation/specs_playbook.md` (new — what the guide does, its scenarios in a sentence each, open items and the `open-items` verbs, the plan link) and its `mkdocs.yml` `nav` entry beside the other playbook pages; `documentation/specs.md` gains a short "Open items" section linking the new page; `documentation/project_config.md` documents `core.specs.open_items`; `README.md` names `specs` where it lists playbooks. Internal: this repo's `CLAUDE.md` per `index.md` `## CLAUDE.md impact`.

Tests: none — docs; `just docs` builds.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Public docs page, nav, specs page section, config reference, README. | `documentation/specs_playbook.md`, `mkdocs.yml`, `documentation/specs.md`, `documentation/project_config.md`, `README.md` | 2 | pending |
| 10.2 | CLAUDE.md sections. | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 10.1

- [ ] Only what a user calls or sees: no module names, no e2e cases, no milestone history.
- [ ] `just docs` builds with no new warning.

### Task 10.2

- [ ] Every CLAUDE.md change listed in `index.md` `## CLAUDE.md impact` is made; no literal statuses typed where the machine is the source.

Return: the list of changed files, nothing else.

## References

- `documentation/learn.md` — a playbook page's shape.
- `documentation/project_config.md` — the `core.specs` entry to extend.

## Verify

`just docs`
