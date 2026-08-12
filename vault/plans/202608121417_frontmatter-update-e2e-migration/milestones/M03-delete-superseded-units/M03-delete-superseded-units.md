---
id: "03"
title: "Delete superseded unit tests after coverage cross-check"
sp: 2
status: pending
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M03: Delete superseded unit tests after coverage cross-check

Goal: `booping-python/tests/commands/frontmatter_update_test.py` is deleted with a recorded proof that every CLI-observable behavior it covered maps to a named corpus case, and the repo carries no stale reference to it.

Scope: deletion of the unit file; a coverage cross-check table appended to this milestone file; a stale-reference sweep. No production code changes. Context the cross-check needs: `TestHookTokenising` is dropped deliberately — it tests `playbook_transition.dispatch_frontmatter_update`, whose coverage lives in `tests/commands/playbook_transition_test.py` (`test_file_target_hook_updates_sibling_file`, `test_file_target_hook_interpolates_instance`); the live-git macro test is consciously abandoned per plan decision (real-execution case M02/2.3 replaces it).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Cross-check: list every test in `frontmatter_update_test.py`, map each to its corpus case filename or to a recorded drop rationale (hook-tokenising → playbook_transition coverage; live-git → M02/2.3); append the mapping table under `## Coverage cross-check` in this file | this milestone file | 1 | pending |
| 3.2 | Delete `booping-python/tests/commands/frontmatter_update_test.py`; sweep stale references (`grep -rn frontmatter_update_test` over the repo) and fix any hit; confirm unit suite still green | `booping-python/tests/commands/frontmatter_update_test.py` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] Every test function/parametrization in the unit file appears in the mapping table with a case filename or drop rationale.
- [ ] No mapping row says "TODO" or "covered somewhere".

### Task 3.2

- [ ] File deleted; `grep -rn frontmatter_update_test` over the repo returns nothing.
- [ ] `uv run pytest tests` and `uv run pytest e2e -k frontmatter` both green after deletion.

## Verify

```
cd booping-python && uv run pytest tests/commands -q && uv run pytest e2e -k frontmatter -q
grep -rn frontmatter_update_test /home/anton/Dev/@A/claude-booping --include='*.py' --include='*.md' --exclude-dir=vault
```

Command-unit suite green without the deleted file, corpus green, the grep prints nothing.
