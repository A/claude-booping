---
status: cancelled
title: Playbook review-gate importance levels
type: feature
sp: 18
split_from: null
created: 2026-08-02 11:47
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Playbook review gates carry high/medium/low importance; a render-time --review-level
  flag dials run review depth"
commit: null
plan_status: awaiting-plan-review
agents:
  research-codebase: a4b0ce5f4b5988d38
  draft-plan: aea349969b3bd39bd
sessions:
- b78f9d61-f9ac-4790-8980-8b19f4af7de7
metrics_active_minutes: 12
metrics_models:
- claude-fable-5
metrics_tokens_input: 129
metrics_tokens_output: 101494
metrics_tokens_cache_creation: 573648
metrics_tokens_cache_read: 6719389
---

# Playbook review-gate importance levels

## Context

`booping render-playbook` renders each step's review gate from a scalar `review_gate:` frontmatter string; when present, the driver always pauses after that step for user confirmation. There is no way to express that some gates matter more than others, and no way for a run to dial review depth up or down. After this plan: a step carries `review_gates:` — a list of `{gate, importance}` entries (`importance` ∈ `high|medium|low`, default `medium`) — and `render-playbook` gains `--review-level {autonomous,low,medium,high}` (default `medium`) that filters which gates render into the composed procedure. The driver maps the user's prompt prose to the flag once per run: "review each step" → `low`, "only main steps" → `high`, "autonomous" → `autonomous`, nothing stated → default. A filtered gate renders nothing, so the driver mechanically sees nothing to honor.

## Decisions

- **Frontmatter shape**: `review_gates: [{gate, importance}]`, `importance` optional defaulting to `medium`; key absent → no gates; multiple entries allowed, each fires separately — settled with the user at intake.
- **Legacy scalar `review_gate:`**: blocking STOP (new `GraphProblem`), matching the legacy `agent:` key precedent — loud migration, one shape in the codebase.
- **Malformed list entry**: non-mapping entry, missing `gate`, or unknown `importance` → blocking STOP (`bad_review_gate`), following the `bad_node`/`bad_state` pattern — a gate silently dropped is a review silently skipped.
- **Flag vocabulary**: `--review-level {autonomous,low,medium,high}`, default `medium`, threshold semantics — `low` renders all gates, `medium` renders medium+high, `high` renders high only, `autonomous` renders none (fully unattended run).
- **Filter application point**: Python-side in `compose()` before Jinja — the template iterates the pre-filtered list; no level vocabulary leaks into `_playbook_step.j2`.
- **Gate bullet content**: unchanged from today — importance is filter-only, never rendered.
- **`--step` output**: keeps its no-gate-chrome contract, unchanged; `compose_step()` is not touched by the filter.
- **`record-decision`'s `"none — mechanical log"` gate**: dropped entirely in migration — it is a non-gate that does not fit `{gate, importance}`.
- **Driver mapping scope**: strictly user-prose → flag value; the driver never infers importance for un-annotated gates (schema default `medium` keeps them firing at the default level, i.e. today's behavior).

## Architecture

`Step` (`booping-python/src/booping/context/playbook.py`) gains `review_gates: list[ReviewGate]` (default empty) replacing `review_gate: str | None`; `ReviewGate` is a pydantic model `{gate: str, importance: Literal["high","medium","low"] = "medium"}` following the `plan_type`/`Playbook.scope` Literal precedent. `_load_step` parses the list and reports the two new blocking problems. `render-playbook`'s `compose()` receives the active level (threaded like `include_lessons`) and computes each step's visible gates before `step_tmpl.render(...)`; `_playbook_step.j2` renders one gate bullet per surviving entry in today's format. Callers: the `/playbook` and `/groom-playbook` skills invoke `booping render-playbook` per `_playbook_driving.j2`, which gains the prose→flag rule and pluralizes gate honoring; its AskUserQuestion wiring is unchanged. `playbook-authoring`'s `step-prompt` step generates wrappers carrying the gate key, so its body, spec, and eval suite move to the new shape in the same sprint.

## Milestones

### M1: Model and loader — 5 SP | pending

**Goal**: `Step.review_gates` parses the new list shape with validation; the legacy scalar and malformed entries are blocking problems.

**Verify**: `just test` green in `booping-python/`; `uv run --project booping-python pytest tests/context/playbook_test.py -k review_gate` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `ReviewGate` pydantic model (`gate: str`, `importance: Literal["high","medium","low"] = "medium"`); replace `Step.review_gate` with `review_gates: list[ReviewGate]` default empty | `booping-python/src/booping/context/playbook.py` | 2 | pending |
| 1.2 | Parse `review_gates:` in `_load_step`; add `GraphProblem` kinds: legacy scalar `review_gate:` key → blocking STOP (message names the new shape), malformed entry (non-mapping, missing `gate`, unknown `importance`) → blocking `bad_review_gate` STOP; update `test_step_review_gate_and_detached_absent_vs_set` and add loader tests for: valid list, defaulted importance, legacy-scalar STOP, malformed-entry STOP | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] `ReviewGate` validates `importance` via `Literal`; instantiating with an unknown level raises.
- [ ] `Step.review_gates` defaults to `[]`; a step without the key loads with an empty list.
- [ ] `just typecheck` passes.

