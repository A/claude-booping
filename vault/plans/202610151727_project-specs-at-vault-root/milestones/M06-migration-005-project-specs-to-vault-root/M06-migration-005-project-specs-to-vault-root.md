---
id: "06"
title: "Migration 005 \u2014 project specs move to the vault root"
sp: 4
status: pending
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M06: Migration 005 — project specs move to the vault root

`migrations/005_project_specs_to_vault_root/migration.md` ships at id 5: on a vault holding `{vault}/specs/{type}/` under the default tier it moves every type directory to the vault root and re-points the relative links inside the moved records; on any other vault it changes nothing, or pins the tier where the old default put it.

**Scope**: the migration file, in the shape of migration 004 — frontmatter `id: 5`, `title`, `summary`; then an intro, `## Setup` (`PLUGIN_ROOT`, `VAULT`, `REPO`; the types are the stems of `$PLUGIN_ROOT/src/specs/schemas/*.yaml`, never a hand list), one numbered section per case, `## Verify`, `## Report`. Cases, judged in this order, the first match wins:

1. `booping config-get core.specs.tiers.project.path` is not null — a repo-pointed tier: change nothing, report `left alone: path {value}`.
2. `$VAULT/specs` is a symlink — the old out-of-repo default, made by `specs init`: set `core.specs.tiers.project.path` in `$VAULT/config.yaml` to the link target relative to `$REPO`, keeping every other key and comment, keep the link; report `pinned: {path}`.
3. `$VAULT/specs` is absent, the vault sits outside the repo and `$REPO/specs/` holds a type directory — pin `path: specs` the same way.
4. `$VAULT/specs` is a directory holding at least one type directory — move. First, any `$VAULT/{type}` that already exists for a type to move fails the migration before anything moves, naming each collision. Then rename each `$VAULT/specs/{type}` to `$VAULT/{type}` (no git — migrate owns commits). Then one Python block — run as `python3 - <<'EOF'`, standard library only (`pathlib`, `os.path`, `re`), Python 3.11+ — re-points the links of every moved `.md`: each inline `](target)` with no `://`, not starting with `#` or `/`, has its anchor split off, is resolved against the file's old directory, mapped from `$VAULT/specs/{type}/…` to `$VAULT/{type}/…` when it lay there, and rewritten as the relative path from the file's new directory plus the anchor; a target that did not exist before the move is left as is and listed. What remains in `$VAULT/specs/` (a README, other files) stays and is listed; `$VAULT/specs` is removed only when empty. Links from other vault files into `specs/{type}/` are listed with `grep`, not rewritten — plans, retros and reviews stay as they were written.
5. Otherwise — `nothing to move`.

A second run lands in case 5 (or 1 after a pin), so re-running changes nothing. `## Verify`: `booping specs check --tier project` reports no `link` finding in a moved record. `## Report`: one line per action — moved, re-pointed link count per file, pinned, left alone, listed leftovers, listed inbound links.

Also `playbooks/_fixtures/vault/.booping` `latest_migration: 4` → `5`, as its own comment asks.

Tests: the migration body is agent-executed prose; its moves and link re-pointing are proven on booping's own vault in M07 (`specs check`'s link check over every record). `booping-python/tests/migrations_test.py` follows if it asserts the shipped id set.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | The migration file per Scope. | `migrations/005_project_specs_to_vault_root/migration.md` | 3 | pending |
| 6.2 | Fixture watermark; migrations test if it pins the id set. | `playbooks/_fixtures/vault/.booping`, `booping-python/tests/migrations_test.py` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] The five cases appear in the order above, each with its report line.
- [ ] The link re-pointing is one fenced Python block, standard library only.
- [ ] No step touches git or the `.booping` marker.

### Task 6.2

- [ ] The fixture marker reads `latest_migration: 5`.

Return: the list of changed files, nothing else.

## References

- `migrations/004_lessons_to_rules/migration.md` — section shape, `## Setup` block, no-op wording.
- `playbooks/makemigration/playbook.md` — the format `migrate` consumes.

## Verify

`bin/booping query --config core.migrate_playbook.queries.pending --where id:gt=4 --columns id,title`
