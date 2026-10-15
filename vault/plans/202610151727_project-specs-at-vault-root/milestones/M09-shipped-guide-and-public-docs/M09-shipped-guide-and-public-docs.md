---
id: "09"
title: "Shipped specs guide and public docs"
sp: 3
status: pending
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M09: Shipped specs guide and public docs

The shipped specs guide and the docs site tell a booping user that project records live at the vault root, that only type directories count as records there, and how to keep them in the repo instead.

**Scope**:

- `src/specs/README.md` — the Tiers table's project row: the vault root, type directories beside `plans/`; or a repo directory set by `core.specs.tiers.project.path`, linked into the vault as `{vault}/specs` by `booping specs init`. The Check section's `layout` bullet: a tier rooted at the vault reads only type directories and ignores the rest of the vault.
- `playbooks/setup/setup-project/opus-5.md` — the already-initialized example's `specs:` line shows the vault root.
- `documentation/project_config.md`, `documentation/install.md`, `documentation/specs.md` — every statement of the old default, and the example output paths, follow; `documentation/specs.md` names migration 005 in one sentence (existing vaults are moved by `/playbook migrate`; a repo-pointed tier is left alone).

Audience filter (`booping:rule/0008`): only what a booping user touches — where records live, keeping them in a repo, the migration. No internal churn: no `tiers.py`, no flag names, no fixture or test talk.

Tests: the docs build.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Shipped guide; setup example line. | `src/specs/README.md`, `playbooks/setup/setup-project/opus-5.md` | 1 | pending |
| 9.2 | The three docs pages. | `documentation/project_config.md`, `documentation/install.md`, `documentation/specs.md` | 2 | pending |

## Definition of Done

### Task 9.1

- [ ] The guide's project row and `layout` bullet say what Scope says; no sentence places the default at `{vault}/specs`.

### Task 9.2

- [ ] No page states `{vault}/specs` or `vault/specs/` as the default; the migration sentence is present once.
- [ ] Nothing in the changed text names an internal module, flag or test.

Return: the list of changed files, nothing else.

## References

- `documentation/specs.md` — the page's existing voice.

## Verify

`just docs`
