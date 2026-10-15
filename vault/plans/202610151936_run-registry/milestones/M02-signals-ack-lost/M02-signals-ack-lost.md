---
id: "02"
title: "Signal forwarding, booping run ack and lost runs"
sp: 3
status: pending
plan: "plans/202610151936_run-registry/index.md"
---

# M02: Signal forwarding, booping run ack and lost runs

A killed wrapper still records its run, `booping run ack` marks finished runs seen, and a record left `running` by a wrapper that died is read as `lost`.

**Scope**: in `booping-python/src/booping/commands/run.py`, install SIGINT and SIGTERM handlers for the child's lifetime that forward the signal to the child's process group (`os.killpg`), then let the normal wait path write `failed` with `exit_code` 128+n and exit with that code. In `booping-python/src/booping/runs.py` add `effective_status(record)` — `lost` when the stored status is `running` and `pid` is null or names no live process (`os.kill(pid, 0)` raising `ProcessLookupError`; `PermissionError` counts as alive), else the stored status — and `ack(ctx, ids)`. Add the `ack` sub-verb: `booping run ack ID...`; per id, in argument order: no record → `error: unknown run {id}`, exit 1, nothing written; effective status `running` → `error: run {id} is still running`, exit 1, nothing written; otherwise set `acked_at` from the date macro (`+%Y-%m-%d %H:%M`) and, for a lost run, `status: lost`, and print `{id}: acked`. All ids are validated before any is written. Log once: `logger.log(vault=ctx.vault, subcommand="run", message=f"ack {' '.join(ids)}")`.

Tests: integration tier. `booping-python/tests/runs_test.py` (pytest): the wrapper launched as a real subprocess with a vault config whose `core.run.command` sleeps, sent SIGTERM once the record shows `running` → record `failed`, `exit_code: 143`, wrapper exit 143, child process gone; `effective_status` over a record with a live pid (the test's own), a pid that cannot exist (above `/proc/sys/kernel/pid_max`, read in the test) and `pid: null`. e2e `booping-python/e2e/cases/run/`: ack of a finished record writes `acked_at`; ack of a lost record stores `lost`; an unknown id exits 1 and writes nothing. `runs_test.py` also covers ack of a still-running record — its `pid` the test's own — exiting 1 and writing nothing.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Signal forwarding and the killed-run outcome; pytest integration test. | `booping-python/src/booping/commands/run.py`, `booping-python/tests/runs_test.py` | 2 | pending |
| 2.2 | `effective_status`, `ack` and the `ack` sub-verb; e2e and pytest cases. | `booping-python/src/booping/runs.py`, `booping-python/src/booping/commands/run.py`, `booping-python/e2e/cases/run/*.txtar`, `booping-python/tests/runs_test.py` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] SIGTERM to the wrapper ends the child and leaves the record `failed` with `exit_code: 143`.

### Task 2.2

- [ ] `bin/booping run ack --help` shows `ID...`; the four ack outcomes above hold.
- [ ] `effective_status` is the only place `lost` is derived.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/tests/test_logger.py` — pytest module shape in this project.
- `booping-python/e2e/cases/items/` — close/reopen cases for an id-list verb's error shape.

## Verify

`cd booping-python && uv run pytest tests/runs_test.py e2e/cases/run -q`
