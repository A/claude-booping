---
title: "Computed status report — booping status over items, ideas, plans, records
  and marks"
type: "feature"
status: in-progress
sp: 12
related_to: null
created: 2026-10-15 19:04
planned: null
started: 2026-10-15 19:19
completed: null
code_reviews: []
sessions:
- 61290692-8f20-4ac8-9584-82a338dc496d
- d5f6dbae-2151-4410-8617-2f647d7a67ab
retro: null
summary: booping status computes a short project status — items, open ideas, 
  plans, unreviewed records, marks — detail per section
commit: e82f87de6208e3d9594826bf2a1b5899ce455346
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a12e77b90acab7246
  cross-review: a2e1a6ea67e762d8a
reviewed_at: 2026-10-15 19:15
---

# Computed status report — booping status over items, ideas, plans, records and marks

## Context

Nothing in booping reports a project's state today: open items come from `booping items list`, plans from a hand-written `booping query --config core.plans --where …`, ideas, unreviewed records and `[clarify]`/`[unknown]` marks from reading or grepping the specs tier. [adr/0028](../../adr/0028-one-project-manager.md) decides status is computed by code from items, open ideas, plans, runs, unreviewed records and marks — short by default, detail on request, no stored handoff. After this plan `booping status` prints five lines — items, ideas, plans, records, marks — and `booping status {section} …` or `--detail` prints each named section as a table. The project-manager (part 4) and the user call the same command.

This is part (2) of the project-manager request (`request.md`); the runs section arrives with part (3), the run registry. Parts (3)–(5) are parked below, under Out of scope.

## Decisions

- **Command shape**: `booping status [SECTION ...] [--detail]` — no section prints the short report, a named section or `--detail` prints detail — C1.
- **Sections**: `items`, `ideas`, `plans`, `records`, `marks`, in that order, one ordered table in `booping/status.py` that part (3) extends with `runs` — C2.
- **Items**: non-terminal items per `open_item` status, split `request`/`backlog`/spec gap; detail is `booping items list`'s table — C3.
- **Ideas nobody took**: project-tier `idea` records at `status: open` that no non-terminal item names as its `record` — C4.
- **Plans**: active = a status the `run` machine of `groom` or `develop` declares non-terminal, filtered per call like the item index; done plans with no code review (new `core.status.queries.unreviewed_plans`) and with no retro (the existing `core.retro_playbook.queries.candidates`) — C5.
- **Unreviewed records**: empty `reviewed`, the site's predicate moved to `booping.specs.records.unreviewed` and shared — C6.
- **Marks**: the sentence-opening parser `scan` already uses, carrying the mark kind; `scan`'s dedup key unchanged — C7.
- **Tier**: project tier only — C8.
- **Output**: locked in the I/O contract below — C9.
- **Config**: `core.status` sits directly under `core` (shared key: the CLI now, the project-manager later), holding only query specs — `active_plans`, `unreviewed_plans`.
- **External references**: none — no new dependency, endpoint or flag of another tool; the web-research pass found nothing to verify.

### Values in play

- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — the report is computed by code; no model reads the vault to summarise it.
- [value/0003 Single source](../../value/0003-single-source.md) — statuses from the machines, plan queries from config, the retro queue's existing spec, one `unreviewed` predicate shared with the site, one mark parser shared with `scan`.
- [value/0002 Minimal effective context](../../value/0002-minimal-effective-context.md) — five lines by default; detail only for the sections asked.
- [value/0011 Everything in one place](../../value/0011-everything-in-one-place.md) — the report reads only vault files; it stores nothing.
- [value/0013 Guides to the goal](../../value/0013-guides-to-the-goal.md) — one command answers "what is going on".

### Departures

