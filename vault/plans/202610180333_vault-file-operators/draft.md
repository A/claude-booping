---
title: "Vault-file operators — set, transition, state, config, next_id; booping items folded in"
type: feature
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

### M01 — `booping set` replaces frontmatter-update and marker-set

sp: 4
depends_on: []

#### Tasks

**Goal**: one `set` verb writes frontmatter of a markdown file or keys of the `.booping` marker; the hook verb follows.
**Scope**: `booping-python/src/booping/commands/` (new `set.py` from `frontmatter_update.py` + `marker_set.py`), `cli.py`, `context/lifecycle.py` (prepended `set status=<to>`), `commands/playbook_transition.py` hook dispatch, every `playbook.yaml` hook list (`playbooks/**`, `vault/_playbooks/**`), `playbooks/_scripts/stamp-session`, prompts and `src/config.yaml` comments naming either command, e2e `cases/frontmatter-update/` + `cases/marker-set/` → `cases/set/`, unit tests.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `set`: `.booping` basename → marker write (one or more pairs, `latest_migration` rule kept), else frontmatter write with `--remove`/`--append`; remove both old commands and their registration | `booping-python/src/booping/commands/set.py`, `booping-python/src/booping/cli.py` | 2 | pending |
| 1.2 | Rename the hook verb to `set` in the lifecycle prepend, the hook dispatcher and every `playbook.yaml`; switch every prompt, script and comment calling either old command | `booping-python/src/booping/context/lifecycle.py`, `playbooks/*/playbook.yaml`, `playbooks/_scripts/stamp-session` | 1 | pending |
| 1.3 | Move the e2e cases to `cases/set/`, rewriting command lines; one case per marker path and one for a rejected `latest_migration`; adjust unit tests | `booping-python/e2e/cases/set/`, `booping-python/tests/context/lifecycle_test.py` | 1 | pending |

Tests: integration tier, txtar cases — frontmatter set/remove/append, marker set incl. `@latest`, a hook-driven `set` through a transition.

#### Definition of Done

- [ ] Task 1.1: `booping set {file}.md k=v` writes frontmatter; `booping set .booping latest_migration=@latest` writes the marker; `booping frontmatter-update` and `booping marker-set` exit 2 as unknown commands.
- [ ] Task 1.2: `grep -rn 'frontmatter-update\|marker-set'` outside `vault/plans`, `*/_specs`, `_reports`, CHANGELOG history and migration old-path columns returns nothing.
- [ ] Task 1.3: `just e2e -k set` passes; no `cases/frontmatter-update/` or `cases/marker-set/` directory remains.

#### References

- `booping-python/src/booping/commands/frontmatter_update.py`, `booping-python/src/booping/commands/marker_set.py` — the behaviour merged.
- `booping-python/e2e/cases/frontmatter-update/` — case shape.

#### Verify

`just e2e -k "set or playbook-transition"`

### M02 — `booping config` replaces config-get

sp: 2
depends_on: [M01]

#### Tasks

