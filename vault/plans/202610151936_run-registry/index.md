---
title: "Run registry — booping run groom|develop launches recorded claude -p runs,
  status shows them"
type: "feature"
status: ready-for-dev
sp: null
related_to: null
created: 2026-10-15 19:37
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 06b18e93-eee0-4ae8-9d7d-3279d4c1bf0d
retro: null
summary: booping run groom|develop launches claude -p from core.run, records 
  each run with its items under runs/, status shows them
commit: fcfe3622274f7eafdb3d9897aa80785232ca7bfb
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a466f96bb943b3ec0
  research-web: afcd469e8c683ac34
  cross-review: af594f8f99c0dec9c
reviewed_at: 2026-10-15 19:49
---

# Run registry — booping run groom|develop launches recorded claude -p runs, status shows them

## Context

A headless groom or develop run is launched today by hand-typing `claude -p` with the right env (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, without which the run kills its own workers after 600 s), `< /dev/null`, a pasted autonomy preamble and a log path; nothing records that the run exists, which item it serves or how it ended. [adr/0028](../../adr/0028-one-project-manager.md) decides every launched run is registered with its item and a fallback check, and a finished run surfaces on the next turn. After this plan `booping run develop {plan} --autonomous` (or `groom {items}`) launches the run from `core.run`, writes `runs/{id}.md` before the child starts and its outcome when it ends, and exits with the child's code; `booping status` gains a `runs:` line — running, finished, failed and lost runs nobody acked — and `booping run ack` marks them seen.

This is part (3) of the project-manager request (`request.md`). Parts (4) and (5) are parked below, under Out of scope.

## Decisions

- **Command shape**: `booping run groom TARGET...`, `booping run develop PLAN`, both `--autonomous`; `booping run ack ID...` — C1.
- **Foreground**: the wrapper waits for the child and exits with its code; the caller backgrounds it — C2.
- **Registry**: one plain-markdown record per run at `{vault}/runs/{id}.md`, the log beside it, logs gitignored — C3.
- **Lifecycle**: only `booping run` writes a record; `lost` is computed at read time from the pid, the fallback check; no state machine — C4.
- **Config**: `core.run` (`dir`, `command`, `env`, `prompt`, `preamble`), directly under `core` as a shared key (the CLI now, the project-manager in part 4) — C5.
- **Ids**: run id from `core.macros.date`, session id a uuid5 of the run id passed as `--session-id` — C6.
- **Items**: given item ids for groom, else the items planned for the plan — C7.
- **Status**: `runs` between `plans` and `records`, unacked records only — C8.
- **Output**: locked in the I/O contract below — C9.
- **External references**: checked against the installed Claude Code 2.1.280 `claude --help`: `-p`, `--permission-mode` (choices include `auto`), `--output-format stream-json` (needs `--verbose` under `-p`), `--verbose`, `--session-id <uuid>`. `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` is not in `--help`; its effect (`0` stops `-p` from ending background tasks after 600 s) is attested by the owner's `orchestrate` playbook, which launches every run with it. It is config, so a changed name is a config edit.

### Values in play

- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — launch, record, outcome and the lost check are code; ids are derived, not random.
- [value/0011 Everything in one place](../../value/0011-everything-in-one-place.md) — runs are plain files in the vault beside the plans and items they serve.
- [value/0004 Analysable history](../../value/0004-analysable-history.md) — a record keeps the prompt, items, session id and outcome; acking hides it from status, never deletes it.
- [value/0006 A constructor](../../value/0006-a-constructor-not-a-fixed-solution.md) — argv, env, prompt and preamble are config, overridable per tier.
- [value/0013 Guides to the goal](../../value/0013-guides-to-the-goal.md) — one command replaces the hand-typed launch; status shows what finished.

### Departures

- [rule/0025](../../rule/0025-mechanics-run-as-code.md) and CLAUDE.md's "`booping playbook-transition` is the only writer of run state" hold: a run record is not a playbook's run state but a CLI-owned log, like the corrections and defaults sidecars, so `booping run` writes it directly.
- The default `command` names `claude` and the default `prompt` `/booping:playbook` — the core knowing its own host is not a stack specific ([value/0005](../../value/0005-stack-agnostic-core.md) holds); both are config.

## Architecture

New `booping-python/src/booping/runs.py` owns the record: id allocation, `create`, `finish`, `ack`, the reader and `effective_status` (the lost check). New `booping-python/src/booping/commands/run.py` holds the parser, target validation, item resolution through `booping.specs.open_items` (`planned_for`, item paths), the launch (`subprocess.Popen` in the repo directory, stdin `/dev/null`, stdout+stderr into the log, its own session so a signal reaches the whole group) and signal forwarding; registered in `cli.py` beside `status`. `booping-python/src/booping/status.py` reads records only through `booping.runs`. `src/config.yaml` gains `core.run`. Nothing in `playbooks/` or `src/templates/` changes; the project-manager (part 4) is the first caller.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [booping run groom\|develop launches and records a run](milestones/M01-run-launch-and-record/M01-run-launch-and-record.md) | 4 | pending |
| 02 | [Signal forwarding, booping run ack and lost runs](milestones/M02-signals-ack-lost/M02-signals-ack-lost.md) | 3 | pending |
| 03 | [Runs section in booping status](milestones/M03-status-runs-section/M03-status-runs-section.md) | 3 | pending |
| 04 | [CLAUDE.md and documentation on booping run and core.run](milestones/M04-docs/M04-docs.md) | 2 | pending |

