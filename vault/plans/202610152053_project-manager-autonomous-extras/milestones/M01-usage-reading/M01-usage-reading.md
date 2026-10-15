---
id: "01"
title: "Usage reading \u2014 booping budget read over run logs and the probe"
sp: 3
status: pending
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M01: Usage reading — booping budget read over run logs and the probe

`booping budget read` prints the subscription's current usage, taken from the newest run log or, failing that, from a probe.

**Scope**: new `booping-python/src/booping/budget.py` (reading only — no verdicts; M02 adds them) and `booping-python/src/booping/commands/budget.py` registering `booping budget` with the `read` verb; `src/config.yaml` gains `core.budget` with `max_age_s: 600` and `probe:` (argv `[claude, -p, "Reply with the single word OK.", --model, haiku, --max-turns, "1", --no-session-persistence, --output-format, stream-json, --verbose]`), each key commented like `core.run`'s. A reading is parsed from a stream's **last** line of `"type": "rate_limit_event"`: `rate_limit_info.unifiedWindows.five_hour` and `.seven_day`, each `utilization` (0–1, shown ×100 rounded to an integer percent) and `resetsAt` (epoch seconds, shown as local `YYYY-MM-DD HH:MM`). Source order: the newest `{vault}/{core.run.dir}/*.log` by mtime when its mtime is within `max_age_s` of now and it holds an event; else run `core.budget.probe` (cwd the repo, stdout captured, stderr discarded) and parse its stdout. A non-JSON line is skipped, never an error. Field shape per C3 in `clarifications.md`.

Tests (integration tier, e2e corpus `booping-python/e2e/cases/budget/`, hand-derived, `core.budget.probe` overridden in the case's vault `config.yaml` with an `sh -c` printing fixed lines — the same fake as `core.run.command` in the run cases; pin `TZ=UTC` in the case so `resetsAt` renders the same everywhere): a fresh run log with two events → the second one's numbers, source the log; no runs dir → the probe's numbers, source `probe`; probe output with no event → exit 4 and the contract's message; probe argv that does not exist → exit 4.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `core.budget` keys `max_age_s`, `probe` with comments. | `src/config.yaml` | 1 | pending |
| 1.2 | Stream parsing, log selection, probe, `booping budget read`. | `booping-python/src/booping/budget.py`, `booping-python/src/booping/commands/budget.py`, `booping-python/src/booping/cli.py` | 1 | pending |
| 1.3 | The four e2e cases above. | `booping-python/e2e/cases/budget/read-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `bin/booping config-get core.budget` prints both keys with the defaults above.

### Task 1.2

- [ ] `bin/booping budget --help` lists `read`; `bin/booping budget read --help` matches the I/O contract in `index.md`.
- [ ] stdout is exactly the contract's three lines; a missing reading is exit 4 with `error: no usage reading: {why}` on stderr and nothing on stdout.
- [ ] Nothing in `budget.py` prints; the command module formats.

### Task 1.3

- [ ] The four cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/runs.py` — module shape (pure reads and writes, a module error class, no printing) and `runs_dir()`.
- `booping-python/e2e/cases/run/develop-autonomous-appends-the-preamble.txtar` — the `sh -c` command override in a case's vault config.
- `/home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/_scripts/usage.py` lines 38–110 — the event parse and probe this ports; port the mechanics only, none of its paths or config keys.

## Verify

`cd booping-python && uv run pytest e2e/cases/budget -q`
