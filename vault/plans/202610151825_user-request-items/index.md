---
title: "User-request items — source and verbatim text on the item store, booping items
  add"
type: "feature"
status: ready-for-dev
sp: null
related_to: null
created: 2026-10-15 18:25
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 75e28809-8ea1-4cee-8c48-f7ef5b025853
retro: null
summary: Item store files user requests verbatim from any channel via booping 
  items add; store verbs move to booping items
commit: 2a5f98134404672214d8b1b9594dc1e1a731fb94
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: ae1876d1fce75f406
  cross-review: ab953a5d2c2054308
reviewed_at: 2026-10-15 18:39
---

# User-request items — source and verbatim text on the item store, booping items add

## Context

The item store ([adr/0025](../../adr/0025-open-items-are-an-index.md)) holds spec gaps only: `booping specs open-items add` requires `--direction`, `source` is a closed set of filing mechanisms (`manual`, `adr`, `mark`, `check`, `sync`, `correction`), the body comes from one `--body` argv flag, and ids are an unlocked max+1. [adr/0028](../../adr/0028-one-project-manager.md) makes it the one item store of the project-manager: a user request is filed with the user's words verbatim and a source, by any channel, through `booping items add`. After this plan the store's verbs live under `booping items`; `add` files a `request` (default) or `backlog` item from `--text` or stdin, byte-for-byte, with no direction and a derived title when none is given; `list` shows each item's source; concurrent adds never share an id.

This is part (1) of the project-manager request (`request.md`); parts (2)–(5) are parked below, under Out of scope.

## Decisions

- **One field**: `source` gains `request` and `backlog`; the existing values are the spec-gap sources — C1.
- **One command group**: top-level `booping items {add|scan|list|plan|close|reopen}`; `booping specs open-items` is removed with every reference — C2.
- **Verbatim text**: `--text TEXT` or `--text -` (stdin) replaces `--body`; written byte-for-byte, never evaluated as Jinja — C3.
- **Direction**: required for spec-gap sources, `null` and rejected for `request`/`backlog` — C4.
- **Title**: optional for `request`/`backlog`, derived from the text's first sentence — C5.
- **Ids**: exclusive file create, next id on collision — C6.
- **Index**: `source` column after `status` — C7.
- **Unchanged**: config key `core.specs.open_items`, `open-items/`, `OI-` ids, the `open_item` machine; no vault migration — C8.
- **Snapshots**: the runner may accept drift in `playbooks/groom/_reports/output.md` and `playbooks/specs/_reports/output.md` that is exactly the command rename and `--text` flag of M04; anything else stops the run.
- **adr/0025**: the runner appends a dated Consequences line — the command is `booping items` and items include user requests ([adr/0028](../../adr/0028-one-project-manager.md)).

### Values in play

- [value/0003 Single source](../../value/0003-single-source.md) — one `source` field, one command group, one store; the item format stays the scaffold in `src/config.yaml`.
- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — code allocates ids, derives titles and writes the text; no model formats an item.
- [value/0011 Everything in one place](../../value/0011-everything-in-one-place.md) — requests join spec gaps in `open-items/`, no second store.
- [value/0005 Stack-agnostic core](../../value/0005-stack-agnostic-core.md) — `items add` is channel-agnostic (argv or stdin); bridges stay outside core.
- [value/0004 Analysable history](../../value/0004-analysable-history.md) — the user's words are kept as said, not paraphrased.

### Departures

- [adr/0028](../../adr/0028-one-project-manager.md) names three sources (user request, spec gap, backlog task); the plan keeps the finer filing-mechanism values as the spec-gap sources instead of collapsing them into one `spec-gap` value — collapsing would lose what `scan`'s dedup key and the index already use.
- [rule/0019](../../rule/0019-driver-owns-vault-workers-own-code.md): none — the adr/0025 line is the runner's.
- [rule/0013](../../rule/0013-snapshot-baselines-accepted-by-user.md) (baselines accepted by the user): the runner accepts the described drift under the owner's standing permission of 2026-10-14 for this feature, listing each accepted report in `develop-defaults.md`.

## Architecture

`booping-python/src/booping/specs/open_items.py` stays the store's only module: vocabulary, id allocation, `write_item` over the `core.specs.open_items.scaffold` tree, the index query and `move()` into the `open_item` machine. The CLI moves from `commands/specs.py` into a new `commands/items.py`, registered in `cli.py` like `correction` and `defaults`, importing the tier helpers `scan` needs from `commands/specs.py`. Callers: `correction add --record` (files an item through `write_item`), the `open-items-follow-plan` script hook on groom's and develop's edges (`booping items close|reopen --plan`), groom's intake (`booping items plan`), the specs playbook's guide step. A future project-manager or a channel bridge calls `booping items add --text -`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [booping items command group](milestones/M01-items-command-group/M01-items-command-group.md) | 4 | pending |
| 02 | [Request and backlog items with verbatim text](milestones/M02-request-items/M02-request-items.md) | 4 | pending |
| 03 | [Source column and collision-safe ids](milestones/M03-index-source-and-safe-ids/M03-index-source-and-safe-ids.md) | 3 | pending |
| 04 | [Playbooks, docs and CLAUDE.md on booping items](milestones/M04-consumers-and-docs/M04-consumers-and-docs.md) | 4 | pending |

## I/O contract

- **`booping items add [--title TEXT] [--text TEXT|-] [--source S] [--direction D] [--record REF]`**: stdin — read only for `--text -`, all of it, verbatim. stdout — the vault-relative item path alone (`open-items/OI-NNNN.md`). stderr — `error: {message}`: `--text is required for source {request|backlog}`, `--text is empty`, `--direction does not apply to source {request|backlog}`, `could not allocate an item id under {dir}`, plus the existing messages. Exit `0` success, `1` user error (nothing written).
- **`booping items list [--all]`**: markdown table, header `| id | status | source | direction | record | title | plan |`; `direction` prints `null` for request items.
- **`booping items scan|plan|close|reopen`**: output unchanged from `booping specs open-items …`.
- **`booping specs open-items …`**: gone — argparse invalid choice, exit 2.

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` drift limited to the command rename and `--text` flag in `playbooks/groom/_reports/output.md` and `playbooks/specs/_reports/output.md`; accepted and listed in `develop-defaults.md`.
- [ ] `printf 'Ship it.\n{{ x }}\n' | bin/booping items add --text -` in a scratch vault files `source: request`, `direction: null`, title `Ship it.` and the two lines verbatim.
- [ ] `bin/booping items --help` lists six verbs; `bin/booping specs --help` lists no `open-items`.

## Out of scope

- Parked siblings of this request, each groomed in its own run after this plan: (2) computed status report; (3) run registry + `booping run groom|develop`; (4) the `project-manager` playbook — supervised and autonomous, splitting a message into items, questions on the item; (5) project-manager docs.
- A channel field on the item, intake bridges, duplicate merging, tracker integrations (adr/0028 — not core).
- Moving `core.specs.open_items` to a shared key, renaming `open-items/` or `OI-` ids, a vault migration.

## CLAUDE.md impact

`## Commands` (the `bin/booping` subcommand list gains `items`, `specs` loses `open-items`), `## Config` (`core.specs` — `open_items` is the store `booping items` lists), `## Lifecycle` (open-items track moved by `booping items`, user requests beside spec gaps) — M04 task 4.2.
