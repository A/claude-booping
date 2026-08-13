---
id: "08"
title: "render-playbook cross-check and unit deletion"
sp: 3
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M08: render-playbook cross-check and unit deletion

Every test in `tests/test_render_playbook.py` maps to a named corpus case or to a recorded, justified drop; then the file and its fixture tree are deleted.

**Scope**: closing the `render-playbook` half. Files: deleted `booping-python/tests/test_render_playbook.py` and `booping-python/tests/__fixtures__/render-playbook-home/`; new gap cases under `booping-python/e2e/cases/render-playbook/`; edited `booping-python/e2e/README.md`. The cross-check is the milestone's real work — deletion is what it authorises. `tests/__fixtures__/playbook-transition-home/` is untouched here.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Build the cross-check table: every one of the 131 tests against the case that replaces it, the milestone that wrote it, or a one-line reason it is dropped (covered by `tests/context/playbook_test.py`, or inexpressible in the sandbox). Write any case the table exposes as missing | `booping-python/e2e/cases/render-playbook/*.txtar` | 2 | pending |
| 8.2 | Delete `tests/test_render_playbook.py` and the `render-playbook-home` fixture tree, confirm no other consumer, and record the cross-check table in the milestone body and the commit message | `booping-python/tests/test_render_playbook.py`, `booping-python/tests/__fixtures__/render-playbook-home/`, `booping-python/e2e/README.md` | 1 | pending |

## Definition of Done

### Task 8.1

- [ ] The table has one row per test function in the file — 131 rows, and the count is verified mechanically, not by eye: the row count of the table equals `git show HEAD:booping-python/tests/test_render_playbook.py | grep -c '^def test_'`, and every test name from that same listing appears verbatim in a row. Both comparisons are run again after deletion, against `git show`, and their output is pasted into the commit message.
- [ ] Every row names either a `.txtar` case file that exists on disk, or a drop reason; no row is blank and none says "covered elsewhere" without naming the file and test.
- [ ] Any behaviour with no case gets one written in this milestone, in the case directory of the section it belongs to.
- [ ] A behaviour found to be untested before the migration is written as a gap case; any bug the porting exposes is recorded in this milestone body and left unfixed.

### Task 8.2

- [ ] `rg -n "render-playbook-home|test_render_playbook" booping-python` returns nothing outside the corpus and this plan.
- [ ] Both paths are deleted and `uv run pytest tests` passes.
- [ ] `just e2e` passes with the render-playbook case directory collected.
- [ ] `booping-python/e2e/README.md` gains the executable-hook `chmod` note only if M10 has already landed it; otherwise this milestone leaves the README alone.
- [ ] The cross-check table is committed — in this milestone file and referenced from the commit message.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook -q && uv run pytest tests/utils_test.py tests/context/playbook_test.py -q && rg -n "render-playbook-home|test_render_playbook" . ; echo "rg exit: $?"
```

The corpus and the two remaining consumers of what this milestone touched are green, and `rg` exits 1 — no reference to the deleted file or its fixture tree survives.
