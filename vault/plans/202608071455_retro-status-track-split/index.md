---
title: Retro as a separate track — retrospective artifacts own retro state, 
  plans end at done
type: feature
status: done
sp: 39
split_from: null
created: 2026-08-07 14:55
planned: null
started: 2026-08-07 15:25
completed: 2026-08-07 16:54
retro: null
goal: null
summary: "Retro/learn move to retrospectives/ artifacts with own statuses; develop
  ends plans at done; --target flag; migration 003"
commit: 3d5e4bed892d5a6a35d13ade9e4ede965aee9131
agents:
  research-codebase: a4cbb53cdf201893b
reviewed_at: 2026-08-07 15:24
sessions:
- a500d0c8-cfea-48f7-ada3-9c5832335959
- 29bf61be-afa2-4102-9572-7199e02688ad
metrics_active_minutes: 119
metrics_models:
- claude-fable-5
metrics_tokens_input: 444
metrics_tokens_output: 294626
metrics_tokens_cache_creation: 1805263
metrics_tokens_cache_read: 26954503
---

# Retro as a separate track — retrospective artifacts own retro state, plans end at done

## Context

Today the shipped playbooks chain their state machines through the plan's `plans/{slug}/index.md`: develop ends a sprint at `awaiting-retro`, retro moves it to `awaiting-learning`, learn closes it to `done`. ~80% of developed plans sit at `awaiting-retro` although development is finished — the plan listing buries done work under a status that means "done, retro pending". After this plan: develop closes the plan at `done`; the retro playbook takes a plan as input but persists its run state on a standalone retrospective artifact `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` in the vault, carrying `awaiting-retro` → `awaiting-learning` → `done`; the plan links to it via `retro:` frontmatter and the retro artifact links back via `plan:`; learn moves fully to the retro track. A `code_review: null` frontmatter seam is added now so code-review can get the same artifact-track treatment later without another frontmatter migration.

## Decisions

- **Retro artifact shape**: single file `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` — existing scaffold dir, slug matches the plan convention, one file is the run artifact.
- **Artifact addressing**: new explicit `--target {path}` flag on `booping playbook-transition` and `booping playbook-state`, overriding the machine's declared `artifact:` — chosen over `{instance}`-on-flat-machines and over directory-per-retro. A machine may omit `artifact:` entirely; omission plus no `--target` is an error naming the flag.
- **Retro queue**: query plans with `status: done` and `retro: null`. The query engine fails a clause when the key is absent, and the plan template already writes `retro: null` on every plan, so the queue is viable without an "unset" operator.
- **Skip sentinel**: a plan the user opts out of retro gets `retro: skipped` (non-null drops it from the queue); `drop-plan` stops writing `status:` — the plan is already `done`.
- **Learn moves fully**: learn queries retrospectives at `awaiting-learning` and closes the retro artifact to `done`; the plan is untouched by learn.
- **code-review interim**: `core.code_review_playbook.status` and both queries repoint to `{status: done, code_review: null}`; the code-review playbook stamps `code_review:` with the review date on completion. Its own artifact track stays out of scope.
- **Migration 003 — full relocate**: every existing `plans/{slug}/retro.md` moves to `retrospectives/{slug}.md` with links rewired; in-flight plans move to `done` with stubs at their matching retro status. Historical done plans get no `code_review:` key (absent key fails the queue clause, so they never flood the review queue); plans moving from `awaiting-retro` get `code_review: null` because they are today's review candidates.
- **Workdir convention**: retro and learn run with workdir = vault root and pass `--target retrospectives/{slug}.md`; a hook's `frontmatter-update` without a file target writes the resolved artifact, i.e. the retro file.

## Architecture

The plan lifecycle ends at develop: `groom` (`framing` … `ready-for-dev`) → `develop` (`ready-for-dev` → `in-progress` → `done` | `fail`). The retro track is a second machine on its own artifact: retro's `save` step creates `retrospectives/{slug}.md` (frontmatter `plan:`, `plans:`, `title`, `created`, `goal_verdicts:`), retro's machine drives `awaiting-retro` → `awaiting-learning`, learn's machine on the same artifact drives `awaiting-learning` → `done`. Cross-linking is frontmatter only: plan `retro:` → retrospectives path, retro `plan:` → plan path. Both playbooks' drivers resolve the artifact per run via `--target`; the shared `close-working-set` script reads the retro file from `BOOPING_ARTIFACT` and stamps every working-set plan's `retro:` back-link. The same pattern (status on plan queue key + `{key}: null` seam + standalone artifact) is what the future code-review track copies.

## Milestones

### M1: Engine — explicit `--target` on transition and state — 5 SP | done

