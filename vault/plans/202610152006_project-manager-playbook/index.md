---
title: "Project-manager playbook — the core manager over items, groom, develop and
  runs"
type: "feature"
status: done
sp: 25
related_to: null
created: 2026-10-15 20:06
planned: null
started: 2026-10-15 20:26
completed: 2026-10-15 20:53
code_reviews: []
sessions:
- c89cc3ae-5e20-46ac-93d9-c83f4ddb84b3
- e1d4bd12-b0f2-4016-8b84-e28f10b43ab8
- 36dbf90d-0102-4f43-add1-4a69775c2e2f
retro: null
summary: 'Core project-manager playbook: items in, groom/develop/review/merge out
  per autonomy mode; item questions; run code-review'
commit: d81f517f27104c0bfb6a7f23297882c072314455
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a25593ccb6e015e22
  research-sources: a7b4675d1f20209c6
  cross-review: a56bd798773a71631
  develop-loop-G1: a315897922f3798f6
  develop-loop-G2: a01463dfad3af8d36
  verify: aaff8f222f06df44a
reviewed_at: 2026-10-15 20:21
metrics_active_minutes: 821
metrics_models:
- <synthetic>
- claude-opus-5-5
metrics_tokens_input: 832
metrics_tokens_output: 286050
metrics_tokens_cache_creation: 2313640
metrics_tokens_cache_read: 111314302
---

# Project-manager playbook — the core manager over items, groom, develop and runs

## Context

The manager role lives today in two user-level playbooks — `orchestrate` (a live session that grooms, develops, reviews, merges and reports) and `backlog-run` + `backlog-manage` (a nightly run over a task store with its own state machine, budget gates and pause/resume). Their state is scattered, questions asked only in chat get lost and every project copies them ([adr/0028](../../adr/0028-one-project-manager.md)). This branch already ships every primitive a core manager stands on — `booping items` (requests filed verbatim), `booping status` (computed report), `booping run groom|develop` (registered runs), `booping correction add`, `booping defaults add` and `core.autonomy` — except two: an item cannot carry a question, and the independent review cannot be launched as a registered run.

After this plan `/playbook project-manager` opens with the short `booping status` and acts from it; every user message is split into items verbatim before any work; each item is classified (tiny fix / plan / question / decision) and taken through groom → develop → independent review → fixes → merge → report in the project's autonomy mode; a question the manager cannot settle is filed on the item with `booping items ask`, chat only pointing to it, and `booping status` shows the item as waiting on the user.

This is parts (1) and (4) of the request (`request.md`); part (2) is parked below, part (3) already shipped (C2).

## Decisions

- **Split**: the playbook, its two CLI gaps, docs and smoke evals now; budget/usage gate, time window and size batching parked — C1.
- **Setup linking**: already shipped (`booping specs init` + setup + two e2e cases) — C2.
- **Questions on an item**: sidecar `open-items/questions/OI-NNNN.md` in the `docs/clarifications.md` format, written only by `booping items ask|answer`; the answered test is code — C3.
- **Waiting on you**: computed from the sidecars into `booping status`, no new item status — C4.
- **Closing without a plan**: an `open → done` edge on the `open_item` machine — C5.
- **Review as a run**: `booping run code-review PLAN [--autonomous]` — C6.
- **Shape**: inline steps `on-start` → `intake` → `work`, no `states:`; intake and work repeat per later message — C7.
- **Mode routing**: supervised grooms inline in the session, develops and reviews through `booping run … --autonomous`, stops before merge; autonomous runs every stage through `booping run … --autonomous` and logs each settled gate with `booping defaults add` — C8.
- **Merge**: local `--no-ff` into the branch the sprint branch was cut from, never pushed; push/deploy/release only by a project rule or runbook targeting `project-manager` — C9.
- **Concurrency**: one develop or code-review run per checkout; groom runs may overlap — C10.
- **Report**: locked in the I/O contract below — C11.
- **External references**: none new. `booping run`'s `claude -p` flags were checked against the installed Claude Code in [202610151936_run-registry](../202610151936_run-registry/index.md); `git merge --no-ff` and `git branch --show-current` are stable git surface.

