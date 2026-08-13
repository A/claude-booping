---
id: "04"
title: "the run walk and the fixture-home retirement"
sp: 3
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M04: the run walk and the fixture-home retirement

The full outer-plus-instance run walk becomes one multi-`cmd` case, both `tests/commands/` state files are deleted, and the shared fixture home goes with them.

**Scope**: the interleaved `playbook-transition` + `playbook-state` walk, the deletion of `tests/commands/playbook_state_test.py` and `tests/commands/playbook_run_integration_test.py`, and the deletion of `tests/__fixtures__/playbook-transition-home/`. Files: new `booping-python/e2e/cases/playbook-state/run-walk.txtar`; deleted `booping-python/tests/commands/playbook_state_test.py`, `booping-python/tests/commands/playbook_run_integration_test.py`, `booping-python/tests/__fixtures__/playbook-transition-home/`; edited `booping-python/tests/commands/playbook_state_writes_nothing_test.py` (new, holding the one surviving unit).

Depends on M02 and M03: the unit file cannot be deleted until every argv-expressible test it holds has a case. One test is **not** expressible and must survive — `test_report_writes_nothing` snapshots `st_mtime` and `st_size`, and the runner reads only the files named in an `expected/` section, so a case can show identical bytes but cannot tell "not written" from "rewritten identically".

Deleting the fixture home is safe only if nothing else reads it: `filer/`, `scripter/` and the top-level `_scripts/` entries under that tree have no consumer once these two files are gone. The task verifies this by grep rather than by assumption.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Write the run-walk case: bootstrap the outer machine, snapshot the frontier mid-run, advance both instances of the subgraph machine, advance the outer machine, then snapshot the all-done frontier — one case, consecutive `cmd` lines, with a leading `chmod +x` for every seeded hook script | `booping-python/e2e/cases/playbook-state/run-walk.txtar` | 2 | pending |
| 4.2 | Move `test_report_writes_nothing` into its own file under `tests/commands/`, then delete `playbook_state_test.py`, `playbook_run_integration_test.py` and `tests/__fixtures__/playbook-transition-home/`, confirming by grep that no other test reads that tree | `booping-python/tests/commands/*`, `booping-python/tests/__fixtures__/playbook-transition-home/` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] One case file carries the whole walk as consecutive `cmd` lines whose stdout concatenates in order; a non-final line exiting non-zero fails the case.
- [ ] Every seeded `_scripts/` file is made executable by a leading `chmod +x` cmd line. The set is read off the fixture playbook's own manifest — every name appearing in a `script <name>` hook entry on any edge the walk takes, plus any bootstrap `hooks.post` entry — not discovered by running the case and watching it fail.
- [ ] The mid-run snapshot pins the outer status, its edge set, and the instance map as it stands with one instance advanced.
- [ ] The final snapshot pins every machine at its terminal status with no `next` key.
- [ ] Macro-rendered dates in any hook-written frontmatter are covered by `[..]` or pinned with `--stub-macro`.

### Task 4.2

- [ ] `test_report_writes_nothing` survives verbatim in intent in its own file, still asserting `st_mtime` and `st_size` are unchanged across a report.
- [ ] `tests/commands/playbook_state_test.py` and `tests/commands/playbook_run_integration_test.py` no longer exist.
- [ ] `tests/__fixtures__/playbook-transition-home/` no longer exists, and `rg -n "playbook-transition-home|get_fixture_path" booping-python/tests` returns no reference to it.
- [ ] `uv run pytest tests` is green.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-state && uv run pytest tests/commands && ! rg -q "playbook-transition-home" tests
```

The corpus is green with the run-walk case collected, the one surviving unit under `tests/commands/` passes, and no test references the deleted fixture tree.
