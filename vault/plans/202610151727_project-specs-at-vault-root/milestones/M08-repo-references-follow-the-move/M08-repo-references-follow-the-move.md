---
id: "08"
title: "Repo references follow the move"
sp: 4
status: in-progress
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M08: Repo references follow the move

No live file in the repo names `vault/specs/` or the old `{vault}/specs` default any more; the core tier's links reach the moved records.

**Scope**:

- `CLAUDE.md` — the four lines naming `vault/specs/` or the null default (`just specs-check`, `core.specs`, Layout, the Vault section): booping's project tier is the vault root's type directories; `path: null` → the vault root.
- Core rules `specs/rule/0001`, `0004`, `0006`, `0007`, `0009`, `0010`, `0030`, `0031` — `## Follows from` links `../../vault/specs/{type}/` → `../../vault/{type}/`.
- `vault/adr/0001-specs-tiers.md` — the Decision's core bullet and the 2026-10-15 Consequences line say booping's project tier is the vault root's type directories; `updated_at` today.
- The local docs playbook: `vault/_playbooks/docs/targeting/opus-5.md`, `research/opus-5.md`, `roles/fable-5.md`, `targets/fable-5.md`, `sync-specs/opus-5.md` — record paths `vault/{type}/…`; `vault/_playbooks/docs/_scripts/commit-docs` — its pathspec covers the vault's existing type directories, the type list derived from the schema stems under `core.specs.format`, never hand-written.

History stays as written: `vault/plans/`, `retrospectives/`, `codereviews/`, `_runs/`, `researches/`, `playbooks/*/_specs/`. The expected drift of `vault/_playbooks/docs/_reports/output.md` is the record-path change only; the runner accepts it.

Tests: integration — `specs check --tier core` link check; a grep for the old path over the live surfaces.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | CLAUDE.md, core rule links, adr/0001. | `CLAUDE.md`, `specs/rule/*.md`, `vault/adr/0001-specs-tiers.md` | 2 | pending |
| 8.2 | Docs playbook step bodies and `commit-docs`. | `vault/_playbooks/docs/*/opus-5.md`, `vault/_playbooks/docs/*/fable-5.md`, `vault/_playbooks/docs/_scripts/commit-docs` | 2 | pending |

## Definition of Done

### Task 8.1

- [ ] `bin/booping specs check --tier core` exits 0.
- [ ] CLAUDE.md states the vault-root default once, in the `core.specs` line.

### Task 8.2

- [ ] `commit-docs` stages `vault/value`, `vault/rule` … that exist and nothing under a removed `vault/specs`.

Return: the list of changed files, nothing else.

## References

- `vault/_playbooks/docs/_scripts/commit-docs` — the pathspec block to replace.

## Verify

`bin/booping specs check --tier core && ! grep -rn 'vault/specs/' CLAUDE.md specs vault/_playbooks vault/adr vault/rule vault/README.md`
