---
title: Deterministic plan transitions via config-wired hooks + Harel superstates
type: feature
status: done
sp: 23
split_from: null
created: 2026-06-15 11:48
commit: 39bba74902d8c0276ebd3d68f3ffce3a53c3ace8
planned: 20260615 11:44
started: 20260615 11:48
completed: null
retro: null
goal: null
summary: "Status transitions become a single deterministic CLI call (`booping transition`) that runs config-listed hook scripts for every mechanical mutation (frontmatter stamps, git HEAD snapshot, render-sprints, vault commit). The LLM only decides which move to make; it never hand-edits frontmatter or hand-runs git. Removes ~12 per-transition hand-edit drift points and collapses duplicated transitions/mutations via Harel OR-superstates."
---

# Deterministic plan transitions via config-wired hooks + Harel superstates

## Context

Today every plan transition is a set of **manual LLM actions**, described as prose in `_plan_transitions.j2`: hand-edit `status:`, hand-set date stamps (`planned`/`started`/`completed`), hand-copy git HEAD into `commit:`, hand-run `git add/commit`, and (separately) remember `booping render-sprints`. ~12 distinct mutation points across 14 edges, each a drift risk (wrong date format, forgotten commit snapshot, stale sprints.md, missed vault commit).

After this plan: a transition is one deterministic CLI call — `booping transition <to> <plan>` — that validates the move against the statemap, then runs an **ordered list of hook scripts wired in config**. Every mechanical mutation is a hook (no LLM). The LLM's only job is deciding *which* edge fires (the `when` trigger) and clearing judgment gates; it then calls one command.

Two mechanisms combine:
1. **Hooks** — `booping transition` is a pure hook-runner. Deterministic ops (set status, frontmatter stamps, HEAD snapshot, render-sprints, vault commit) are all hooks listed in `src/config.yaml`, not special-cased dispatcher logic.
2. **Harel OR-superstates** — statuses group into superstates; a transition or entry/exit hook declared on a superstate is inherited by every substate. Collapses today's duplicated `→ cancelled`/`set completed`/`set started` edges into one group-level declaration. Only the OR-superstate subset of statecharts — no AND-states, no history.

Companion cleanup in the same sprint: drop the redundant `business_goal` frontmatter field (the harness guesses it; user never asked to assist) and replace it with `summary` — a brief plan-intent line used for search and shown in `sprints.md`.

## Decisions

- **Hook vocabulary**: hooks are booping subcommands referenced by name in config. Initial set: `frontmatter-update`, `render-sprints`, `vault-commit`. Dispatcher maps hook names → actions; unknown hook name = exit 2. — Keeps hooks config-wired, not hardcoded in the dispatcher.
- **Interpolation, not a DSL**: `frontmatter-update` values support simple substitution — `@now` → `yyyymmdd hh:mm`, `@today` → `yyyy-mm-dd`, `@head` → `git rev-parse HEAD`; anything else is a literal. Plain interpolation, no expression language. — Smallest thing that covers every deterministic mutation in the current on_exit table.
- **Frontmatter round-trip is minimal-diff, block-scoped**: `frontmatter-update` must (1) split the `.md` on the first two `---` delimiters into [yaml-block, body], (2) parse + mutate **only the yaml block**, (3) concatenate the **unmodified body verbatim**. Never feed the whole `.md` to a YAML parser. Preserve key order; touched keys only. — `ruamel.yaml` round-trip mode keeps the diff minimal and the formatting stable. (No comment-preservation requirement — real plans carry none.)
- **Superstate semantics**: OR-superstates only. A status's valid edges = its own `transitions` ∪ inherited superstate `transitions`. On a `to` collision the substate-specific edge wins (specificity). Superstate `on_entry`/`on_exit` hooks run when a transition crosses the superstate boundary; exit hooks run inner→outer, entry hooks outer→inner. — The minimal Harel subset that removes duplication without orthogonality/history complexity.
- **Behavior preservation**: the new hook wiring must reproduce **exactly** the mutations in the current `plan.statuses[*].transitions[*].on_exit` table — no behavior change, only relocation (edge → superstate boundary where shared). Verified by an explicit old→new mutation-equivalence table. — De-risks the config rewrite; this milestone is a refactor under a feature umbrella.
- **Override contract**: additive only. Add `plan.superstates` + `plan.hooks` (new dict keys, deep-merge cleanly). Leave per-status `transitions` list-replace-wholesale as documented. No `shallow_merge_keys` change yet — project-level per-status override stays a half-possible future feature until a real use case appears. — No project currently overrides `plan.statuses`; don't pay the contract-rewrite cost speculatively.
- **Dispatcher does NOT enforce gates**: `transition` applies mutations and trusts the caller cleared judgment gates (`when`/`gates` stay LLM-facing prose). — Per user: deterministic hooks handle mutations; judgment stays with the skill.
- **`business_goal` → `summary`**: remove `business_goal` everywhere; add `summary` (brief intent line, written by `/groom`, shown as a `sprints.md` column). — `business_goal` is guessed, never user-assisted; `summary` earns its place via search + listing.

