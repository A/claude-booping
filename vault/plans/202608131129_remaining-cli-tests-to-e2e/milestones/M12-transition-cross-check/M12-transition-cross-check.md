---
id: "12"
title: "playbook-transition cross-check and unit deletion"
sp: 2
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M12: playbook-transition cross-check and unit deletion

Every test in `tests/commands/playbook_transition_test.py` maps to a named corpus case or a recorded drop; then the file is deleted, with its fixture tree left in place for its other consumers.

**Scope**: closing the `playbook-transition` half and the sprint. Files: deleted `booping-python/tests/commands/playbook_transition_test.py`; new gap cases under `booping-python/e2e/cases/playbook-transition/`. `tests/__fixtures__/playbook-transition-home/` is **kept** — `tests/commands/playbook_state_test.py` and `tests/commands/playbook_run_integration_test.py` both plant from it and are out of this plan's scope.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 12.1 | Build the cross-check table over all 46 tests — case that replaces it, milestone that wrote it, or a one-line drop reason — and write any case it exposes as missing | `booping-python/e2e/cases/playbook-transition/*.txtar` | 1 | pending |
| 12.2 | Delete the unit file, confirm the fixture tree's remaining consumers still pass, and record the table in the milestone body and the commit message | `booping-python/tests/commands/playbook_transition_test.py` | 1 | pending |

## Definition of Done

### Task 12.1

- [ ] The table has one row per test function — 46 rows, verified mechanically: the row count equals `git show HEAD:booping-python/tests/commands/playbook_transition_test.py | grep -c '^def test_'`, and every test name from that listing appears verbatim in a row. Both comparisons are re-run after deletion, against `git show`, and pasted into the commit message.
- [ ] Every row names an existing `.txtar` file or a drop reason naming the file and test that covers it instead; `test_cli_end_to_end` is mapped to the corpus case that subsumes it.
- [ ] Any behaviour with no case gets one written here; any bug the porting exposes is recorded in this milestone body and left unfixed.

### Task 12.2

- [ ] `tests/commands/playbook_transition_test.py` is deleted and `rg -n "playbook_transition_test" booping-python` returns nothing.
- [ ] `tests/__fixtures__/playbook-transition-home/` still exists, and `uv run pytest tests/commands/playbook_state_test.py tests/commands/playbook_run_integration_test.py` passes.
- [ ] The cross-check table is committed — in this milestone file and referenced from the commit message.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-transition -q && uv run pytest tests/commands/playbook_state_test.py tests/commands/playbook_run_integration_test.py -q && rg -n "playbook_transition_test" . ; echo "rg exit: $?"
```

The corpus passes, the fixture tree's remaining consumers pass, and `rg` exits 1 — no reference to the deleted file survives.
