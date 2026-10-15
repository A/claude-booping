---
id: "01"
title: "Tier schemas — each tier's effective schema set, used by booping specs check"
sp: 4
status: done
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M01: Tier schemas — each tier's effective schema set, used by booping specs check

`booping specs check` validates each record against its tier's effective schema — the shipped `{core.specs.format}/schemas/{type}.yaml` overlaid by the tier's own `{tier root}/_schemas/{type}.yaml` — so a tier overrides a shipped type's shape and adds types of its own.

**Scope**: `booping-python/src/booping/specs/tiers.py` gains the per-tier resolver: `schemas(format_dir, root) -> dict[str, Path]` — stem → path, shipped first, `{root}/_schemas/*.yaml` replacing a same stem and adding new ones (C3) — and `Tier` gains it as a field `resolve_tiers` sets; the tier's types are its sorted keys. `records.py` `load_tier` never treats a `_`-prefixed directory as a record directory in any tier (C11). `check.py` `check_tier` takes each record's schema path from its tier's map instead of the shared `format_dir`; a record whose type is not in its tier's map is the existing `layout` error. An mdcheck exit 2 on a tier-owned schema (a path under `{root}/_schemas/`) becomes one `schema` error finding on that schema file — message mdcheck's first stderr line — and that type's remaining records are skipped for the schema check in this run; exit 2 on a shipped schema stays the internal error (C6). `commands/specs.py` `_run_check` passes tiers, not one type list. The `values`/`rules`/`supersedes` `ref` check keeps resolving against the target tier's records.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): a project tier with `_schemas/rule.yaml` requiring `## Правило` / `## Следует из ценностей` passes a Russian-headed rule and flags an English-headed one with a `schema` error; the same Russian rule in a tier without `_schemas/` fails with the shipped schema's `schema` error; a global tier's `_schemas/rule.yaml` does not reach the project tier (project still checked by the shipped schema); a `_schemas/rule.yaml` with an unknown key gives one `schema` error on that file and exit 1. `tests/specs/tiers_test.py` gains a unit test of the overlay (override + add), `test_types_lists_shipped_schemas` stays green.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Per-tier schema resolver on `Tier`; `_`-prefixed directories skipped by `load_tier`. | `booping-python/src/booping/specs/tiers.py`, `booping-python/src/booping/specs/records.py`, `booping-python/tests/specs/tiers_test.py` | 2 | done |
| 1.2 | `check_tier` uses the tier's schema map; tier-schema load failure as a `schema` finding. | `booping-python/src/booping/specs/check.py`, `booping-python/src/booping/commands/specs.py` | 1 | done |
| 1.3 | The four e2e cases above. | `booping-python/e2e/cases/specs/check-*.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `schemas(format_dir, root)` returns the shipped map when `{root}/_schemas/` is absent, replaces a same stem and adds a new stem when present — unit-tested.
- [x] A `_schemas/` directory in a tier not rooted at the vault yields no record and no `layout` finding.

### Task 1.2

- [x] `just specs-check` on this repo is unchanged (no `_schemas/` in either tier).
- [x] A broken tier schema → exactly one finding `{path}:1  error  schema  {mdcheck message}` for the schema file, exit 1; a broken shipped schema → exit 2 as before.

### Task 1.3

- [x] The four cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/specs/ls-tier-global-reads-the-home-dir-specs.txtar` — global-tier fixture shape.
- `booping-python/e2e/cases/specs/init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` — project-tier fixture shape (`.booping` marker, vault config).
- `src/specs/schemas/rule.yaml` — the shipped schema a test override translates.

## Verify

`cd booping-python && uv run pytest tests/specs e2e/cases/specs -q`