## Architecture

Load-time inputs unchanged (`Context.assemble()` reads `src/config.yaml` + vault override). New runtime path:

```
LLM decides edge ──> booping transition <to> <plan>
                       │
                       ├─ resolve current status from plan frontmatter
                       ├─ resolve valid edges = own ∪ inherited superstate edges
                       ├─ validate <to> is reachable  (else exit 1)
                       └─ run ordered hook list:
                            1. frontmatter-update status=<to>           (always, dispatcher-prepended)
                            2. <superstate on_exit hooks>  (inner→outer, boundary crossed)
                            3. <edge hooks>                (from matched transition)
                            4. <superstate on_entry hooks> (outer→inner, boundary crossed)
                            5. <plan.hooks.post>           (render-sprints, vault-commit)
```

`_plan_transitions.j2` renders the human-readable `On exit` column **from the hook lists** (single source: machine list drives both execution and the LLM-facing prose). Skill bodies replace "hand-edit `status:` + `git commit`" prose with "call `booping transition <to> <plan>`".

Callers of `booping transition`: groom, develop, retro, learn (via the shared partial). `frontmatter-update` is also usable standalone by `/chat` for chore frontmatter tweaks.

## Milestones

### M1: `frontmatter-update` hook + interpolation — 4 SP | pending

**Goal**: `booping frontmatter-update <plan> 'key=val ...'` sets frontmatter keys with `@now`/`@today`/`@head` interpolation, preserving comments, key order, and body.

**Verify**: `booping frontmatter-update <fixture-plan> 'planned=@now commit=@head' && git -C <vault> diff` shows only the two keys changed, comments intact.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `ruamel.yaml` dep; block-scoped helper: split `.md` on first two `---` into [yaml, body], parse+mutate yaml only, concat body verbatim; preserve key order, minimal diff | `booping-python/pyproject.toml`, `booping-python/src/booping/context/_yaml.py` | 2 | pending |
| 1.2 | `commands/frontmatter_update.py`: arg parse (`<plan>` + `key=val` pairs), `@now`/`@today`/`@head` interpolation, write-back, log line, exit codes; wire into `cli.py` | `booping-python/src/booping/commands/frontmatter_update.py`, `booping-python/src/booping/cli.py` | 2 | pending |

#### Task 1.1 DoD
- [ ] Helper splits on the first two `---` delimiters; the body after the closing `---` is concatenated back byte-identical.
- [ ] Round-trip with no key changes leaves the whole file byte-identical (key order preserved).
- [ ] Whole-`.md` is never passed to the YAML parser (only the extracted block).
- [ ] `ruamel.yaml` pinned to a version confirmed on PyPI.

