---
id: "10"
title: "corpus cross-check and tier audit"
sp: 2
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M10: corpus cross-check and tier audit

Every deleted test is accounted for, the corpus README records the rules this migration relied on, and the whole gate runs green.

**Scope**: the migration's closing audit. Files: edited `booping-python/e2e/README.md`; this milestone file, which carries the cross-check tables. No case or unit is written here — anything the audit finds missing is a case added under the milestone that owns it.

Depends on every other milestone.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Build the cross-check table with the columns `unit file`, `test name`, `replaced by`, `kind` — where `kind` is one of `case`, `surviving unit` or `dropped`, and `replaced by` names the `.txtar` path, the unit file, or the drop reason — sourcing its rows from `git show HEAD~N:<path>` for each deleted file so no test is missed from memory, then close any gap it exposes in the owning milestone | this milestone file | 1 | pending |
| 10.2 | Record in `e2e/README.md` the two rules this migration ran on: shipped-content dependence limited to existence rather than extent, and the conditions under which a case legitimately omits its `stdout` section | `booping-python/e2e/README.md` | 1 | pending |

## Definition of Done

### Task 10.1

- [ ] Every one of the fourteen `render_test.py` tests appears in the table against a named case file.
- [ ] Every one of the eighteen `playbook_state_test.py` tests and the one run-integration test appears against a named case file or the surviving `test_report_writes_nothing` unit.
- [ ] Every one of the fourteen `test_session_stats.py` tests removed in M07 appears against a named case file, and the one recorded drop carries its reason.
- [ ] The `build_test.py` tests appear marked as dropped with the command's retirement as the reason.
- [ ] No row is blank, and any gap the table exposed was closed by a case added under the milestone that owns that command.

### Task 10.2

- [ ] `e2e/README.md` states that a case may depend on shipped plugin content only through its existence, never its extent, and gives the migration gate as the worked example.
- [ ] It states that omitting a `stdout` section means unasserted rather than empty, names `debug-context` as the one command relying on that, and says a case doing so must comment why.
- [ ] Neither addition restates the `pytest-txtar` case format, which the plugin's own README owns.

## Verify

```
cd booping-python && uv run pytest e2e --collect-only -q | tail -1 && rg -c "existence, never its extent|unasserted" e2e/README.md
```

The corpus collects every case the cross-check table names, and the README carries both recorded rules. The whole-repo gate for this sprint is `just ci`, which belongs to the plan's Final Verification and runs once there.