**Goal**: `booping playbook-transition` and `booping playbook-state` can address a state artifact directly, and a `states:` machine may omit `artifact:`.

**Verify**: `just lint typecheck pytest`; manual `booping playbook-transition` round-trip against a temp file with `--target`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `--target {path}` to `playbook-transition`: overrides declared `artifact:`, relative paths resolve against workdir, mutually exclusive with `--instance`, `BOOPING_ARTIFACT` carries the resolved target, bootstrap on a missing target file stays legal only when the target status is `initial`. Make `artifact:` optional in a `states:` machine; a transition with neither declared artifact nor `--target` errors naming the flag. | `booping-python/src/booping/` (playbook-transition implementation), `booping-python/tests/` | 3 | done |
| 1.2 | Add `--target {path}` to `playbook-state` with the same resolution; the frontier report names the resolved target path; missing declared artifact without `--target` errors naming the flag. | `booping-python/src/booping/` (playbook-state implementation), `booping-python/tests/` | 2 | done |

#### Task 1.1 DoD

- [x] `playbook-transition {playbook} {to} --target {path}` writes `status:` to that file and hooks receive `BOOPING_ARTIFACT` = resolved target.
- [x] `--target` + `--instance` together exit 1 with a clear message.
- [x] A machine without `artifact:` loads; transition without `--target` on it exits 1 naming `--target`.
- [x] Tests cover: relative/absolute target, bootstrap via target, mutual exclusion, missing-artifact error.

#### Task 1.2 DoD

- [x] `playbook-state {playbook} --target {path}` reports that file's frontier.
- [x] Missing declared artifact without `--target` exits 1 naming the flag.
- [x] Tests cover the target path in the report and the error case.