#### Task 1.2 DoD
- [ ] `frontmatter-update <plan> 'planned=@now'` sets `planned` to `yyyymmdd hh:mm`, leaves all other keys + comments + body untouched.
- [ ] `@head` resolves to `git rev-parse HEAD` of the repo; `@today` → `yyyy-mm-dd`; unknown token written literally.
- [ ] Missing plan → exit 1 + stderr; malformed `key=val` → exit 1 + stderr.
- [ ] Log line appended: `<iso>: [frontmatter-update] <plan> <keys>`.
- [ ] `booping frontmatter-update --help` reflects the surface.

---

### M2: Superstate config schema + edge-resolution engine — 4 SP | pending

**Goal**: `src/config.yaml` gains `plan.superstates` + `plan.hooks`, and a resolver computes the valid edges + boundary hooks for any status (no dispatcher yet).

**Verify**: a unit test asserts `resolve_edges("in-spec")` returns own edges ∪ inherited `planning` edges, and `resolve_hooks("in-spec","awaiting-plan-review")` returns the full ordered hook list matching the equivalence table.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `plan.superstates` (planning/executing/closing/terminal per grouping) + `plan.hooks.post`; convert every `on_exit` prose entry to a `hooks` list; build old→new mutation-equivalence table as a test fixture | `src/config.yaml`, `booping-python/tests/__fixtures__/*` | 2 | pending |
| 2.2 | Resolver in the context layer: `resolve_edges(status)` (own ∪ inherited, substate wins on collision) and `resolve_hooks(from,to)` (status-set + on_exit boundary + edge + on_entry boundary + post), with tests | `booping-python/src/booping/context/plan.py` (or new `lifecycle.py`), `booping-python/tests/context/*` | 2 | pending |

Grouping (accepted): `planning`{backlog, in-spec, awaiting-plan-review, ready-for-dev}; `executing`{in-progress}; `closing`{awaiting-retro, awaiting-learning}; `terminal`{done, fail, cancelled}. Group edges: any `planning → cancelled`, any `planning → in-progress`, `executing → fail`. Boundary hooks dedupe the shared `started`/`commit` (executing on_entry) and `completed` (terminal on_entry + closing on_entry) stamps.

#### Task 2.1 DoD
- [ ] Every mutation in the pre-change `on_exit` table appears exactly once in the new wiring (edge, on_entry, or on_exit) — equivalence table checked in.
- [ ] `plan.superstates` + `plan.hooks` deep-merge cleanly over an empty project override (no contract regression).

#### Task 2.2 DoD
- [ ] `resolve_edges` returns own + inherited edges; substate edge wins on `to` collision.
- [ ] `resolve_hooks(from,to)` returns the ordered list matching the equivalence fixture for all 14 current edges + the new group edges.
- [ ] Unreachable `to` → resolver signals invalid (no silent empty list).

---

### M3: `transition` dispatcher (hook-runner) — 4 SP | pending

**Goal**: `booping transition <to> <plan>` validates the move and runs the resolved hook list end-to-end (frontmatter stamps → render-sprints → vault-commit).

**Verify**: `booping transition awaiting-plan-review <fixture-plan>` on an `in-spec` plan → frontmatter shows `status: awaiting-plan-review` + `planned` + `commit`, `sprints.md` regenerated, one vault commit `awaiting-plan-review: <kebab-title>`; invalid target exits 1 with the allowed targets listed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `commands/transition.py`: read status, validate via resolver, build + run ordered hooks (dispatch by hook name to `frontmatter-update`/`render-sprints`/`vault-commit`), idempotent re-run, exit codes, log line; wire into `cli.py` | `booping-python/src/booping/commands/transition.py`, `booping-python/src/booping/cli.py` | 2 | pending |
| 3.2 | `commands/vault_commit.py` (exact location, not inline): path-scoped staging only — the passed plan + `sprints.md` + explicit `--also <path>...` extras; **never** `git add -A`/`.`; commit `<to-status>: <kebab-title>`; integration test covering one full transition | `booping-python/src/booping/commands/vault_commit.py`, `booping-python/tests/commands/*` | 2 | pending |

