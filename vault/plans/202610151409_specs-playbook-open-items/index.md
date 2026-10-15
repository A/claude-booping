---
title: "Specs playbook and open items"
type: "feature"
status: in-progress
sp: 34
related_to: null
created: 2026-10-15 14:09
planned: null
started: 2026-10-15 14:29
completed: null
code_reviews: []
sessions:
- e47a3e24-2b43-4c07-9bf4-7e3853a04685
- 6996e136-87a3-4448-a7e3-12485f57a0ac
retro: null
summary: Core specs playbook as a guide over every specs scenario, plus open 
  items as a stored index driven by booping specs open-items
commit: 1e9a8f64482957307e95c6b419ab490ab5f697e7
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-15 14:26
---

# Specs playbook and open items

## Context

Specs records (`src/specs/README.md`) have a format, a checker and tiers, but no user surface: a tier is set up by `booping specs init` alone, values are settled in ad-hoc chats, decisions are recorded by hand, nothing reviews the set for internal conflicts or compares it with the code, and a gap between a record and the code — an ADR's unconfirmed `Confirmation:` line, a `[clarify]` mark, a `specs check` finding — lives nowhere a run can take it.

After this plan:

- `/playbook specs` is a guide ([adr/0024](../../specs/adr/0024-specs-playbook-is-a-guide.md)): it carries what the record types and principles are (by reference to `src/specs/README.md`) and the user's scenarios — init with the alignment guide, alignment, auto-review, recording a decision/idea/rule, sync specs and code, retro-to-rules, working open items — and acts on what the user asks without asking which action to take. On a repo without a project tier it offers init and the alignment guide.
- Open items ([adr/0025](../../specs/adr/0025-open-items-are-an-index.md)) are files `{vault}/open-items/OI-NNNN.md` under an `open_item` state machine (`open`, `planned`, `done`, `dropped`), driven by `booping specs open-items` (`list`, `add`, `scan`, `plan`, `close`, `reopen`). Closing a plan through develop closes its items; a failed or cancelled plan returns them to `open`; closed items stay and are filtered out of the index.

Goal (feature guidance): the user calls one playbook for every specs task, and every specs-to-code gap is one listed, plannable item.

### Values in play

Per [booping:rule/0030](../../../specs/rule/0030-planning-shows-values-in-play.md):

- [value/0015](../../specs/value/0015-deterministic-where-it-can-be.md) deterministic — numbering, the index, mark and check scanning, ADR confirmation extraction, plan linking and closing are CLI code with e2e cases; the playbook spends model tokens only on judgement (which scenario, what a record says, whether spec and code agree).
- [value/0002](../../specs/value/0002-minimal-effective-context.md) minimal context — the guide links `src/specs/README.md` and the alignment guide instead of inlining them; one step, scenarios a few lines each.
- [value/0013](../../specs/value/0013-guides-to-the-goal.md) guides to the goal — the playbook is a guide, not a router; every scenario names the next call ([rule/0005](../../specs/rule/0005-next-step-is-named.md)).
- [value/0003](../../specs/value/0003-single-source.md) single source — an item's plan link lives only on the item (`plan:`); no `open_items:` list on the plan. Statuses live in the `open_item` machine and the index renders from a query spec in config.
- [value/0004](../../specs/value/0004-analysable-history.md) analysable history — closed items stay, with `closed_at` and `reason`.
- [value/0009](../../specs/value/0009-adjustable-control.md) adjustable control — records the agent writes carry `created_by: claude` and no `reviewed`; items name their `source`.

### Departures