**Blocked (1/2)**: manual retro walkthrough failed — an existing `--target` file written without `status:` (retro save's contract) is not bootstrappable, `playbook-transition` errors `no frontmatter status: key`; re-briefed the worker to treat a status-less existing artifact as `not-started` and bootstrap into it. **Resolved**: fix landed with 5 new tests (739 passing), walkthrough re-run green end to end.

---

### M2: Retro playbook on its own artifact — 7 SP | done

**Goal**: retro runs with workdir = vault root, creates `retrospectives/{slug}.md`, and its machine lives on that file.

**Verify**: `bin/booping render-playbook retro --project playbooks/_fixtures/vault` renders without STOP notices; step table and `## State` section reflect the new machine.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rewrite `states:` — machine omits `artifact:` (driver passes `--target`), statuses `awaiting-retro` → `awaiting-learning` (terminal for retro's machine), hooks become `frontmatter-update reviewed_at=...` (no file target — writes the artifact) + `script close-working-set` with the new argv. Update `core.retro_playbook`: `status: done`, `queries.candidates` `where: {status: done, retro: null}`, columns unchanged. | `playbooks/retro/playbook.yaml`, `src/config.yaml` | 2 | done |
| 2.2 | Rework `save` to write `retrospectives/{YYYYMMDDHHMM}_{kebab-title}.md` with frontmatter `plan:` (primary plan path), `plans:`, `title`, `created`, `goal_verdicts:` — no `status:` by hand, the first transition bootstraps it. Rewrite `playbook.md` prose: drop "retro statuses are a sub-path of the plan state-machine" and `plans/{slug}/retro.md`, state the workdir = vault root + `--target` convention. | `playbooks/retro/save/prompt.md` (and its `base.md` source when present), `playbooks/retro/playbook.md` | 3 | done |
| 2.3 | Update `intake`: queue renders from the new candidates query, plan selection by argument or queue, skipped siblings routed to `drop-plan` with the `retro: skipped` semantics named. | `playbooks/retro/intake/prompt.md` | 2 | done |

#### Task 2.1 DoD

- [x] `playbook.yaml` has no `artifact:` under the machine and the two edges carry the new hooks.
- [x] `core.retro_playbook.queries.candidates` filters `status: done, retro: null`.
- [x] Rendered `## State` section shows the new statuses and the `--target`-bearing invocations.

#### Task 2.2 DoD

- [x] `save` names the exact retrospectives path shape and every frontmatter key it writes, and writes no `status:`.
- [x] `playbook.md` carries no reference to `plans/{slug}/retro.md` or plan-status retro semantics.

#### Task 2.3 DoD

- [x] `intake` reads the queue via the config query, never a hardcoded status name.
- [x] Skip path names `drop-plan` and the `retro: skipped` outcome.

---

### M3: Scripts — close-working-set and drop-plan — 5 SP | done

**Goal**: the shared vault-commit script works from vault-root workdir with a standalone retro artifact; drop-plan stamps the skip sentinel.

**Verify**: `just pytest` (script-level tests where present); a dry run of each script against a scratch vault.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rework `close-working-set`: vault resolves from `BOOPING_WORKDIR` (now the vault root, not `plans/{slug}`), the retro file comes from `BOOPING_ARTIFACT`, the plan set from the retro artifact's `plans:` frontmatter; `--verdicts` stamps each plan's `retro:` with the vault-relative retrospectives path plus `goal:`; the commit includes the retro artifact and every touched plan; learn's call (`--status done --stage _lessons _booping --prefix learn`) keeps working against the same env. | `playbooks/_scripts/close-working-set` | 4 | done |
| 3.2 | Rework `drop-plan`: stamp `retro: skipped` and `goal: skipped`; stop writing `status:` and `completed:`; vault resolution updated for vault-root workdir. | `playbooks/retro/_scripts/drop-plan` | 1 | done |

#### Task 3.1 DoD

- [x] Script derives vault, retro path and plan set from env + artifact frontmatter — no `workdir.parent.parent`, no hardcoded `plans/{slug}/retro.md`.
- [x] `--verdicts` writes plan `retro:` back-links pointing at `retrospectives/{slug}.md`.
- [x] Both retro's and learn's hook argv shapes run green against a scratch vault.

#### Task 3.2 DoD

- [x] A dropped plan's diff touches only `retro:` and `goal:`.

---

### M4: Learn playbook on the retro track — 5 SP | done

**Goal**: learn's unit of work is the retrospective artifact — queried at `awaiting-learning`, closed to `done` on it.

**Verify**: `bin/booping render-playbook learn --project playbooks/_fixtures/vault` renders without STOP notices.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite `states:` — machine omits `artifact:`, `awaiting-learning` → `done` (terminal) with the close-working-set hook. Update `core.learn_playbook`: `queries.candidates` gets its **own explicit glob** `retrospectives/*.md` (omitting `glob` silently inherits the plans glob), `where: {status: awaiting-learning}`, columns include `plan`. | `playbooks/learn/playbook.yaml`, `src/config.yaml` | 2 | done |
| 4.2 | Update `intake`, `write` and `transition` step prose: the retro artifact is addressed directly (argument = retrospectives path, or the queue), workdir = vault root, transitions pass `--target`; drop the plan-indirection lookup through `retro:` frontmatter. | `playbooks/learn/intake/prompt.md` (and `base.md`), `playbooks/learn/write/prompt.md` (and `base.md`), `playbooks/learn/transition/prompt.md` when present | 3 | done |

#### Task 4.1 DoD

- [x] `queries.candidates` declares `glob: [retrospectives/*.md]` explicitly.
- [x] Rendered `## State` shows `awaiting-learning` → `done` on the retro artifact via `--target`.

#### Task 4.2 DoD

- [x] No step resolves a retrospective through a plan's `retro:` field.
- [x] Learn's eval fixtures under `playbooks/learn/*/_fixtures/` carry no stale `plans/{slug}/retro.md` paths.

---

### M5: Develop terminal `done` + code_review seam — 5 SP | done

**Goal**: develop closes plans at `done`; the `code_review:` frontmatter seam exists and code-review's queue reads it.

**Verify**: `bin/booping render-playbook develop --project playbooks/_fixtures/vault` and same for `code-review`; both render without STOP notices.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Develop machine: `in-progress` → `done` (terminal) replacing `awaiting-retro`; `wrap-up` handoff prose repointed — the sprint is closed at `done`, retro is offered as `/playbook retro {plan-path}` with no status gate. | `playbooks/develop/playbook.yaml`, `playbooks/develop/wrap-up/prompt.md` | 2 | done |
| 5.2 | Add `code_review: null` to the plan frontmatter template and partial. Repoint `core.code_review_playbook`: `status: done`, `queries.review_candidates` and `queries.scope_candidates` both `where: {status: done, code_review: null}`. Code-review playbook stamps `code_review: "{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` on the reviewed plan at completion via `booping frontmatter-update`. | `docs/template_plan_frontmatter.md`, `playbooks/_partials/plan_frontmatter.md`, `src/config.yaml`, `playbooks/code-review/` (the step that closes a review) | 3 | done |

#### Task 5.1 DoD

- [x] Develop's rendered `## State` shows `in-progress` → `done`; no `awaiting-retro` anywhere in the render.
- [x] `wrap-up` names no status gate for retro.

#### Task 5.2 DoD

- [x] New plans render `code_review: null` in identity frontmatter.
- [x] Both code-review queries filter `status: done, code_review: null`.
- [x] A completed review's plan diff shows a dated `code_review:` value.

---

### M6: Migration 003 — retro track split — 5 SP | done

**Goal**: an existing vault converts in one idempotent pass; the fixture watermark advances.

**Verify**: run the migration procedure against a scratch copy of a populated vault twice — second pass reports nothing to do.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Author `migrations/003_retro-track-split/migration.md` (frontmatter `id: 3`) following the 001/002 shape: idempotent ruamel script + confirm block. Conversions: plans at `awaiting-retro` → `status: done`, `retro: null` kept, `code_review: null` added (they are today's review candidates); plans at `awaiting-learning` → `status: done` and their `plans/{slug}/retro.md` relocated to `retrospectives/{slug}.md` with `status: awaiting-learning`, `plan:` back-link and the plan's `retro:` repointed; done plans with a `plans/{slug}/retro.md` → relocated with `status: done` and links rewired; done plans with `goal: skipped` and `retro: null` → `retro: skipped`; historical done plans get no `code_review:` key. Skip-if-nothing, "kept existing" reporting, never silent overwrite. | `migrations/003_retro-track-split/migration.md` | 4 | done |
| 6.2 | Bump the fixture watermark: `playbooks/_fixtures/vault/.booping` `latest_migration: 3`. | `playbooks/_fixtures/vault/.booping` | 1 | done |

#### Task 6.1 DoD

- [x] Every conversion above is covered, idempotent, and reported per file.
- [x] Second run against a converted vault reports nothing to do.
- [x] Frontmatter writes preserve comments/key order (ruamel round-trip, per 001/002).

#### Task 6.2 DoD

- [x] `just snapshots` reports no migration-gate STOP against the fixture vault.

---

### M7: Fixtures, snapshots, dead code, docs — 7 SP | done

**Goal**: the repo is internally consistent — fixture vault, committed reports, code and docs all speak the new lifecycle.

**Verify**: `just ci` green (lint, typecheck, pytest, snapshots, mdcheck).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Rewrite the fixture vault to the new design: add `retrospectives/` with fixture artifacts, convert the six fixture plans (`awaiting-retro` pair → `done` + `retro: null` + `code_review: null`; the `awaiting-learning` one → `done` + a retrospectives fixture at `awaiting-learning` with links). Re-accept snapshots: `just snapshots-accept` for retro, learn, develop, code-review; `just mdcheck` green (adjust `rules.yaml` siblings where status names moved). | `playbooks/_fixtures/vault/`, `playbooks/{retro,learn,develop,code-review}/_reports/` | 3 | done |
| 7.2 | Delete the orphaned `Retro` model: `context/retro.py`, its `context.retros` wiring in `context/__init__.py`, and `tests/context/retro_test.py`. | `booping-python/src/booping/context/retro.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/tests/context/retro_test.py` | 2 | done |
| 7.3 | Docs sweep — every surface naming the old chaining: README Statuses section, CLAUDE.md (plan-lifecycle bullets + playbook descriptions), `documentation/{index,quick_start,develop,retro,learn,code_review,vault,install,project_config}.md`, retro/learn `_specs/` prose that states the old design rationale. | `README.md`, `CLAUDE.md`, `documentation/`, `playbooks/retro/_specs/`, `playbooks/learn/_specs/` | 2 | done |

#### Task 7.1 DoD

- [x] `just snapshots` and `just mdcheck` pass.
- [x] No fixture plan carries `awaiting-retro` or `awaiting-learning` as a plan status.

#### Task 7.2 DoD

- [x] `grep -r "context.retros\|Retro.load_all"` over `booping-python/` and `src/` returns nothing.
- [x] `just lint typecheck pytest` pass after deletion.

#### Task 7.3 DoD

- [x] `grep -rn "awaiting-retro\|awaiting-learning"` over `README.md CLAUDE.md documentation/` names only the retro-track (retrospective-artifact) semantics, never a plan status.

---

## Final Verification

- [x] `just ci` green end to end.
- [x] `bin/booping render-playbook {name} --project playbooks/_fixtures/vault` clean (no STOP) for retro, learn, develop, code-review, groom.
- [x] Rendered bodies reviewed: no stale state names, no prose duplicating rendered tables, no placeholder leaks.
- [x] A manual retro walkthrough on a scratch vault: develop-finished plan at `done` → retro creates the retrospectives artifact → transition to `awaiting-learning` stamps the plan's `retro:` link → learn closes the artifact to `done`.

## Out of scope

- code-review's own artifact track (its `code_review:` seam and queue repoint ship here; the standalone review artifact + machine is the follow-up pilot).
- Post-implementation prose-shape reshape milestone — declared out of scope at intake.
- Any change to groom's machine or the plan directory shape.

## CLAUDE.md impact

Owned by task 7.3: the plan-lifecycle section (status chaining, terminal statuses), the retro/learn/develop playbook descriptions, and the CLI section's `playbook-transition` / `playbook-state` signatures gain `--target`.