## I/O contract

- **`booping run develop PLAN [--autonomous]`** — `PLAN` a plan's `index.md` or its directory, absolute or relative to the cwd, inside the vault and existing.
- **`booping run groom TARGET... [--autonomous]`** — every `TARGET` an open item id `OI-NNNN` with a file under `open-items/`, or exactly one `PLAN` as above (a parked groom run). Mixing the two is an error.
- **`booping run ack ID...`** — run ids.
- **stdin** — not read; the child gets `/dev/null`.
- **Launch** — argv `core.run.command + ["--session-id", {session_id}, {prompt}]`, cwd the repo directory, env the inherited environment updated with `core.run.env`. `{prompt}` is `core.run.prompt` with `{playbook}` and `{target}` filled — `{target}` the plan's absolute `index.md` path, or for items `{id} ({absolute item path})` joined by `, ` — followed, under `--autonomous`, by a blank line and `core.run.preamble`.
- **Preamble** (`core.run.preamble`, verbatim): `AUTONOMOUS RUN, started by booping run — nobody can answer. Do not use AskUserQuestion and do not wait at review gates: confirm each yourself and log it with booping defaults add. Settle an unclear point with a sensible default and log it the same way. A question only the owner can answer parks the run where the playbook allows it; otherwise stop and report it. Never end the run while a background agent or a check you started is still running — wait for it. Never push.`
- **Record** `{vault}/runs/{id}.md` — frontmatter keys in this order: `id`, `playbook`, `mode` (`autonomous` | `supervised`), `target` (list, as given; plan paths vault-relative to `index.md`), `plan` (vault-relative `index.md` or null), `items` (list of ids), `status` (`running` | `finished` | `failed` | `lost`), `pid` (int while running, else null), `session_id`, `log` (`runs/{id}.log`), `started_at`, `ended_at`, `exit_code`, `acked_at` (dates `YYYY-MM-DD HH:MM`, null until set); body `# {id}`, a blank line, the prompt in a ```` ```text ```` fence.
- **stdout, `run groom|develop`**: line 1 `runs/{id}.md`, flushed at launch; line 2 at the end `{id}: {status} (exit {code})`.
- **stdout, `run ack`**: `{id}: acked` per id, in argument order.
- **stdout, `status`**: the line `runs: {r} running, {f} finished, {x} failed, {l} lost` after `plans:`, zero counts omitted, `runs: none` with no unacked record; detail `| id | playbook | mode | items | status | started_at | ended_at | exit_code | log |`, rows by id, `items` joined by `, `, empty cells `—`; no row → `none`.
- **stderr**: `error: {message}` — `no attached project`/no vault (as `items list` words it), `unknown item {id}`, `plan not found: {path}`, `develop takes exactly one plan`, `groom takes item ids or one plan, not both`, `unknown run {id}`, `run {id} is still running`, `cannot launch {argv0}: {reason}`, `cannot write run record: {reason}`. The child's own output goes to the log only.
- **Exit codes**: `run groom|develop` — the child's code; 128+n when ended by signal n; 127 when the command cannot be launched (record written `failed`); 1 a user error above (no record written); 2 argparse. `run ack` — 0, or 1 on the first invalid id with nothing written.

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` shows no drift (no playbook or template source changes in this plan).
- [ ] `bin/booping run --help`, `run develop --help`, `run ack --help` match the contract.
- [ ] `bin/booping status` in this repo prints six lines, `runs:` after `plans:`.
- [ ] A develop run against a scratch vault whose `core.run.command` is `[echo]` writes a `finished` record and a log holding the prompt.

## Out of scope

- Parked siblings of this request, each groomed in its own run after this plan: (4) the `project-manager` playbook — supervised and autonomous modes, questions on the item, the request → items → groom → develop → independent review → fixes → merge → report loop, backlog-run's budget and window gates, pause/resume and batching by size, launching runs through `booping run`; (5) project-manager docs and setup linking `{vault}` specs to a repo-pointed tier.
- Resuming a session (`--resume`), a detached or daemon launch, a timer unit, budget accounting on the record.
- Deleting or pruning old records and logs.
- Intake channels, duplicate merging, tracker integrations (adr/0028 — not core).

## CLAUDE.md impact

`## Commands` (`run` in the `bin/booping` subcommand list), `## Config` (`core.run`), `## Vault` (`runs/`), `## Lifecycle` (run records) — M04 task 4.1.
