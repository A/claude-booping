---
title: "Vault-file operators — set, transition, state, config, next_id; booping items
  folded in"
type: "feature"
status: done
sp: 28
related_to: null
created: 2026-10-18 03:33
planned: null
started: 2026-10-18 03:45
completed: 2026-10-18 04:25
code_reviews: []
sessions:
- 955b76a5-4a7f-495d-b87c-25f4e4c2dbc8
retro: null
summary: One vault-file operator set — set, transition, state, config, next_id 
  in create — with booping items folded into it
commit: 07dde5f8a92b7d2de1bd3679bad34d5425b6aec0
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-18 03:44
metrics_active_minutes: 118
metrics_models:
- claude-opus-5-5
metrics_tokens_input: 436
metrics_tokens_output: 184453
metrics_tokens_cache_creation: 404983
metrics_tokens_cache_read: 52803665
---

# Vault-file operators — set, transition, state, config, next_id; booping items folded in

## Context

Operations on vault files are spread over commands named each its own way — `frontmatter-update` (`booping-python/src/booping/commands/frontmatter_update.py`), `marker-set` (`commands/marker_set.py`), `playbook-transition` (`commands/playbook_transition.py`), `playbook-state` (`commands/playbook_state.py`), `config-get` (`commands/config_get.py`) — and `booping items` (`commands/items.py`, `specs/open_items.py`) carries eight verbs that mostly restate `create`, `query`, `frontmatter-update` and `playbook-transition`. After this plan the vocabulary is `create`, `query`, `set`, `transition`, `state`, `config` (plus `render`, `render-playbook`), and `booping items` is gone: its verbs are expressed through those operators, item ids come from a `next_id` template global, sizes are checked by an mdcheck schema, and `scan` is `booping specs scan`. No aliases (release 2.0.0).

Values in play: value/0015 and rule/0025 (code only where code reads the result; items' bookkeeping moves onto the generic operators, `batch` becomes prose), value/0003 (one operator per operation), value/0006 (a framework's primitives a user playbook gets too), adr/0037 and adr/0038 (existing primitives and mdcheck schemas over bespoke commands). No departure from a value or rule.

## Decisions