#### Task 1.2 DoD

- [ ] A step with `review_gates: [{gate: "x"}]` loads with one gate at `medium`.
- [ ] A step with legacy `review_gate: "x"` (or `review_gate: null`) produces a blocking STOP problem naming `review_gates:` as the replacement.
- [ ] A `review_gates:` entry that is not a mapping, lacks `gate`, or carries an unknown `importance` produces a blocking `bad_review_gate` STOP.
- [ ] `uv run --project booping-python pytest tests/context/playbook_test.py -k review_gate` passes.

---

### M2: Render filtering and CLI flag — 5 SP | pending

**Goal**: `render-playbook --review-level` filters gates at the declared threshold; the composed render shows one bullet per surviving gate in today's format.

**Verify**: `uv run --project booping-python pytest tests/test_render_playbook.py` passes; `bin/booping render-playbook groom --review-level autonomous | grep -c 'Review gate'` prints `0`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `--review-level` (`choices=["autonomous","low","medium","high"]`, default `medium`) to `add_parser`; thread the value into `compose()` like `include_lessons` (`compose_step()` untouched) | `booping-python/src/booping/commands/render_playbook.py` | 2 | pending |
| 2.2 | Filter each step's gates in `compose()` before `step_tmpl.render(...)` (importance ≥ level; `autonomous` → none); update `_playbook_step.j2` to render one bullet per surviving gate in today's exact format; update `test_gate_directive_verbatim`, migrate fixture frontmatter to `review_gates:`, add filter tests per level and a multi-gate rendering test, plus CLI-flag tests imitating `test_cli_no_lessons_flag`/`test_cli_help_lists_no_lessons` | `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_playbook_step.j2`, `booping-python/tests/test_render_playbook.py`, `booping-python/tests/__fixtures__/render-playbook-home/_playbooks/composed/*/prompt.md`, `booping-python/tests/__fixtures__/playbooks-home/_playbooks/alpha/*/prompt.md` | 3 | pending |

#### Task 2.1 DoD

- [ ] `bin/booping render-playbook --help` lists `--review-level` with its four choices and default `medium`.
- [ ] An invalid value exits non-zero with an argparse error on stderr.

#### Task 2.2 DoD

- [ ] `--review-level low` renders every declared gate; `medium` drops `low` gates; `high` keeps only `high` gates; `autonomous` renders none.
- [ ] A step with two surviving gates renders two bullets, each in today's format (no importance shown).
- [ ] `--step` output remains gate-chrome-free at every level.
- [ ] All migrated fixtures load without STOP notices; `uv run --project booping-python pytest tests/test_render_playbook.py` passes.

---

### M3: Driver protocol — 2 SP | pending

**Goal**: the driving partial maps the user's prompt prose to the flag once per run and honors every surviving gate bullet.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` renders cleanly and its output states the prose→flag rule and plural gate honoring.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add the render-step rule: judge the user's ask once before rendering — "review each/every step" → `--review-level low`, "only main steps" → `high`, "autonomous / don't stop for reviews" → `autonomous`, nothing stated → omit the flag; pluralize gate honoring ("honor each `Review gate:` bullet"), AskUserQuestion wiring unchanged | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |

#### Task 3.1 DoD

- [ ] The partial names all four flag values and the default-omission rule in one place.
- [ ] Gate-honoring prose covers multiple bullets per step without changing the AskUserQuestion contract.
- [ ] Rendered output of a skill including the partial (`bin/booping render src/templates/skills/playbook.md.j2`) shows the new rule.

---

### M4: Core playbook migration and authoring contract — 4 SP | pending

**Goal**: every core playbook step carries the new shape with judged importance; `playbook-authoring` emits `review_gates:` in the wrappers it generates.