### Values in play

- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — the questions sidecar, its answered test, the waiting count and every launch are code; the playbook spends judgement only on splitting messages and classifying items.
- [value/0009 Adjustable control](../../value/0009-adjustable-control.md) — one config key switches the stops; what autonomous settled stays visible in `defaults.md`.
- [value/0007 Plans run to the end](../../value/0007-plans-run-to-the-end.md) — an approved plan develops headless with `--autonomous` in both modes; questions belong to grooming or the item.
- [value/0013 Guides to the goal](../../value/0013-guides-to-the-goal.md) — the session opens with status and names the next action; chat points at the item holding the question.
- [value/0005 Stack-agnostic core](../../value/0005-stack-agnostic-core.md) — merge is local git only; push, deploy, boards and channels are project rules and runbooks.
- [value/0003 Single source](../../value/0003-single-source.md) — one question format for plans and items; one item store, no second task store.

### Departures

- adr/0028 lists budget/window gates, pause/resume and size batching under the manager; this plan parks them as a sibling (C1) — the manager runs without them until that plan ships, so an autonomous session has no usage ceiling of its own beyond the subscription's.
- [rule/0012](../../rule/0012-every-diff-reviewed-in-plannotator.md) is retired, so the review is the core `code-review` playbook launched headless, not a browser review.

## Architecture

```
user message ─► intake ─► booping items add --source request --text - (one per request, verbatim)
                              │
session start ─► on-start ─► booping status ─► work ◄─ booping status runs (each turn)
                                                 │
     ┌───────────── classify each item ─────────┼──────────────────────────┐
  tiny fix                 plan                 question             decision
  worker edits,     supervised: /playbook groom  answer in chat    /playbook specs
  driver commits    inline; autonomous:          or items ask      records it
  items close       booping run groom --auto        │                 │
     │                     │                     items close       items close
     │              booping run develop --auto
     │              booping run code-review --auto
     │              driver commits review fixes
     │              merge gate (supervised: stop) ─► git merge --no-ff
     └──────────────────────────► report line per item
```

- `booping-python/src/booping/specs/questions.py` (new) parses and writes a questions sidecar; `commands/items.py` gains `ask` and `answer`; `status.py` reads the waiting count through it.
- `playbooks/specs/playbook.yaml` `open_item` gains `open → done`.
- `commands/run.py` accepts `code-review` beside `groom` and `develop`; the prompt template is shared.
- `playbooks/project-manager/` — `playbook.md` (preamble: modes, session loop, hard rules, agents), `playbook.yaml` (`graph:` only), `on-start/`, `intake/`, `work/` each with `prompt.md`; smoke suites beside `intake/` and `on-start/`.
- `src/config.yaml` gains `core.project_manager_playbook.agents` (the worker for tiny fixes, the researcher).

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Questions on an item — booping items ask and answer](milestones/M01-item-questions/M01-item-questions.md) | 4 | done |
| 02 | [Closing an open item and the waiting-on-you status](milestones/M02-item-close-and-status/M02-item-close-and-status.md) | 3 | done |
| 03 | [booping run code-review registers the independent review](milestones/M03-run-code-review/M03-run-code-review.md) | 2 | done |
| 04 | [project-manager playbook — manifest, preamble, on-start and intake](milestones/M04-playbook-skeleton/M04-playbook-skeleton.md) | 4 | done |
| 05 | [project-manager work step — classify, route, review, merge, report](milestones/M05-work-step/M05-work-step.md) | 4 | done |
| 06 | [Smoke suite for project-manager intake](milestones/M06-intake-smoke/M06-intake-smoke.md) | 3 | done |
| 07 | [Smoke suite for project-manager on-start](milestones/M07-on-start-smoke/M07-on-start-smoke.md) | 2 | done |
| 08 | [Documentation, README and CLAUDE.md on the project-manager](milestones/M08-docs/M08-docs.md) | 3 | done |

## I/O contract