- None from a value or rule. [rule/0017](../../rule/0017-structured-data-rendered-not-restated.md) holds: the `done` literal lives in the `unreviewed_plans` query spec in config, like the retro queue's, not in code.
- Two mark parsers stay (the site's `site/markdown.py` and `open_items.py`); status uses `open_items.py`'s so its count is what `scan` would file. Merging them is out of scope.

## Architecture

New `booping-python/src/booping/status.py` computes the report: an ordered tuple of sections, each a name, a summary-line function and a detail function over one `Context`. Its readers: `open_items.machine`/`open_statuses`/`index_rows`/`index_table` for items; `booping.query.build_spec`/`resolve_spec`/`run`/`as_table` for plans over `core.status.queries.*` and `core.retro_playbook.queries.candidates`, the active filter built from the `groom` and `develop` playbooks' `run` machines in `ctx.playbooks`; `booping.specs.tiers.resolve_tiers` + `booping.specs.records.load_tier` for the project tier's records, read once per call, feeding ideas, records and marks. New `booping-python/src/booping/commands/status.py` holds the parser and printing, registered in `cli.py` beside `items`. Nothing writes; the command logs one line (`subcommand="status"`) like `items list`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [booping status command and the items section](milestones/M01-status-command-and-items/M01-status-command-and-items.md) | 3 | in-progress |
| 02 | [Plans section](milestones/M02-plans-section/M02-plans-section.md) | 3 | in-progress |
| 03 | [Ideas, records and marks sections](milestones/M03-ideas-records-marks/M03-ideas-records-marks.md) | 4 | in-progress |
| 04 | [CLAUDE.md and documentation on booping status](milestones/M04-docs/M04-docs.md) | 2 | in-progress |

## I/O contract

- **`booping status [SECTION ...] [--detail]`** — `SECTION` one of `items`, `ideas`, `plans`, `records`, `marks` (argparse choices; repeated names print once, in the canonical order). stdin — not read.
- **stdout, short** (no section, no `--detail`): exactly five lines, in section order:
  - `items: {n} {status}, … — request {r}, backlog {b}, spec gap {g}` — statuses in the `open_item` machine's order, zero counts omitted; with no non-terminal item, `items: none`.
  - `ideas: {n} open, not taken` — or `ideas: none`.
  - `plans: {n} {status}, … — done: {a} without code review, {b} without retro` — active statuses in groom's machine order then develop's (first occurrence wins), zero counts omitted; no active plan → `plans: none active`; the ` — done: …` tail is omitted when both counts are zero.
  - `records: {n} unreviewed — {type} {k}, …` — types in the schema order of the format directory, zero counts omitted; or `records: none unreviewed`.
  - `marks: {n} — clarify {c}, unknown {u}` — or `marks: none`.
- **stdout, detail**: per printed section, `## {section}`, a blank line, then its body; sections separated by one blank line. Empty body → the line `none`.
  - `items` — exactly `booping items list`'s table.
  - `ideas` — `| ref | title | created_at |`, by ref.
  - `plans` — `### active` with the `active_plans` columns then `path`; `### without code review` with `unreviewed_plans`' columns then `path`; `### without retro` with the retro candidates' columns then `path`. Each sub-table empty → `none` under its H3.
  - `records` — `| ref | status | title |`, by type order then number; `status` `—` for a value.
  - `marks` — `| kind | record | text |`, `record` the anchored ref `scan` would file.
- **stderr**: `error: {message}` on no attached project or no vault, plus `warning: skipping …` from the query engine for an unparseable plan file.
- **Exit codes**: `0` whenever the vault is readable (an empty vault prints the five `none` lines); `1` no project or vault; `2` an unknown section (argparse).

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` shows no drift (no playbook source changes in this plan).
- [ ] `bin/booping status` in this repo prints five lines in the locked shape; `bin/booping status ideas marks` prints two `##` sections.
- [ ] `bin/booping status --help` lists the five sections; `bin/booping status bogus` exits 2.

## Out of scope

- Parked siblings of this request, each groomed in its own run after this plan: (3) run registry + `booping run groom|develop` — adds the `runs` section to `booping status`; (4) the `project-manager` playbook — supervised and autonomous, opening with `booping status`; (5) project-manager docs and setup linking.
- Global and core tiers in the report; a JSON output mode; a stored or cached status file.
- Merging the site's mark parser with `open_items.py`'s.
- Intake channels, duplicate merging, tracker integrations (adr/0028 — not core).

## CLAUDE.md impact

`## Commands` (the `bin/booping` subcommand list gains `status`), `## Config` (`core.status` — the status report's query specs, a shared key) — M04 task 4.1.