- `booping set <file> k=v… [--remove k]… [--append k=v]…` replaces `frontmatter-update` and `marker-set`. A file named `.booping` is the marker (bare YAML mapping, `update_marker`, `latest_migration` keeps its int-or-`@latest` rule); any other file is markdown frontmatter (`update_frontmatter`, Jinja `macro` interpolation and YAML typing as today). `set` with no file argument is an error; the marker path is given explicitly (`booping set .booping latest_migration=@latest`). The hook verb in `playbook.yaml` `hooks:` lists is renamed `frontmatter-update` → `set` with the same token grammar (optional file target first, `{instance}` filled).
- `booping transition <file> <status> [--playbook P] [--state S]` replaces `playbook-transition`. Resolution: every machine whose `artifact` pattern matches the file (instance filled from the path) and whose current status of the file has an edge (superstates merged) to `<status>`; a file with no status bootstraps only into a matching machine's `initial`. Exactly one candidate → it; none → exit 1 naming the file's status and the legal targets; more than one → exit 1 listing `playbook/state` candidates and asking for `--playbook`. `--playbook` (and `--state` within it) narrows the candidates and is required for machines without `artifact:` (code-review, retro, learn, docs, model-benchmark), where the file is the target. The workdir is implied from the file and the matched artifact pattern, as an absolute `--target` implies it today; `--workdir` is dropped. Rendered `Advance:` lines always pass `--playbook` (groom/run and develop/run share `index.md` and the edges `awaiting-approval → ready-for-dev|cancelled` with different hooks).
- `booping state <file> [--playbook P]` replaces `playbook-state`: the frontier report for every machine of the matching playbook(s) in the file's run directory, instances included, same output shape as today.
- `booping config <key>` replaces `config-get`, output and exit codes unchanged; booping-tracker shells to it.
- `create` exposes a template global `next_id(prefix, width=4)`: the highest `{prefix}{n}` among file names in the destination directory plus one, zero-padded to `width`; no file yields 1. A name that already exists is skipped as today and reported, which is how a race shows.
- Open items are created by `booping create core.specs.open_items.template {vault}/open-items --set title=… --set source=… [--set direction=…] [--set record=…] [--set body=…]`, the tree keyed `"{{ next_id('OI-') }}.md"` and stamping `created_at` by macro. Corrections and agent decisions key their trees `"{{ next_id('R') }}-{{ name }}.md"` / `"{{ next_id('D') }}-{{ name }}.md"` with `--set name={step-slug}` instead of a timestamp.
- Item sizes: `booping set open-items/OI-NNNN.md size=M`; `playbooks/specs/_schemas/open_item.yaml` (mdcheck) checks `size` against the sizes of `core.project_manager_playbook.batch.sizes` restated as an enum, with a comment that the two change together (as adr/0038's milestone schema restates the SP threshold).
- `items add --record adr/NNNN` defaults (title from the ADR's `Confirmation:` line, direction `spec-to-code`, source `adr`) move to the caller: the driver reads the ADR and passes `--set title=… --set direction=spec-to-code --set source=adr --set record=adr/NNNN`; the specs Sync scenario passes `--set source=sync --set direction=…`.
- `items plan` → `booping set {item} plan={plan index} && booping transition {item} planned`; `items close` → `booping transition {item} done|dropped` (with `set reason=…` when given); `items reopen` → `booping transition {item} open` (its edge hook already clears `plan`). `open-items-follow-plan` runs `booping query --glob 'open-items/OI-*.md' --where plan={artifact} --where status=planned --output paths` and transitions each, absorbing failures as today.
- `items batch` → prose in the project-manager `work` step: list open items of a direct size with `booping query` and pack them in id order under `max_sp`, the sizes, direct list and cap rendered from `core.project_manager_playbook.batch`.
- `items scan` → `booping specs scan [--tier T]`, same behaviour and output, code moved into `commands/specs.py`.
- `booping items list` → `booping query --config core.specs.open_items.index`.
- Kept in `specs/open_items.py` only what `status`, `run`, `specs scan` and the site still import; the id allocator, `move`, `set_size`, `pack`, `sized_open_items` and bulk close/reopen go.

## Architecture

```
booping set  ───────────── frontmatter (.md) │ marker (.booping)
booping transition file st ─► machines whose artifact matches file ─► edge from current status ─► hooks (set …, script …)
booping state file ─────── frontier of the matching playbook(s)
booping config key
booping create tree dest ── template env + next_id(prefix) over dest
booping query ─────────── slices (items list, follow-plan hook, PM batch)
booping specs scan ─────── marks + check findings → items via create
```

Callers whose expected text changes: `src/templates/_partials/_playbook_driving.j2` (Run state), `src/templates/_partials/_playbook_graph.j2` (State section, `Advance:` line), every `playbook.yaml` hook list, `playbooks/_scripts/*` and `playbooks/*/_scripts/*` (comments and `config-get`), prompts naming the old commands (groom, develop, retro, project-manager, specs, setup, migrate, model-benchmark), `migrations/004_*`, `migrations/005_*`, `booping-tracker/src/booping_tracker/config.py`. The develop run executing this plan switches to `booping transition` for its own milestone moves from the commit of M03 on.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [booping set` replaces frontmatter-update and marker-set](milestones/M01-booping-set-replaces-frontmatter-update-and-marker-set/M01-booping-set-replaces-frontmatter-update-and-marker-set.md) | 4 | done |
| 02 | [booping config` replaces config-get](milestones/M02-booping-config-replaces-config-get/M02-booping-config-replaces-config-get.md) | 2 | done |
| 03 | [booping transition` infers the machine from the file](milestones/M03-booping-transition-infers-the-machine-from-the-file/M03-booping-transition-infers-the-machine-from-the-file.md) | 4 | done |
| 04 | [booping state` reports the frontier for a file](milestones/M04-booping-state-reports-the-frontier-for-a-file/M04-booping-state-reports-the-frontier-for-a-file.md) | 2 | done |
| 05 | [The driving protocol and every prompt name the new verbs](milestones/M05-the-driving-protocol-and-every-prompt-name-the-new-verbs/M05-the-driving-protocol-and-every-prompt-name-the-new-verbs.md) | 3 | done |
| 06 | [next_id` in create; items, corrections and decisions use it](milestones/M06-next-id-in-create-items-corrections-and-decisions-use-it/M06-next-id-in-create-items-corrections-and-decisions-use-it.md) | 3 | done |
| 07 | [Item callers move onto the operators](milestones/M07-item-callers-move-onto-the-operators/M07-item-callers-move-onto-the-operators.md) | 4 | done |
| 08 | [booping items` removed; scan is `booping specs scan](milestones/M08-booping-items-removed-scan-is-booping-specs-scan/M08-booping-items-removed-scan-is-booping-specs-scan.md) | 3 | done |
| 09 | [Docs, CLAUDE.md and CHANGELOG name the operator set](milestones/M09-docs-claude-md-and-changelog-name-the-operator-set/M09-docs-claude-md-and-changelog-name-the-operator-set.md) | 3 | done |

## Groups

| group | milestones | sp |
| --- | --- | --- |
| G1 | M01, M02, M03, M04, M05 | 15 |
| G2 | M06, M07, M08, M09 | 13 |

## I/O contract

- **Arguments / flags**:
  - `booping set <file> [k=v…] [--remove K]… [--append K=V]…` — `.booping` → marker keys; otherwise frontmatter.
  - `booping transition <file> <status> [--playbook P] [--state S]` — inferred machine, or narrowed.
  - `booping state <file> [--playbook P]`.
  - `booping config <key>`.
  - `booping specs scan [--tier T]`.
  - Template global `next_id(prefix, width=4)` in `create` trees.
- **stdin**: none new (`--set body=-` unchanged where it exists today).
- **stdout**: `set` — the diff report `frontmatter-update` printed; `transition` — today's mutation report; `state` — today's frontier report; `config` — today's `config-get` output; `specs scan` — today's `items scan` lines.
- **stderr**: `transition` ambiguity: `error: {file} matches more than one machine with an edge {from} → {to}: {playbook/state}, {playbook/state}; pass --playbook`; no match: `error: {file} ({status}) has no edge to {to}; legal: {list}`; no-artifact without `--playbook`: `error: {file} matches no machine artifact; pass --playbook`.
- **Exit codes**: `0` success; `1` user error (no or ambiguous machine, illegal edge, bad value, missing file); `2` usage or config error; `config` keeps `1` for a missing key.

## Final Verification

- [ ] Help text updated and accurate for `set`, `transition`, `state`, `config`, `specs scan`, `create`.
- [ ] Happy-path + at least one failure-path invocation verified per new verb.
- [ ] Exit codes match the documented contract.
- [ ] `bin/booping render src/templates/skills/playbook.md.j2` and `bin/booping render-playbook groom|develop|code-review` render cleanly with the new verbs.
- [ ] `just lint`, `just typecheck`, `just pytest`, `just e2e`, `just mdcheck`, `just specs-check`, `just docs` green.

## Out of scope

- Vault records (`vault/` outside `plans/`) — the driver updates them after develop.
- A migration renaming `frontmatter-update` hooks in users' own playbooks — 2.0.0 is breaking, listed in the CHANGELOG.
- `booping specs` other verbs, `run`, `status`, `plan split`, `render*` — unchanged.
- The cross-review step adr/0035 removes — its own change.

## CLAUDE.md impact

`## Commands` (the operator sub-list), `## Playbooks` (run state: `booping transition` the only writer, `booping state` the frontier), `## Lifecycle` (open items moved by `transition`, created by `create`, sized by `set`), `## Config` (`core.specs.open_items` tree keyed by `next_id`) — M09.