- **`booping items ask ID --topic TEXT --question TEXT [--option TEXT]... [--step TEXT]`** — `ID` an `open` or `planned` item; appends to `open-items/questions/{ID}.md` (created with the H1 `# Questions — {ID}` when absent) the next `## C{n} — {topic} — open`, then `**Asked:** {YYYY-MM-DD} — {step}` (`--step` default `project-manager/work`), `**Question:** {question}`, `**Options:**` with one `- {option}` bullet each when any `--option` is given, and an empty `**Answer:**`. stdout: `open-items/questions/{ID}.md#C{n}`.
- **`booping items answer ID C{n} --text TEXT`** — `--text -` reads stdin, kept verbatim; writes the answer body and flips the heading's last segment to `answered`. stdout: `open-items/questions/{ID}.md#C{n}: answered`.
- **Answered test** — exactly `docs/clarifications.md`'s: heading ends `answered` and the answer body has a non-blank line. An item is waiting on the user while it is `open` or `planned` and its sidecar holds a question that fails the test.
- **`booping items close ID`** on an `open` item → `done` with `closed_at` (was an error).
- **`booping run code-review PLAN [--autonomous]`** — exactly one plan, validated and recorded as `develop` is; record `playbook: code-review`; prompt `core.run.prompt` with `{playbook}` = `code-review`.
- **`booping status` items line** — the existing line, then ` — {n} waiting on you` when `n > 0`; nothing appended at `0`.
- **`booping status items --detail`** — the existing table, then, when any item waits, a blank line, `Waiting on you:`, a blank line and `| id | title | open questions | sidecar |` with rows by id, `open questions` the count failing the test, `sidecar` `open-items/questions/{id}.md`.
- **stderr** (`error: {message}`, exit 1, nothing written): `unknown item {id}`, `item {id} is {status}` (ask on a closed item), `unknown question {id} {C}`, `question {id} {C} is already answered`, `--text is blank`, `code-review takes exactly one plan`, plus the existing `plan not found: {path}`.
- **Manager report** — one line per item touched this turn, `{id} {title} — {outcome} — {pointer}`: `outcome` one of `done`, `planned`, `running`, `waiting on you`, `dropped`; `pointer` the closing commit's short sha (`done` without a plan), the plan's vault path (`planned`, `done` with a plan), the run record `runs/{run}.md` (`running`), the sidecar `open-items/questions/{id}.md#C{n}` (`waiting on you`), the close reason (`dropped`). Then the next action in one sentence (rule/0005).

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` drift only in `playbooks/project-manager/_reports/output.md` (new) and the `open_item` table of `playbooks/specs/_reports/output.md` (`open → done`); accepted per the owner's snapshot policy, each listed in `develop-defaults.md`.
- [ ] `bin/booping render-playbook project-manager` renders with no STOP or Note notice, three steps, the agents table.
- [ ] `EVAL_PR=0 just smoke project-manager/intake` and `EVAL_PR=0 just smoke project-manager/on-start` pass.
- [ ] `bin/booping items ask --help`, `items answer --help`, `run code-review --help` match the contract.

## Out of scope

- Parked sibling, groomed in its own run after this plan: **project-manager autonomous extras** — a budget/usage gate before each milestone (a usage probe in code over Claude Code's `rate_limit_event` stream line, configurable 5-hour/7-day ceilings and a per-run allowance, `pause` recording the next milestone on the plan, resume from it), an optional time window (`start`/`end`/`grace`), batching small items by size (XS/S/M/L, a batch SP cap) so tiny fixes share one run, and a timer that starts an autonomous session.
- Intake from messengers or ntfy, duplicate merging, tracker providers (adr/0028 — not core).
- Retiring the user-level `orchestrate`, `backlog-run` and `backlog-manage` — the owner decides.
- Pushing, PRs, deploys and releases in core — project rules and runbooks.
- Groom reading item questions, or plan clarifications moving into item sidecars.

## CLAUDE.md impact

Opening paragraph's playbook list (`project-manager`); `## Commands` (`items` gains `ask`, `answer`; `run` gains `code-review`); `## Lifecycle` open-items track (the questions sidecar, `open → done`); `## Config` (`core.project_manager_playbook`) — M08 task 8.3.
