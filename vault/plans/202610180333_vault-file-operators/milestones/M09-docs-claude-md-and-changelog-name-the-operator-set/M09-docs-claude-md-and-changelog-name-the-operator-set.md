---
id: "09"
title: "Docs, CLAUDE.md and CHANGELOG name the operator set"
sp: 3
status: pending
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M09: Docs, CLAUDE.md and CHANGELOG name the operator set

## Tasks

**Goal**: every doc surface names `set`, `transition`, `state`, `config`, `next_id`, `specs scan`, and none names a removed command.
**Scope**: `CLAUDE.md` (Commands sub-list, Playbooks run-state bullets, Lifecycle bullets naming `booping items`/`playbook-transition`), `README.md`, `documentation/*.md` (playbook, project_config, project_manager, specs_playbook, specs, vault, groom, develop), `CHANGELOG.md` Unreleased (Breaking: the renamed and removed commands), `booping-tracker/README.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | CLAUDE.md and README: the operator set with one capability phrase each; run-state wording; open-items lifecycle via operators | `CLAUDE.md`, `README.md` | 1 | pending |
| 9.2 | documentation pages and booping-tracker README; anchors that move are relinked | `documentation/playbook.md`, `documentation/project_manager.md`, `booping-tracker/README.md` | 1 | pending |
| 9.3 | CHANGELOG Unreleased: one Breaking line listing old → new commands and the removal of `booping items`, audience: plugin users only | `CHANGELOG.md` | 1 | pending |

Tests: none beyond `just docs` and the stale-name grep.

## Definition of Done

- [ ] Task 9.1: `grep -n 'frontmatter-update\|marker-set\|playbook-transition\|playbook-state\|config-get\|booping items' CLAUDE.md README.md` returns nothing.
- [ ] Task 9.2: `just docs` builds strict; `grep -rn` of the same names in `documentation/` returns nothing.
- [ ] Task 9.3: the CHANGELOG line names each old command with its replacement and nothing internal.

## References

- `CHANGELOG.md` — Unreleased section shape.

## Verify

`just docs`
