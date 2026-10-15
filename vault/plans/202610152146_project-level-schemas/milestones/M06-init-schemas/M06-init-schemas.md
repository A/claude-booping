---
id: "06"
title: "booping specs init --schemas copies a shipped schema set into a tier"
sp: 3
status: pending
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M06: booping specs init --schemas copies a shipped schema set into a tier

`booping specs init --tier global|project --schemas ru` copies the shipped Russian set into the tier's `_schemas/`.

**Scope**: `commands/specs.py` `init` verb gains `--schemas SET` (help: `copy the shipped schema set schemas-SET into the tier's _schemas/`). `specs/init.py` `plan()` takes the set name: sets are the `schemas-*` directories under `core.specs.format` (discovered, C8); one `dir` action for `{tier root}/_schemas/` when missing and one `file` action per `*.yaml` of the set, appended after the tier's own actions — also for a vault-rooted tier, whose plain `init` writes nothing. Any target file already present → `InitError` `{path} exists; init writes nothing` before anything is applied. Unknown set → `InitError` `unknown schema set {set}: one of {sets joined by ', '}`. Both print `error: …` on stderr, exit 1, as `init`'s existing errors do. Output lines are `init`'s existing `created dir …` / `created file …`.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): `init --tier project --schemas ru` on a vault-rooted tier creates `{vault}/_schemas/` and the eight files (expected stdout the nine lines; one `expected/` file asserted byte-for-byte, `rule.yaml`); `init --tier global --schemas ru` creates `_specs/`, its README and `_specs/_schemas/*`; an existing `_schemas/rule.yaml` → exit 1, error line, nothing written; `--schemas xx` → exit 1 naming `ru`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `--schemas` flag, set discovery, copy actions and the two errors. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/init.py` | 2 | pending |
| 6.2 | The four e2e cases above. | `booping-python/e2e/cases/specs/init-schemas-*.txtar` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] `bin/booping specs init --help` shows `--schemas SET`.
- [ ] Without `--schemas`, the three existing `init` cases pass unchanged.

### Task 6.2

- [ ] The cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/specs/init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` — output and `expected/` shape.
- `booping-python/e2e/cases/specs/init-a-conflicting-vault-specs-writes-nothing.txtar` — the all-or-nothing error shape.

## Verify

`cd booping-python && uv run pytest e2e/cases/specs -q -k init`