#### Task 3.1 DoD
- [ ] Valid edge runs all resolved hooks in order; final frontmatter + sprints.md match expectation.
- [ ] Invalid `<to>` → exit 1 + stderr listing allowed targets for the current status.
- [ ] Unknown hook name in config → exit 2 + stderr.
- [ ] Hook failure mid-list → exit 2, stderr names the failed hook (no partial silent success).
- [ ] **Idempotent re-run**: if the plan's status already equals `<to>`, the command does not error on the (now-missing) `<from>` edge — it re-runs the post hooks (`render-sprints`, `vault-commit`) so a mid-list failure is recoverable by re-invoking the same command.
- [ ] Log line: `<iso>: [transition] <plan> <from>→<to>`.
- [ ] `booping transition --help` reflects the surface.

#### Task 3.2 DoD
- [ ] `vault-commit` stages **only** the passed plan + `sprints.md` + any `--also` paths — never `git add -A`/`.`.
- [ ] Commits with `<to-status>: <kebab-title>`.
- [ ] Integration test: `in-spec → awaiting-plan-review` end-to-end produces exactly one commit with the expected tree.

---

### M4: Rewrite `_plan_transitions.j2` + skill bodies to call `transition` — 4 SP | pending

**Goal**: the transitions partial renders the `On exit` column from config hook lists and instructs callers to run `booping transition`; manual `status:` edit + `git commit` prose is gone from all skills.

**Verify**: `bin/booping render src/templates/skills/groom.md.j2` (+ develop/retro/learn) shows the `booping transition` call and an `On exit` column derived from hooks; no "hand-edit `status:`" or inline `git commit -m` prose remains.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite `_plan_transitions.j2`: render `On exit` from `hooks` lists (incl. inherited boundary hooks); replace the manual edit + git-commit preamble with a single `booping transition <to> <plan>` instruction | `src/templates/_partials/_plan_transitions.j2` | 2 | pending |
| 4.2 | Verify-render across groom/develop/retro/learn; fix any prose in skill bodies that restates manual transition steps | `src/templates/skills/{groom,develop,retro,learn}.md.j2` | 2 | pending |

#### Task 4.1 DoD
- [ ] `On exit` column content matches the config `hooks` lists (no hand-written prose duplication).
- [ ] Partial preamble instructs `booping transition`, not hand-edit + git.
- [ ] Inherited superstate edges (e.g. `→ cancelled`, `→ in-progress`) render in each owning skill's slice.

#### Task 4.2 DoD
- [ ] All four skills render with no stale manual-transition prose, no `{{placeholder}}` leaks.
- [ ] No skill body restates the flow outside the rendered table.

---

### M5: `business_goal` → `summary` — 4 SP | pending

**Goal**: `business_goal` removed everywhere; `summary` added to the model, frontmatter template, plan-frontmatter doc, and shown as a `sprints.md` column; `/groom` writes a bounded `summary`; existing vault plans migrated in the same sprint.

**Verify**: load a vault → `Plan` has `summary`, no `business_goal`; `booping render-sprints` output has a `summary` column; `grep -rn business_goal` (excluding this plan + retro) returns nothing in the repo; existing project-vault plans show `summary:` and no `business_goal:`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Model + render: drop `business_goal`, add `summary` to `Plan`; add `summary` to `_plan_frontmatter.j2` + `docs/template_plan_frontmatter.md`; add `summary` column to `sprints.md.j2`; instruct `/groom` to write `summary` with a **bounded shape** (single line, ≤ ~120 chars / ~20 words, plain intent, no prose) | `booping-python/src/booping/context/plan.py`, `src/templates/_partials/_plan_frontmatter.j2`, `docs/template_plan_frontmatter.md`, `src/templates/sprints.md.j2`, `src/templates/skills/groom.md.j2` | 2 | pending |
| 5.2 | Purge `business_goal` from task docs + plan-template checklist + tests + fixtures | `docs/task_feature.md`, `docs/task_refactoring.md`, `docs/plan_templates/backend.md`, `booping-python/tests/context/plan_test.py`, `booping-python/tests/__fixtures__/vault-full/plans/*.md` | 1 | pending |
| 5.3 | One-shot migration of this project's vault: strip `business_goal:`, inject empty `summary:` (preserving key position) across `~/Claude/claude-booping/plans/*.md` via `frontmatter-update` (reuses M1; no new tooling). Other projects' vaults migrate harmlessly-lazily (extra key ignored, missing `summary` → empty) | `~/Claude/claude-booping/plans/*.md` | 1 | pending |

