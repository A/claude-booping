---
id: "03"
title: "booping specs open-items list renders the index"
sp: 2
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M03: booping specs open-items list renders the index

`booping specs open-items list` prints the open and planned items as the table of `index.md` `## I/O contract` → `list`; `--all` adds closed ones.

**Scope**: `list [--all]` in `booping-python/src/booping/commands/specs.py`, rendering through `core.specs.open_items.index` with the query engine (`booping-python/src/booping/query.py`) in-process; the default filter is `status` in the machine's non-terminal statuses read from `playbooks/specs/playbook.yaml` (no status literal in code); null cells render `—`; no rows → `no open items`.

Tests: integration tier, txtar cases — empty vault prints `no open items`; a vault with one item each `open`, `planned`, `done`, `dropped` lists two rows by default and four with `--all`, sorted by id.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `list` and `--all` over the index query spec, plus the two cases. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/open_items.py`, `booping-python/e2e/cases/specs/open-items-list-*.txtar` | 2 | done |

## Definition of Done

### Task 3.1

- [x] Columns exactly `id | status | direction | record | title | plan`, markdown table, sorted by id.
- [x] The default filter derives from the machine's terminal statuses, not a hardcoded list.
- [x] Both cases pass.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/query.py` — how a config query spec is run and printed.
- `booping-python/e2e/cases/query/` — a query case to copy the fixture shape from.

## Verify

`just e2e -k "open-items-list"`