**Goal**: `booping config <key>` prints what `config-get` printed, with the same exit codes.
**Scope**: `booping-python/src/booping/commands/config_get.py` → `config.py`, `cli.py`, `booping-tracker/src/booping_tracker/config.py` + its tests and README, `playbooks/develop/_scripts/refresh-milestone-table`, `vault/_playbooks/docs/_scripts/commit-docs`, `playbooks/setup/**`, `playbooks/project-manager/work/prompt.md`, `migrations/004_lessons_to_rules/migration.md`, `migrations/005_project_specs_to_vault_root/migration.md`, e2e `cases/config-get/` → `cases/config/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rename the command and its module; switch booping-tracker's shell-out and every script, prompt and migration caller | `booping-python/src/booping/commands/config.py`, `booping-tracker/src/booping_tracker/config.py`, `migrations/004_lessons_to_rules/migration.md` | 1 | pending |
| 2.2 | Move e2e cases to `cases/config/`; update booping-tracker tests | `booping-python/e2e/cases/config/`, `booping-tracker/tests/config_test.py` | 1 | pending |

Tests: integration tier — existing cases under the new name; booping-tracker's config test against the renamed call.

#### Definition of Done

- [ ] Task 2.1: `booping config core.plans.glob` prints `plans/*/index.md`; `booping config-get` is unknown; `grep -rn 'config-get'` outside history returns nothing.
- [ ] Task 2.2: `just e2e -k config` and booping-tracker's pytest pass.

#### References

- `booping-python/src/booping/commands/config_get.py` — the behaviour kept.

#### Verify

`just e2e -k config`

### M03 — `booping transition` infers the machine from the file

sp: 4
depends_on: [M01]

#### Tasks

**Goal**: `booping transition <file> <status>` moves a file along the one machine that matches it, or fails naming the candidates.
**Scope**: `booping-python/src/booping/commands/playbook_transition.py` → `transition.py` (CLI + the in-process `transition()` other code calls), `cli.py`, `specs/open_items.py` callers of `transition()`, e2e `cases/playbook-transition/` → `cases/transition/`, unit tests and script docstrings naming the old command.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Candidate resolution: machines across all playbooks whose `artifact` matches the file (instance from the path), filtered by an edge from the file's current status (or `initial` when it has none), narrowed by `--playbook`/`--state`; workdir implied from file + pattern; `--playbook` required for machines without `artifact:` | `booping-python/src/booping/commands/transition.py` | 3 | pending |
| 3.2 | Move the e2e corpus to `cases/transition/` with rewritten argv; add cases: unique inference (open item, milestone instance), ambiguous `index.md` edge without `--playbook` exits 1 listing `groom/run` and `develop/run`, a no-artifact machine without `--playbook` exits 1, illegal target lists legal ones | `booping-python/e2e/cases/transition/` | 1 | pending |

Tests: integration tier, txtar — the four inference cases above plus the moved corpus; the hook environment (`BOOPING_*`) unchanged.

#### Definition of Done

- [ ] Task 3.1: `booping transition {vault}/open-items/OI-0001.md clarify` moves the item without `--playbook`; `booping transition {plan}/index.md ready-for-dev` from `awaiting-approval` exits 1 naming both candidates; with `--playbook groom` it runs groom's hooks; the printed mutation report is unchanged in shape.
- [ ] Task 3.2: `just e2e -k transition` passes; `booping playbook-transition` is unknown.

#### References

- `booping-python/src/booping/commands/playbook_transition.py` — `transition()`, `implied_workdir()`, `_resolve_artifact()`.
- `booping-python/src/booping/context/lifecycle.py` — `resolve_edges`, `resolve_hooks`.
- `booping-python/e2e/cases/playbook-transition/` — case shape.

#### Verify

`just e2e -k transition`

### M04 — `booping state` reports the frontier for a file

sp: 2
depends_on: [M03]

#### Tasks

**Goal**: `booping state <file>` prints today's frontier report for the playbook(s) whose machines match the file.
**Scope**: `booping-python/src/booping/commands/playbook_state.py` → `state.py`, `cli.py`, e2e `cases/playbook-state/` → `cases/state/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Resolve the playbook(s) from the file with M03's matcher (`--playbook` narrows, required without `artifact:`), run dir from the file; report every machine of each, instances included | `booping-python/src/booping/commands/state.py` | 1 | pending |
| 4.2 | Move e2e cases to `cases/state/` with rewritten argv; add one case where `index.md` reports groom and develop without `--playbook` | `booping-python/e2e/cases/state/` | 1 | pending |

Tests: integration tier — the moved corpus plus the two-playbook case.

#### Definition of Done

- [ ] Task 4.1: `booping state {plan}/index.md --playbook groom` prints the same report `playbook-state groom --workdir {plan}` printed; `booping playbook-state` is unknown.
- [ ] Task 4.2: `just e2e -k state` passes.

#### References

- `booping-python/src/booping/commands/playbook_state.py` — the report kept.

#### Verify

`just e2e -k state`

### M05 — The driving protocol and every prompt name the new verbs

sp: 3
depends_on: [M02, M04]

#### Tasks

**Goal**: rendered skills and playbooks tell the driver `booping state`, `booping transition … --playbook`, `booping set`, `booping config`.
**Scope**: `src/templates/_partials/_playbook_driving.j2` (Run state), `src/templates/_partials/_playbook_graph.j2` (State intro, `Advance:` line), `booping-python/src/booping/commands/render_playbook.py` entry dicts if the line needs new fields, all prompts under `playbooks/**` and `vault/_playbooks/**` naming `playbook-transition`/`playbook-state`, `playbooks/specs/playbook.yaml` header comment, script comments in `playbooks/**/_scripts/*`, render-playbook e2e expected outputs.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite the Run state section and the graph partial: `booping state {workdir}/{artifact} --playbook {name}`, `Advance: booping transition {artifact path} <to> --playbook {name}[ --state X]`, instance paths for per-instance machines | `src/templates/_partials/_playbook_driving.j2`, `src/templates/_partials/_playbook_graph.j2` | 2 | pending |
| 5.2 | Switch every prompt, playbook.yaml comment and script comment; rebaseline the render-playbook cases whose expected text names the commands | `playbooks/specs/playbook.yaml`, `playbooks/develop/develop-loop/base.md`, `booping-python/e2e/cases/render-playbook/` | 1 | pending |

Tests: integration tier — render-playbook cases for a stateful playbook (groom), a per-instance machine (develop milestone) and a no-artifact machine (code-review).

#### Definition of Done

- [ ] Task 5.1: `bin/booping render-playbook groom` shows `Advance: booping transition` with `--playbook groom`; `bin/booping render-playbook develop` shows the milestone instance path; `bin/booping render-playbook code-review` shows `--playbook code-review` with its target.
- [ ] Task 5.2: `grep -rn 'playbook-transition\|playbook-state'` outside history returns nothing.

#### References

- `src/templates/_partials/_playbook_graph.j2` — the current State section.

#### Verify

`just e2e -k render-playbook`

### M06 — `next_id` in create; items, corrections and decisions use it

sp: 3
depends_on: [M01]

#### Tasks

**Goal**: a template tree can name a file `{{ next_id('OI-') }}.md` and get the next free id in the destination.
**Scope**: `booping-python/src/booping/commands/create.py` (`dest` into the env), `booping-python/src/booping/rendering.py` if the global lives there, `src/config.yaml` (`core.specs.open_items.template`, `core.corrections.template`, `core.agent_decisions.template`), prompts that pass `--set name=$(date …)` (`_playbook_driving.j2`, `specs/rule/0031-corrections-are-logged.md`, `playbooks/code-review/resolve/opus-5.md`, project-manager prompts), e2e `cases/create/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `next_id(prefix, width=4)` bound to the destination: max `{prefix}(\d+)` over its file names + 1, padded; usable in names and contents | `booping-python/src/booping/commands/create.py` | 1 | pending |
| 6.2 | Key the three trees by `next_id` (`OI-`, `R`, `D`), the item tree stamping `created_at` by macro; switch the callers' `--set name=` to a step slug | `src/config.yaml`, `src/templates/_partials/_playbook_driving.j2`, `specs/rule/0031-corrections-are-logged.md` | 1 | pending |
| 6.3 | e2e: empty dir → `OI-0001`, existing `OI-0007` → `OI-0008`, a correction gets `R0001-{slug}.md` | `booping-python/e2e/cases/create/` | 1 | pending |

Tests: integration tier, txtar — the three cases with stubbed date/session macros.

#### Definition of Done

- [ ] Task 6.1: a tree keyed `"{{ next_id('OI-') }}.md"` writes `OI-0001.md` in an empty destination and `OI-0008.md` beside `OI-0007.md`.
- [ ] Task 6.2: `bin/booping render src/templates/skills/playbook.md.j2` shows the agent-decision call without `$(date`.
- [ ] Task 6.3: `just e2e -k create` passes.

#### References

- `booping-python/src/booping/specs/open_items.py` — `create_item` id rule.
- `booping-python/e2e/cases/create/core-correction-entry-stamps-session-and-time.txtar` — case shape.

#### Verify

`just e2e -k create`

### M07 — Item callers move onto the operators

sp: 4
depends_on: [M03, M06]

#### Tasks

**Goal**: no prompt, hook or doc calls `booping items`; every item operation runs through `create`, `query`, `set`, `transition`, and batching is prose.
**Scope**: `playbooks/specs/playbook.yaml` (open_item `when:` texts and header comment), `playbooks/specs/guide/prompt.md`, `playbooks/specs/playbook.md`, `playbooks/project-manager/{work,intake}/prompt.md` + fixtures + `tests.yaml`, `playbooks/groom/intake/fable-5.md`, `playbooks/_scripts/open-items-follow-plan`, new `playbooks/specs/_schemas/open_item.yaml`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Rewrite the open_item `when:` texts and every prompt: add → `create` tree, list → `query --config core.specs.open_items.index`, plan → `set plan=` + `transition planned`, close/reopen → `transition`, size → `set size=` + `mdcheck` with the schema | `playbooks/specs/playbook.yaml`, `playbooks/specs/guide/prompt.md`, `playbooks/groom/intake/fable-5.md` | 2 | pending |
| 7.2 | Project-manager batching as prose over `query`, sizes/direct/cap rendered from `core.project_manager_playbook.batch`; its eval fixtures and asserts follow | `playbooks/project-manager/work/prompt.md`, `playbooks/project-manager/intake/prompt.md`, `playbooks/project-manager/intake/tests.yaml` | 1 | pending |
| 7.3 | `open-items-follow-plan` as `query … --output paths` + `transition` per item, failures absorbed; the size schema; its e2e case rewritten | `playbooks/_scripts/open-items-follow-plan`, `playbooks/specs/_schemas/open_item.yaml`, `booping-python/e2e/cases/transition/` | 1 | pending |

Tests: integration tier — follow-plan hook closes a planned item on develop `done` and reopens it on `fail`; the size schema rejects `XL`.

#### Definition of Done

- [ ] Task 7.1: `grep -rn 'booping items'` in `playbooks/`, `src/` and `specs/` returns nothing.
- [ ] Task 7.2: `bin/booping render-playbook project-manager` shows the sizes, direct sizes and cap from config in the batching paragraph.
- [ ] Task 7.3: `mdcheck playbooks/specs/_schemas/open_item.yaml` flags an item with `size: XL`; the follow-plan case passes.

#### References

- `playbooks/groom/_schemas/milestone.yaml` — schema shape and the restated-config comment.
- `playbooks/_scripts/open-items-follow-plan` — failure absorption kept.

#### Verify

`just e2e -k "transition and follow"`

### M08 — `booping items` removed; scan is `booping specs scan`

sp: 3
depends_on: [M07]

#### Tasks

**Goal**: `booping items` no longer exists; `booping specs scan` files the same items `items scan` did.
**Scope**: `booping-python/src/booping/commands/items.py` (removed), `commands/specs.py` (scan), `specs/open_items.py` (pruned to what `status.py`, `commands/run.py`, `commands/status.py`, scan and tests import), `cli.py`, e2e `cases/items/`, `tests/specs/open_items_test.py`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Move `_run_scan` into `booping specs scan [--tier]`, writing items through the M06 tree | `booping-python/src/booping/commands/specs.py` | 1 | pending |
| 8.2 | Remove `commands/items.py` and its registration; prune `open_items.py` (allocator, `move`, `set_size`, `pack`, `sized_open_items`, bulk close/reopen) | `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/cli.py` | 1 | pending |
| 8.3 | e2e: move the scan cases to `cases/specs/` as `specs scan`; delete the other `cases/items/` cases, keeping one `query`-based list case under `cases/query/` | `booping-python/e2e/cases/specs/`, `booping-python/e2e/cases/query/` | 1 | pending |

Tests: integration tier — the moved scan cases; status cases still pass.

#### Definition of Done

- [ ] Task 8.1: `booping specs scan` on the scan fixtures prints what `items scan` printed.
- [ ] Task 8.2: `booping items` is unknown; `just typecheck` is clean.
- [ ] Task 8.3: no `cases/items/` directory remains; `just e2e` passes.

#### References

- `booping-python/src/booping/commands/items.py` — `_run_scan`.
- `booping-python/e2e/cases/items/` — scan case shapes.

#### Verify

`just e2e -k "scan or status or query"`

### M09 — Docs, CLAUDE.md and CHANGELOG name the operator set

sp: 3
depends_on: [M05, M08]

#### Tasks

**Goal**: every doc surface names `set`, `transition`, `state`, `config`, `next_id`, `specs scan`, and none names a removed command.
**Scope**: `CLAUDE.md` (Commands sub-list, Playbooks run-state bullets, Lifecycle bullets naming `booping items`/`playbook-transition`), `README.md`, `documentation/*.md` (playbook, project_config, project_manager, specs_playbook, specs, vault, groom, develop), `CHANGELOG.md` Unreleased (Breaking: the renamed and removed commands), `booping-tracker/README.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | CLAUDE.md and README: the operator set with one capability phrase each; run-state wording; open-items lifecycle via operators | `CLAUDE.md`, `README.md` | 1 | pending |
| 9.2 | documentation pages and booping-tracker README; anchors that move are relinked | `documentation/playbook.md`, `documentation/project_manager.md`, `booping-tracker/README.md` | 1 | pending |
| 9.3 | CHANGELOG Unreleased: one Breaking line listing old → new commands and the removal of `booping items`, audience: plugin users only | `CHANGELOG.md` | 1 | pending |

Tests: none beyond `just docs` and the stale-name grep.

#### Definition of Done

- [ ] Task 9.1: `grep -n 'frontmatter-update\|marker-set\|playbook-transition\|playbook-state\|config-get\|booping items' CLAUDE.md README.md` returns nothing.
- [ ] Task 9.2: `just docs` builds strict; `grep -rn` of the same names in `documentation/` returns nothing.
- [ ] Task 9.3: the CHANGELOG line names each old command with its replacement and nothing internal.

#### References

- `CHANGELOG.md` — Unreleased section shape.

#### Verify

`just docs`

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