#### Task 5.1 DoD
- [ ] `Plan.summary` loads from frontmatter; `business_goal` field gone from model + frontmatter template + doc.
- [ ] `sprints.md` renders a `summary` column.
- [ ] `/groom` body instructs writing `summary` with the bounded shape stated above (Rule 7 — return contract bounded).

#### Task 5.2 DoD
- [ ] `grep -rn business_goal` over the repo (excluding this plan + any retro) is empty.
- [ ] Tests + fixtures updated; `just test` green.

#### Task 5.3 DoD
- [ ] No `~/Claude/claude-booping/plans/*.md` contains `business_goal:`; each carries a `summary:` key.
- [ ] Migration leaves all other frontmatter keys + bodies byte-identical (block-scoped via M1 helper).

---

### M6: CLAUDE.md + end-user docs + lifecycle doc — 3 SP | pending

**Goal**: project + end-user docs reflect the new subcommands, config schema (`superstates`/`hooks`), the `summary` field, and the deterministic transition flow.

**Verify**: docs name `transition`/`frontmatter-update`/`vault-commit`; `documentation/project_config.md` documents `plan.superstates` + `plan.hooks` + `summary`; lifecycle overview renders.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Update `CLAUDE.md`: CLI section (new subcommands), config schema (superstates + **hook vocabulary/mechanics** — internal home for these), plan-lifecycle (transitions now via `booping transition`), `summary`, editing conventions | `CLAUDE.md` | 1 | pending |
| 6.2 | Update `documentation/project_config.md` — audience-scoped: document `summary` + a **brief** note that statuses group into superstates (an overridable surface); **do not** document internal hook mechanics (`render-sprints`/`vault-commit` vocabulary) here (Rule 6 — those live in CLAUDE.md). Add deterministic-transition note to `plan_lifecycle_overview.md.j2`; spot-check other `documentation/*.md` for stale manual-transition text | `documentation/project_config.md`, `src/templates/docs/plan_lifecycle_overview.md.j2`, `documentation/*.md` | 2 | pending |

#### Task 6.1 DoD
- [ ] CLAUDE.md CLI + config-schema + lifecycle sections name the new subcommands, superstates, hooks, and `summary`.

#### Task 6.2 DoD
- [ ] `project_config.md` documents `summary` + a brief superstate note (overridable surface, additive-merge); hook mechanics are **absent** from end-user docs (Rule 6).
- [ ] No `documentation/*.md` describes transitions as manual frontmatter edits.

---

## I/O contract

**`booping frontmatter-update <plan> 'key=val ...'`**
- args: positional plan path; one or more `key=val` (value may be `@now`/`@today`/`@head`/literal).
- stdout: none on success (or one-line confirmation). stderr: errors. Exit `0` ok, `1` user error (missing plan, malformed pair), `2` internal.
- side effect: log line `<iso>: [frontmatter-update] <plan> <keys>`.

**`booping transition <to> <plan>`**
- args: positional target status; plan path.
- stdout: `<from> → <to>`. stderr: errors. Exit `0` ok, `1` invalid edge / unknown status / plan not found (stderr lists allowed targets), `2` hook failure / unknown hook.
- side effect: runs hook list; log line `<iso>: [transition] <plan> <from>→<to>`.

**`booping vault-commit`** (hook; not typically called directly)
- stages plan + sibling artifacts + `sprints.md`, commits `<to-status>: <kebab-title>`.

