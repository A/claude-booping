---
id: "02"
title: "Budget gate \u2014 ceilings, run allowance and time window in booping budget gate"
sp: 4
status: pending
plan: "plans/202610152053_project-manager-autonomous-extras/index.md"
---

# M02: Budget gate — ceilings, run allowance and time window in booping budget gate

`booping budget gate` decides `allow` or `pause` from the reading, the two ceilings, an optional per-run allowance and an optional time window, and exits 0 or 3.

**Scope**: `booping-python/src/booping/budget.py` gains the verdict; `commands/budget.py` gains `gate`; `src/config.yaml` `core.budget` gains `ceiling_5h_pct: 90`, `ceiling_7d_pct: 85`, `run_pct: null`, `window: null` (shape `{start: "HH:MM", end: "HH:MM"}`, local, an end before the start wraps midnight). Check order, first match wins: (1) not gated — no `BOOPING_RUN_ID` in the environment and `core.autonomy` is not `autonomous` → `allow`; (2) window closed → `pause`, `resume_after` the next start; (3) no reading (M01's failure) → `pause`, no `resume_after`; (4) 5-hour ≥ ceiling → `pause`, `resume_after` its `resetsAt`; (5) 7-day ≥ ceiling → `pause`, its `resetsAt`; (6) `run_pct` set and a registered run whose record carries `usage_baseline_7d` → spent = 7-day − baseline; spent ≥ `run_pct` → `pause`, no `resume_after`; (7) `allow`. Now is `core.macros.date` (`+%Y-%m-%d %H:%M`), so a case pins it with `macro_stubs`; the window check runs before any reading so a closed window costs no probe. The run record is found as `{vault}/{core.run.dir}/{BOOPING_RUN_ID}.md`; the `usage_baseline_7d` key itself is written by M03. Verdict lines locked in `index.md`'s I/O contract.

Tests (integration tier, `booping-python/e2e/cases/budget/`, hand-derived, probe faked as in M01, `TZ=UTC`, date macro stubbed): supervised, no run id → `allow — not gated…` without calling the probe (the fake probe exits 1); run id set, under both ceilings → `allow` with the numbers; 7-day at the ceiling → `pause` naming it with its reset; window `01:00`–`07:00` at `12:00` → `pause`, `resume_after` the next start, `01:00` the following day; wrapping window `22:00`–`06:00` at `23:30` → `allow`; `run_pct: 2` with baseline 10 and reading 12 → `pause`; no reading under `autonomous` → `pause`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Config keys with comments. | `src/config.yaml` | 1 | pending |
| 2.2 | Verdict function and `gate` verb. | `booping-python/src/booping/budget.py`, `booping-python/src/booping/commands/budget.py` | 2 | pending |
| 2.3 | The seven e2e cases above. | `booping-python/e2e/cases/budget/gate-*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.budget` prints all six keys.

### Task 2.2

- [ ] `bin/booping budget gate --help` matches the contract; exit 0 on `allow`, 3 on `pause`, 1 on a config error (`error: core.budget.window must be {start: HH:MM, end: HH:MM}`).
- [ ] stdout is exactly one verdict line; `pause` also prints `resume_after: {YYYY-MM-DD HH:MM}` on a second line when there is one.
- [ ] The verdict is a pure function of (gated, now, window, reading or its absence, ceilings, run allowance, baseline) — unit-callable with no I/O.

### Task 2.3

- [ ] The seven cases exist and pass; M01's cases pass unchanged.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/autonomy.py` — how `core.autonomy` is read.
- `booping-python/e2e/cases/run/second-run-in-the-same-second-gets-a-suffix.txtar` — a `macro_stubs` date pin.
- `/home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/_scripts/usage.py` lines 113–151 (`verdict`) — the check order this simplifies; its `stop` verdict, nightly baseline and per-size estimates are not ported (C4).

## Verify

`cd booping-python && uv run pytest e2e/cases/budget -q`
