---
title: "Project-manager autonomous extras — budget gate, time window, size batching"
type: "feature"
status: in-progress
sp: 24
related_to: null
created: 2026-10-15 20:54
planned: null
started: 2026-10-15 21:14
completed: null
code_reviews: []
sessions:
- cc8c9973-3ab7-48e7-b1a5-806b0e65eba7
- 018b65c5-3c42-4f44-a466-b84420bcdb9c
retro: null
summary: 'Autonomous extras for project-manager: code-computed usage/window gate with
  paused runs and resume, item sizes and batches'
commit: 44b785b3652b9f78bc8646ebf2f0e0e8dec54f48
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-sources: aadfc435155833a3e
  research-codebase: a1d5160b7fc56a628
  cross-review: ad3d63ce1ba1b7168
reviewed_at: 2026-10-15 21:06
---

# Project-manager autonomous extras — budget gate, time window, size batching

## Context

The core project-manager ([202610152006_project-manager-playbook](../202610152006_project-manager-playbook/index.md)) launches groom, develop and code-review through `booping run … --autonomous` with no usage ceiling, no time window and one route per item — its recorded departure from [adr/0028](../../adr/0028-one-project-manager.md), which says the manager carries over backlog-run's budget and window gates, pause and resume, and size batching. After this plan:

- `booping budget read` prints the subscription's 5-hour and 7-day usage, from the newest run log (`booping run` already logs the child's `stream-json`) or a probe; `booping budget gate` turns it, the ceilings, an optional per-run allowance and an optional time window into `allow` (exit 0) or `pause` (exit 3).
- `booping run … --autonomous` passes the gate before it launches; develop passes it before each milestone group. A run that meets a closed gate ends `paused`, its record carrying the reason, the resume time and the plan's next milestone; `booping status` lists it with the command that resumes it.
- The manager sizes tiny fixes (`booping items size`), and `booping items batch` packs the small ones into batches that skip grooming — one worker briefing per batch, one commit per item.

Part (2) of the request — linking a repo-pointed specs tier into the vault — already ships (C1).

## Decisions

- **Usage source**: last `rate_limit_event` of the newest fresh `runs/*.log`, else `core.budget.probe`; no event = no reading = `pause` — C3.
- **Verdicts**: `allow` / `pause` only; ceilings 5h/7d, optional `run_pct` from a baseline stored at launch; per-size cost estimates dropped — C4.
- **Who is gated**: inside a registered run (`BOOPING_RUN_ID`) or under `core.autonomy: autonomous`; a supervised interactive session never — C5.
- **Pause record**: run status `paused` with `paused_reason`, `resume_after`, `next_milestone` stamped by the gate itself on the run record — C6.
- **Resume**: rerun `booping run develop {plan} --autonomous`; develop resumes from its milestone frontier; a later record on the same plan marks the paused one resumed, computed — C7.
- **Window**: `core.budget.window` local `HH:MM` pair, wraps midnight; checked by the gate; no kill at a grace deadline — C8.
- **Batching**: item `size:` written by `booping items size`; `core.project_manager_playbook.batch` (`sizes`, `direct`, `max_sp`); `booping items batch` packs in code — C9.
- **Manager**: report outcome `paused`; relaunch from `booping status`'s resume command once `resume_after` passed — C10.
- **Timer**: not core; the docs show a cron line over `booping run` — C11.
- **No new eval suite** — C12.
- **External references**: `rate_limit_event` shape (`rate_limit_info.unifiedWindows.{five_hour,seven_day}.{utilization,resetsAt}`) checked live against the installed Claude Code 2.1.280 on 2026-10-15; absent from Claude Code's official docs, documented by third parties only ([Untether stream-json cheatsheet](https://littlebearapps.com/help/untether/claude-stream-json-cheatsheet/)). The probe's flags (`-p`, `--model haiku`, `--max-turns`, `--no-session-persistence`, `--output-format stream-json`, `--verbose`) ran in that check.

### Values in play

- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — reading, verdict, record stamp, next milestone, resumed state and batch packing are code; the model judges only an item's size.
- [value/0009 Adjustable control](../../value/0009-adjustable-control.md) — every threshold and the window are config; a paused run is visible in `booping status` with its reason.
- [value/0003 Single source](../../value/0003-single-source.md) — the next milestone lives once (milestone statuses), stamped on the run record only as the history of where it stopped; resumed is computed, not stamped.
- [value/0005 Stack-agnostic core](../../value/0005-stack-agnostic-core.md) / [value/0006 A constructor](../../value/0006-a-constructor-not-a-fixed-solution.md) — the probe is a config argv; the timer is the user's scheduler.
- [value/0007 Plans run to the end](../../value/0007-plans-run-to-the-end.md) — a pause is a resumable stop between milestone groups, never mid-milestone.
- [value/0010 Proven to work](../../value/0010-proven-to-work.md) — every verdict branch and the batch packing are held by e2e cases.

### Departures

- The request says "the next milestone recorded on the item"; it is recorded on the run record, which names the item and the plan (C6, value/0003).
- adr/0028 lists the timer under the manager; it stays the user's scheduler (C11, value/0005).
- backlog-run's `stop` verdict, nightly baseline, per-size estimates and grace kill are not carried over (C4, C8).
- [rule/0013](../../rule/0013-snapshot-baselines-accepted-by-user.md): the develop run accepts the plan-described snapshot drift under the owner's standing permission for this feature (2026-10-14), listing each report in `develop-defaults.md`.

## Architecture

```
booping run X --autonomous ──► budget.verdict ──pause──► exit 3, no record
          │ allow (baseline_7d stored when run_pct set)
          ▼
   child claude -p (env BOOPING_RUN_ID) ── stream-json ──► runs/{id}.log ◄── budget.read (newest fresh log | probe)
          │
   develop-loop: before each group ─► booping budget gate ─pause─► stamps runs/{id}.md
          │                                                       (paused_reason, resume_after, next_milestone)
          ▼                                                       child ends 0 ─► status: paused
   booping status runs --detail ─► Paused: … | resume: booping run develop {plan} --autonomous

project-manager work: classify ─► tiny fix ─► booping items size ─► booping items batch ─► per batch: gate ─► worker ─► commit per item ─► items close
```

- `booping-python/src/booping/budget.py` (new) — reading, verdict, record stamp; `commands/budget.py` (new) — `read`, `gate`.
- `commands/run.py` / `runs.py` — `BOOPING_RUN_ID`, launch gate, baseline, `paused` status.
- `status.py` — resumed computation, `Paused:` table.
- `commands/items.py` / `specs/open_items.py` — `size`, `batch`.
- `src/config.yaml` — `core.budget` (shared: run launcher, develop, manager), item `size`, `core.project_manager_playbook.batch`.
- `playbooks/develop/develop-loop/base.md`, `playbooks/project-manager/work/prompt.md` — one call each where the code decides.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Usage reading — booping budget read over run logs and the probe](milestones/M01-usage-reading/M01-usage-reading.md) | 3 | done |
| 02 | [Budget gate — ceilings, run allowance and time window in booping budget gate](milestones/M02-budget-gate/M02-budget-gate.md) | 4 | done |
| 03 | [Paused runs — launch gate, the gate stamps the run record, the paused status](milestones/M03-run-pause/M03-run-pause.md) | 4 | done |
| 04 | [Paused runs in booping status with next milestone and resume command](milestones/M04-status-paused/M04-status-paused.md) | 3 | done |
| 05 | [Item sizes and batches — booping items size and items batch](milestones/M05-item-size-batch/M05-item-size-batch.md) | 4 | done |
| 06 | [Develop-loop gate and project-manager batches, pauses and resumes](milestones/M06-playbook-wiring/M06-playbook-wiring.md) | 3 | done |
| 07 | [Documentation, CLAUDE.md and config reference for budget, window and batches](milestones/M07-docs/M07-docs.md) | 3 | done |