## Out of scope

- Gate enforcement in the dispatcher (judgment gates stay LLM-side).
- `shallow_merge_keys` for per-status project override (additive superstates only).
- AND-states / history pseudostates (OR-superstates only).
- PostToolUse/SessionStart sprints.md hook bundle (separate queued plan).
- Migrating **other** projects' vaults (only this project's vault is migrated, M5.3; others are harmless — extra key ignored, missing `summary` → empty).

## Risk register

| Risk | Mitigation | Status |
|------|-----------|--------|
| **Mid-flight hook failure** — status set, later hook fails → uncommitted/partial state; naive re-run fails on stale `<from>`. | M3.1 makes `transition` **idempotent**: if status already == `<to>`, re-run post hooks instead of erroring. Hook failure → exit 2 naming the failed hook; operator re-runs the same command to converge. | mitigated in M3.1 |
| **Git working-tree collision** — `vault-commit` bundling unrelated user WIP. | M3.2: **path-scoped staging only** (passed plan + `sprints.md` + explicit `--also`), never `git add -A`/`.`. Residual edge: user WIP *inside the plan file itself* would be bundled — accepted (the plan file is owned by the transition flow). | accepted (user) |

## Delivery

- Implementation branch + PR target base: **`release/0.1.6`** (not `main`). `/develop` opens the PR against `release/0.1.6`.

## CLAUDE.md impact

Update `## CLI` (new subcommands `transition`, `frontmatter-update`, `vault-commit`), `## Config schema` (add `plan.superstates`, `plan.hooks`; note `on_exit`→`hooks`), `## Plan lifecycle` (transitions now executed via `booping transition`, not manual frontmatter edits), and the frontmatter field list (`business_goal`→`summary`). Covered by M6.1.

## Proposed rendered prose (advance review — per request)

Sample of the rewritten `_plan_transitions.j2` preamble + one status slice, so the prose direction can be approved **before** development. Final full prose lands in M4.

> ## Plan Transitions
>
> This table is the contract. When an internal action matches a `When` trigger, verify the `Gates` hold, then execute the move with one command — it applies every mechanical mutation (status, date stamps, commit snapshot, sprints.md, vault commit) deterministically:
>
> ```bash
> booping transition <to-status> plans/<plan-file>.md
> ```
>
> Do not hand-edit `status:` or hand-run `git commit` — the command owns all of it.
>
> ### `in-spec` — /groom is actively specifying…
>
> | To | When | Gates | On exit (auto) |
> |----|------|-------|----------------|
> | `awaiting-plan-review` | Draft complete | Cross-validation; every task estimated | sets `planned`, `commit` |
> | `cancelled` *(via planning)* | User shelves the work | — | sets `completed` |

---

# Quality Checklist

## Frontmatter
- [ ] Matches plan frontmatter template.
- [ ] `sp` (23) equals sum of per-task SP.

## Content
- [ ] Context names the user-visible behavior change (one command vs manual edits).
- [ ] Every task lists exact files; every DoD is checkbox + invocation-verifiable.
- [ ] Each milestone executable from a fresh session with only the plan.

## I/O contract
- [ ] Arg/flag shape enumerated for all three subcommands.
- [ ] Exit codes defined per failure mode.
- [ ] stdout vs stderr separation specified.

## Skill-design hygiene
- [ ] `On exit` rendered from config hooks — no prose duplication.
- [ ] No restated flow outside the rendered table.
- [ ] Structured facts (superstates, hooks) in `src/config.yaml`, not prose.

## Anti-patterns (must be absent)
- [ ] No TBD/TODO/implement-later.
- [ ] No task spanning unrelated concerns.
- [ ] No stale state names; no manual-transition prose left after M4.

## External references validated
- [ ] `ruamel.yaml` version confirmed on PyPI.
- [ ] Template + doc paths exist; lazy-load links resolve.

## Behavior preservation
- [ ] Old→new mutation-equivalence table proves no transition changes its frontmatter effects.