**Verify**: `bin/booping render-playbook groom` and `bin/booping render-playbook playbook-authoring` emit no STOP notices; `grep -rl '^review_gate:' playbooks/` prints nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Migrate step frontmatter: groom — `present` → `high`, `intake` → `medium`, drop the `review_gate: null` keys on the six gateless steps; playbook-authoring — `interview` and `decompose` → `high`; `manifest`, `states`, `step-spec`, `llm-tests`, `step-prompt` → `medium`; `fixtures`, `step-suite`, `smoke-optimizer`, `regress-optimizer` → `low`; `record-decision`'s `"none — mechanical log"` gate dropped entirely | `playbooks/groom/*/prompt.md`, `playbooks/playbook-authoring/*/prompt.md` | 2 | pending |
| 4.2 | Move `playbook-authoring`'s wrapper-generation contract to the new shape: the `step-prompt` step body, its spec, and its eval suite (the `'^review_gate:'` assertion and grader wording) | `playbooks/playbook-authoring/step-prompt/opus-5.md`, `playbooks/playbook-authoring/step-prompt/tests.yaml`, `playbooks/playbook-authoring/_specs/steps/step-prompt/index.md`, `playbooks/playbook-authoring/_specs/steps/step-prompt/test-plan.md` | 2 | pending |

#### Task 4.1 DoD

- [ ] Every migrated gate keeps its gate text verbatim; only the shape and importance change.
- [ ] `bin/booping render-playbook groom` and `bin/booping render-playbook playbook-authoring` emit no STOP or Note notices.
- [ ] `grep -rl '^review_gate:' playbooks/` prints nothing.

#### Task 4.2 DoD

- [ ] The `step-prompt` body and spec describe `review_gates: [{gate, importance}]` as the wrapper shape it writes.
- [ ] `tests.yaml` asserts the new key shape (`'^review_gates:'` or equivalent) and its grader wording matches.
- [ ] No file under `playbooks/playbook-authoring/` still documents the scalar shape.

---

### M5: Documentation — 2 SP | pending

**Goal**: the public docs and the repo guide describe the new shape and flag.

**Verify**: `grep -rn 'review_gate[^s]' documentation/ CLAUDE.md` prints nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite `documentation/playbook.md` frontmatter reference, example block, and the repeat-semantics line for `review_gates:` + document `--review-level`; update the root `CLAUDE.md` Playbooks paragraph (`summary,review_gate` mention, "Gates are rendered from `review_gate` frontmatter") and the `render-playbook` CLI listing | `documentation/playbook.md`, `CLAUDE.md` | 2 | pending |

#### Task 5.1 DoD

- [ ] `documentation/playbook.md` shows a `review_gates:` example with an explicit `importance` and documents all four `--review-level` values and the default.
- [ ] `CLAUDE.md` names the new shape and flag everywhere the old ones appeared; `grep -rn 'review_gate[^s]' documentation/ CLAUDE.md` prints nothing.

---

## I/O contract

- **Arguments / flags**: `booping render-playbook <name> [--step <step>] [--review-level {autonomous,low,medium,high}] [--project <path>] [--output <path>] [--no-lessons]` — `--review-level` sets the gate-render threshold, default `medium`; it affects only the composed render (`--step` output carries no gate chrome at any level).
- **stdin**: none.
- **stdout**: composed markdown; gate bullets appear only for gates at or above the active level, byte-identical in format to today's bullet.
- **stderr**: unknown playbook / argparse errors, as today.
- **Exit codes**: unchanged — `0` on render (STOP/Note notices stay in-band), `1` on unknown playbook, `2` on argparse error (argparse default).

## Final Verification

- [ ] Help text updated and accurate (`--review-level` listed with choices and default).
- [ ] Happy path: `bin/booping render-playbook groom` renders gates at `medium`; failure path: invalid `--review-level` value exits non-zero with stderr message.
- [ ] Exit codes match the documented contract.
- [ ] `bin/booping render src/templates/skills/playbook.md.j2` (consumer skill) renders cleanly.
- [ ] `just lint`, `just typecheck`, `just test` green.

## Out of scope

- State-machine transition `gates:` (in `states:` entries and `plan.statuses` — different object, untouched).
- The legacy `/groom` skill and plan-lifecycle review gates.
- Retro-annotating vault/global playbooks (e.g. `user-stories`) — their scalar keys surface as STOP notices for their owners to migrate.
- The three prior plan artifacts named in the request — unread, unadopted.
- No compatibility shim for the scalar shape; no reshape milestone.

## CLAUDE.md impact

Covered by M5 task 5.1: the Playbooks paragraph (step frontmatter shape, "Gates are rendered from `review_gate` frontmatter") and the `render-playbook` entry in the `## CLI` section gain `review_gates:` + `--review-level`.
