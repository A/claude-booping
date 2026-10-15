---
id: "07"
title: "Booping's own records move to the vault root"
sp: 3
status: done
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M07: Booping's own records move to the vault root

Booping's project records sit at `vault/{type}/`, `vault/specs/` is gone, the repo marker is at migration 5, and the project tier checks clean.

**Scope**: from the repo root, follow `migrations/005_project_specs_to_vault_root/migration.md` against this repo's vault `vault/` (in the repo, default tier — case 4). Then the leftover `vault/specs/README.md` moves to `vault/README.md`, rewritten for its place: booping's project tier is the type directories at the vault root (`vault/{type}/`, not `vault/specs/`), and its two links become `../src/specs/README.md` and `../src/specs/README.md#check`. Then `bin/booping marker-set latest_migration=5`. This milestone dogfoods the migration and owns its fixes: a step that fails here is fixed in `migrations/005_project_specs_to_vault_root/migration.md` itself, then the migration re-run from that step (it is re-run safe); each fix is named in the return.

The core tier's links into these records break until M08; they are not this milestone's.

Tests: integration — `specs check --tier project` over the moved set, its `link` check covering every re-pointed link.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Apply migration 005 to `vault/`; fix the migration file for any step that fails. | `vault/specs/**` → `vault/{type}/**`, `migrations/005_project_specs_to_vault_root/migration.md` | 2 | done |
| 7.2 | `vault/specs/README.md` → `vault/README.md`; marker watermark. | `vault/README.md`, `.booping` | 1 | done |

## Definition of Done

### Task 7.1

- [x] `vault/specs/` does not exist; every record that was under it sits at `vault/{type}/` with the same file name.
- [x] The migration's report lines are pasted into the return.

### Task 7.2

- [x] `vault/README.md` names no `vault/specs/` path; `.booping` reads `latest_migration: 5`.

Return: the list of changed files (moves as `old → new` per type directory), plus the migration's report lines.

## References

- `migrations/005_project_specs_to_vault_root/migration.md` — the procedure.

## Verify

`bin/booping specs check --tier project`