## I/O contract

- **`booping budget read`** — no arguments. stdout, three lines in this order: `5h: {pct}% (resets {YYYY-MM-DD HH:MM})`, `7d: {pct}% (resets {YYYY-MM-DD HH:MM})`, `source: {vault-relative log path}|probe`. Exit 0; no reading → exit 4, stderr `error: no usage reading: {why}` (`probe exited {n}`, `cannot run probe: {argv0}`, `no rate_limit_event in probe output`), stdout empty.
- **`booping budget gate`** — no arguments. stdout, one verdict line, plus `resume_after: {YYYY-MM-DD HH:MM}` on a second line for a `pause` that has one. Verdict lines:
  - `allow — not gated: supervised session`
  - `allow — 5h {a}%, 7d {b}%` (with `run_pct`: `, run {spent}/{run_pct}`)
  - `pause — outside window {start}-{end}`
  - `pause — no usage reading: {why}`
  - `pause — 5h usage {a}% ≥ ceiling {c}%`
  - `pause — 7d usage {b}% ≥ ceiling {c}%`
  - `pause — run allowance spent: {spent} ≥ {run_pct} (7d points)`

  Exit 0 `allow`, 3 `pause`, 1 config error (`error: core.budget.window must be {start: HH:MM, end: HH:MM}`). Inside a registered run a `pause` stamps `{vault}/runs/{BOOPING_RUN_ID}.md`.
- **Run record keys** — `usage_baseline_7d` (int, launch, only with `run_pct`); `paused_reason` (the verdict line after `pause — `), `resume_after` (`YYYY-MM-DD HH:MM` or null), `next_milestone` (milestone stem or null) — stamped by the gate. Status `paused` when the child exits 0 with `paused_reason` set.
- **`booping run groom|develop|code-review … --autonomous`** under a closed gate → the verdict lines on stdout, exit 3, no record.
- **`booping status runs --detail`** — when an unresumed paused run exists: blank line, `Paused:`, blank line, `| id | plan | items | next milestone | reason | resume after | resume |`; rows by id; `resume` = `` `booping run develop {plan} --autonomous` `` — only develop runs pause; a later record of any playbook on the same plan marks one resumed.
- **`booping items size ID SIZE`** — stdout `{id}: size {SIZE}`; errors (exit 1, stderr, nothing written): `unknown item {id}`, `item {id} is {status}`, `unknown size {SIZE}: one of {keys joined by ', '}`.
- **`booping items batch`** — stdout one line per batch `B{n} ({sp} SP): {id} {id} …`, or `no batch: no open item of a direct size`; exit 0.
- **Manager report** — the parent plan's line contract plus one outcome: `paused`, pointer the run record `runs/{run}.md`, or `gate closed` when no run started.

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` drift only in `playbooks/develop/_reports/output.md` (the gate step) and `playbooks/project-manager/_reports/output.md` (the work step's sizing, batches, paused); accepted per the owner's snapshot policy, each listed in `develop-defaults.md`.
- [ ] `bin/booping budget --help`, `budget gate --help`, `items size --help`, `items batch --help`, `run develop --help` match the contract.
- [ ] `bin/booping budget read` in this repo prints a live reading (happy path) and `bin/booping budget gate` prints `allow — not gated: supervised session`.

## Out of scope

- A timer or scheduler unit (C11).
- Batching plan-sized items into one groom (C9).
- Killing a run at a window's end (C8).
- Usage sources other than the Claude Code stream line beyond what `core.budget.probe` allows (C3).
- Tracker providers, intake channels, retiring the user-level `orchestrate`, `backlog-run`, `backlog-manage` (request).

## CLAUDE.md impact

`## Commands` (`budget` with `read`, `gate`; `items` gains `size`, `batch`); `## Config` (`core.budget`); `## Lifecycle` run-records bullet (`paused`, its keys, resumed computed) — M07 task 7.2.
