# Develop defaults — autonomous run 2026-10-15

- **Branch**: `feat/specs`, reused as-is — the owner named it in the invocation and forbade switching; no `feat/` sprint branch created. The `ready-for-dev` → `in-progress` gate "the user confirmed the branch name" is taken as satisfied by that instruction.
- **Review gates**: auto-confirmed (owner unavailable, autonomous run).
- **Groups** (cap 15 SP): G1 M01–M04 (14 SP), G2 M05–M07 (6 SP).
- **Drift**: plan commit `0d2819e` vs HEAD `202b1da` — only groom's vault commits on this plan; no plan-touched code changed; nothing outstanding.
- **Snapshots**: rule/0013 is overridden for this run by the owner's standing permission (2026-10-14) and the plan's Departures; accepted reports are listed below.

## Accepted snapshot reports
- **Out-of-contract file `booping-python/e2e/conftest.py`** (G1 worker): accepted — it drops `CLAUDE_CODE_SESSION_ID` so cases are hermetic inside a Claude Code session, and puts the repo's `bin/` first on `PATH` so a case's `env CLAUDE_CODE_SESSION_ID=… booping …` runs this checkout; both are needed by M02's own cases and add no scope.
- **M03 `commands/specs.py` untouched**: the `--source` help renders from `SOURCES`, so adding `correction` there satisfies 3.1's DoD without editing the listed file.
- **Commit split**: one worker built M01–M04 together, so `correction.py`, `commands/correction.py` and `cli.py` land whole in M01's commit; M02–M04 commit their own helpers and cases. Messages follow rule/0022 (`feat(correction): …`) with the worker named in the body.
