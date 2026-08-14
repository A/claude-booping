---
id: "03"
title: "Delete superseded unit tests after coverage cross-check"
sp: 2
status: done
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M03: Delete superseded unit tests after coverage cross-check

Goal: `booping-python/tests/commands/frontmatter_update_test.py` is deleted with a recorded proof that every CLI-observable behavior it covered maps to a named corpus case, and the repo carries no stale reference to it.

Scope: deletion of the unit file; a coverage cross-check table created at `vault/plans/202608121417_frontmatter-update-e2e-migration/milestones/M03-delete-superseded-units/coverage-cross-check.md`; a stale-reference sweep. No production code changes. Context the cross-check needs: `TestHookTokenising` is dropped deliberately — it tests `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`); the live-git macro test is consciously abandoned per plan decision (real-execution case M02/2.3 replaces it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Cross-check: list every test in `frontmatter_update_test.py`, map each to its corpus case filename or to a recorded drop rationale (hook-tokenising → playbook_transition coverage; live-git → M02/2.3). Create the file below, holding a `# Coverage cross-check` heading and that one table — nothing else, and nothing in the run report | `vault/plans/202608121417_frontmatter-update-e2e-migration/milestones/M03-delete-superseded-units/coverage-cross-check.md` | 1 | done |
| 3.2 | Delete `booping-python/tests/commands/frontmatter_update_test.py`; sweep stale references (`grep -rn frontmatter_update_test` from the repo root) and fix any hit; confirm the command-unit suite still green | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `coverage-cross-check.md` exists at the path named in the task row and holds every test function/parametrization in the unit file, each with a case filename or a drop rationale.
- [x] No mapping row says "TODO" or "covered somewhere".

### Task 3.2

- [x] File deleted; the stale-reference grep returns nothing.
- [x] `uv run pytest tests/commands` and `uv run pytest e2e -k frontmatter` both green after deletion.

## References

- `vault/plans/202608111422_e2e-contract-corpus-pilot/milestones/M04-delete-superseded-tests/M04-delete-superseded-tests.md` — the same deletion-after-cross-check milestone from the scaffold pilot.
- `booping-python/tests/commands/frontmatter_update_test.py` — the file being cross-checked and deleted.
- `booping-python/e2e/cases/frontmatter-update/` — the corpus cases M01 and M02 left behind, which the table maps onto.

## Verify

```
cd booping-python && uv run pytest tests/commands -q && uv run pytest e2e -k frontmatter -q && cd .. && ! grep -rn frontmatter_update_test . --include='*.py' --include='*.md' --exclude-dir=vault --exclude-dir=.git
```

Command-unit suite green without the deleted file, corpus green, the grep prints nothing.