- **ADR-landing items are model-triggered, not computed** (departs from value/0015): the guide tells the agent to run `booping specs open-items add --record adr/NNNN` after writing an ADR with a confirmation line; the CLI extracts the line. A computed sweep over every ADR would file an item for each long-confirmed decision (27 ADRs in booping's own tier), so `scan` covers marks and check findings only. See C5.
- **The `specs` render carries a `## State` section for a machine its own run never moves** (stretches the driving protocol's "a `## State` section means a stateful run"): the `open_item` machine must live in a playbook manifest to use `playbook-transition`, and `specs` is its owner. The preamble names the workdir (the vault) and says only `booping specs open-items` moves it. See C3.
- **The CLI has verbs beyond adr/0025's list, add and close** — `scan`, `plan`, `reopen` — an extension the ADR's sources (marks, check findings) and its `planned` status need, not a contradiction.

## Decisions

- **Split**: parts 1 + 2 here; corrections (adr/0026) and autonomy modes (adr/0027) parked — C1.
- **Playbook shape**: one step, `guide`, inline, no run-state machine for the run; the setup playbook is the prior art for an ephemeral conversational playbook — C2.
- **Machine home**: `states.open_item` in `playbooks/specs/playbook.yaml`, `artifact: open-items/{instance}.md`, workdir the vault, moved only through the CLI, which calls the transition engine in-process — C3.
- **Config**: `core.specs.open_items` (shared by the specs CLI, the specs playbook and develop/groom hooks, so directly under `core.specs`): `dir`, `scaffold` (the item file tree) and `index` (the query spec `list` renders) — C4.
- **Sources**: `add` (manual or model, `--source`), `add --record adr/NNNN` (confirmation line extracted), `scan` (marks + `specs check` findings over the project tier, deduplicated) — C5, C6.
- **Plan link**: groom intake links items a request names via `open-items plan`; develop `done` closes them, develop `fail`/`cancelled` and groom `cancelled` reopen them, through one shared hook script that absorbs failure — C7.
- **Evals**: one suite at `playbooks/specs/guide/`, three smoke cases — C8.
- **No migration**: `open-items/` is created on first `add`/`scan`; there is no existing content to convert (precedent: migrations 001–004 convert content only).

## Architecture

```
/playbook specs ──render──▶ playbook.md (preamble: README link, tiers, workdir)
                            guide/prompt.md (scenarios) ──lazy──▶ docs/specs-alignment.md
        │ model judgement
        ▼
booping specs open-items {list|add|scan|plan|close|reopen}
        │  numbering, scaffold (core.specs.open_items.scaffold),
        │  index (core.specs.open_items.index query spec),
        │  transitions (playbooks/specs/playbook.yaml states.open_item, in-process engine)
        ▼
{vault}/open-items/OI-NNNN.md
        ▲
playbooks/_scripts/open-items-follow-plan {done|open}
        ▲ hooks: develop → done | fail | cancelled, groom → cancelled
```

### Open item file

```markdown
---
id: OI-0001
title: "Closing a plan closes its open items"
status: open
direction: spec-to-code
record: adr/0025#consequences
source: adr
plan: null
created_at: 2026-10-15
closed_at: null
reason: null
---

# Closing a plan closes its open items

{body — optional free paragraph from --body}
```

- `direction` ∈ `code-to-spec` | `spec-to-code` | `conflict` | `clarify`.
- `source` ∈ `manual` | `adr` | `mark` | `check` | `sync`.
- `record` — `{type}/{NNNN}` plus `#{heading-slug}` when the source is under a heading; `null` for a manual item about no record.
- `plan` — vault-relative `plans/{dir}/index.md`, or `null`.

### `open_item` machine

| From | To | When | Hook |
|---|---|---|---|
| `open` | `planned` | `open-items plan` linked a plan | — (CLI writes `plan:` before the transition; gate: `plan` names an existing file) |
| `open` | `dropped` | `close --dropped` | `frontmatter-update closed_at=… ` |
| `planned` | `done` | `close` / the plan reached develop `done` | `frontmatter-update closed_at=…` |
| `planned` | `dropped` | `close --dropped` | `frontmatter-update closed_at=…` |
| `planned` | `open` | `reopen` / the plan failed or was cancelled | `frontmatter-update plan=''` |

`done` and `dropped` are terminal. `close` on an `open` item without `--dropped` is exit 1 (`OI-0001 is open; plan it first or close it with --dropped`).

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Open-item machine, config and the specs playbook skeleton](milestones/M01-open-item-machine-and-config/M01-open-item-machine-and-config.md) | 3 | done |
| 02 | [booping specs open-items add files an item](milestones/M02-open-items-add/M02-open-items-add.md) | 4 | done |
| 03 | [booping specs open-items list renders the index](milestones/M03-open-items-list/M03-open-items-list.md) | 2 | done |
| 04 | [plan, close and reopen move items through the machine](milestones/M04-open-items-plan-close-reopen/M04-open-items-plan-close-reopen.md) | 4 | done |
| 05 | [scan files items from marks and check findings](milestones/M05-open-items-scan/M05-open-items-scan.md) | 4 | pending |
| 06 | [Plans link, close and reopen their items](milestones/M06-plans-close-their-items/M06-plans-close-their-items.md) | 4 | pending |
| 07 | [The specs guide — preamble and scenarios](milestones/M07-specs-guide-body/M07-specs-guide-body.md) | 4 | pending |
| 08 | [The alignment guide doc](milestones/M08-alignment-guide/M08-alignment-guide.md) | 2 | pending |
| 09 | [Smoke evals for specs/guide](milestones/M09-specs-guide-smoke-evals/M09-specs-guide-smoke-evals.md) | 4 | pending |
| 10 | [Docs, README and CLAUDE.md name the specs playbook and open items](milestones/M10-docs-and-claude-md/M10-docs-and-claude-md.md) | 3 | pending |

## I/O contract

All verbs: `booping specs open-items {verb} …`, run anywhere inside a booping project; paths printed vault-relative. Exit `0` success, `1` user error (unknown id, bad transition, bad flag value, no project) with one `error: …` line on stderr, nothing on stdout.

- `list [--all]` — stdout: the markdown table rendered from `core.specs.open_items.index`, columns `id | status | direction | record | title | plan`, sorted by id, `—` for a null cell; default rows `open` + `planned`, `--all` every status. No rows → the single line `no open items`.
- `add --title TEXT --direction D [--record REF] [--source S] [--body TEXT]` — `--source` defaults to `manual`. `add --record adr/NNNN` without `--title` reads the ADR's `Confirmation:` bullet (the text after `Confirmation:`, first sentence, truncated at 100 chars with `…`) as the title, `direction` defaults to `spec-to-code`, `source` to `adr`, `record` gets `#consequences`; an ADR without a confirmation line is exit 1. stdout: the created path, `open-items/OI-0001.md`.
- `scan [--tier T]` (default `project`) — files one item per `[clarify]`/`[unknown]` mark (`direction: clarify`, `source: mark`, title the sentence after the mark truncated at 100 chars with `…`, record `{type}/{NNNN}#{nearest-heading-slug}`) and per `specs check` finding (`direction: clarify`, `source: check`, title `{check}: {message}` truncated likewise, record `{type}/{NNNN}` when the path parses, else the tier-relative path). An item whose `(source, record, title)` matches any existing item of any status is skipped. stdout: one created path per line, then `{n} created, {m} already tracked`.
- `plan ID… --plan PATH` — every ID must be `open`; writes `plan:` and moves to `planned`. stdout: one transition report per item.
- `close ID… [--dropped] [--reason TEXT]` / `close --plan PATH` — `planned` → `done` (or → `dropped` with `--dropped`, which also accepts `open`); `--plan` closes every `planned` item linked to that plan as `done`, zero matches is exit 0 with `no planned items for {plan}`. stdout: one transition report per item.
- `reopen ID…` / `reopen --plan PATH` — `planned` → `open`, `plan:` cleared; zero matches with `--plan` is exit 0 with `no planned items for {plan}`.

## Final Verification

- [ ] `booping specs open-items --help` and every verb's `--help` list the flags of the I/O contract.
- [ ] Happy path and at least one exit-1 path per verb are e2e cases under `booping-python/e2e/cases/specs/`.
- [ ] `just snapshots` shows drift only in `playbooks/specs/_reports/output.md` (new), groom's and develop's reports (the hook and intake lines this plan adds); each accepted per the run's snapshot policy.
- [ ] `bin/booping render-playbook specs` renders without a STOP notice; `just smoke specs/guide` is green.
- [ ] `just ci` is green.

## Risk register

- The `## State` section on the `specs` render may lead a driver to create a run workdir for a run that has none — mitigated by the preamble naming the vault as the machine's workdir and the CLI as its only mover (C3).
- A `planned` item whose plan is closed outside develop (hand edit, cancelled before develop) stays `planned` — mitigated by the groom `cancelled` hook and `reopen --plan` as the manual reconcile, named in the guide.
- `scan` items go stale when a mark is resolved — accepted by adr/0025 (closed by hand, `close --dropped --reason resolved`).
- Smoke evals run on subscription auth and never in CI — the milestone's Verify runs them once.

## Out of scope

Parked sibling stubs, each groomed in its own run:

- **Corrections log** (adr/0026) — `booping correction add` (step, did, said verbatim, why, session id + message position the way `session-stats` finds the transcript) into the run artefact's `corrections.md` sidecar; a core rule targeted at groom, develop and code-review; retro reads the sidecar as its feed; a correction touching a spec also files an open item (`open-items add --source correction`, needs a sixth `source` value). Independent of this plan except that last line.
- **Autonomy modes** (adr/0027) — project config key `supervised` (default) | `autonomous`; the specs playbook's open-items scenario and a manager path honour it (autonomous: groom + develop without stopping, gates auto-confirmed, defaults recorded); uncommitted changes on a branch during a migration always shown and asked about. Needs this plan's open-items scenario.

Also out: a story record for the new surface (the `docs` playbook owns stories); seeding booping's own vault with items (a `scan` after merge is the user's call).

## CLAUDE.md impact

Owned by M10: the opening playbook list gains `specs`; `## Commands` `bin/booping` subcommand list names `specs open-items`; `## Lifecycle` gains an **Open-items track** bullet (artifact `{vault}/open-items/OI-NNNN.md`, `open_item` machine, plan link on the item, develop/groom hooks); `## Config` names `core.specs.open_items`; `## Vault` lists `open-items/`.
