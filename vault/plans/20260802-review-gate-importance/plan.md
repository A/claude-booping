---
title: Playbook review gate importance level
type: feature
status: awaiting-plan-review
sp: 18
split_from: null
created: 2026-08-02
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Playbook review gates carry high/medium/low importance; a render-time level
  filters which gates pause the run"
commit: null
sessions:
- e32af68a-a303-4265-a4c0-a03dac92c829
active_minutes: 501
models:
- claude-fable-5
---

# Playbook review gate importance level

## Context

Playbook steps declare a review gate as single-string `review_gate:` frontmatter on `prompt.md`; `booping render-playbook` renders every declared gate as a `Review gate:` bullet, and the driver pauses on each one identically. There is no way to rank gates or dial review intensity per run. After this plan: steps declare `review_gates:` — a list of `{gate, importance}` items (`high|medium|low`, default `medium`) — and `render-playbook` takes `--review-level {low,medium,high,autonomous}` (default `medium`); gates below the level are absent from the composed render, so the driver never pauses on them. Legacy `review_gate:` strings keep loading as a single `medium` gate with a deprecation line in `.booping.log`. The driver protocol maps user prose to a level and persists it on stateful runs.

## Decisions

- **Frontmatter shape**: `review_gates:` list of `{gate: <prose>, importance: high|medium|low}`, `importance` optional defaulting to `medium` — user-chosen over a sibling scalar key; supports several gates per step.
- **Level vocabulary = importance names**: `--review-level` takes the minimum surviving importance (`low` → all, `medium` → medium+high, `high` → high only) plus `autonomous` (none) — one vocabulary for gate attribute and run threshold, no mode-name synonyms.
- **Filtering in `compose()`, before Jinja**: each step's `review_gates` list is filtered in Python inside `compose()` via the pure `gate_survives(importance, level)` resolver; only surviving gates enter the template context. The template holds no filtering logic and the resolver is not a Jinja global — user's call.
- **Filtering at render time**: a filtered gate leaves no trace in the output (no bullet, no marker) — user-confirmed; the driver honors only what renders.
- **Legacy `review_gate:` accepted silently**: loads as one `medium` gate, appends a deprecation line to the vault `_booping/.booping.log`; both keys present → `review_gates:` wins, same log line. No STOP, no Note — user's call to keep personal/global playbooks working.
- **Persistence via the driver-written channel**: the chosen level is written to the run artifact as `review_level:` frontmatter by `booping frontmatter-update` (same non-hook channel as the `agents:` mapping); `playbook-state`/`playbook-transition` unchanged.
- **Malformed `review_gates:` entry is blocking**: new `GraphProblem` kind `malformed_review_gate` rendered as an in-band STOP notice, following the existing shape-problem dispatch.

## Architecture

`booping-python/src/booping/context/playbook.py` owns the schema: a `ReviewGate` model on `Step`, parsed in `_load_step`, plus a pure `gate_survives(importance, level)` resolver beside `resolve_detached` (not a Jinja global). `booping-python/src/booping/commands/render_playbook.py` owns the flag and the filtering: `--review-level` registered in `add_parser`, threaded through `compose()`/`_run()` exactly like `include_lessons`, and applied inside `compose()` — each step's gate list is filtered through `gate_survives` before the template context is built. `src/templates/_partials/_playbook_step.j2` is the single point rendering gate chrome for plain and subgraph-inner sections; it emits one bullet per gate in the pre-filtered list it receives, with no filtering logic of its own. `src/templates/_partials/_playbook_driving.j2` binds the drivers (`/playbook`, `/groom-playbook` — both consume the partial live, no rebuild): level inference from user prose, `--review-level` on every render call, persistence and resume. Callers of the rendered output are the driver skills; the output stays plain markdown on stdout.

## Milestones

### M1: Schema, legacy path, resolver — 6 SP | pending

**Goal**: playbook loading understands `review_gates:` (validated, defaulted), accepts legacy `review_gate:` with a logged deprecation, and exposes `gate_survives`.

**Verify**: `just test` green in `booping-python/`; `uv run --project booping-python booping render-playbook groom >/dev/null && grep "deprecated review_gate" ~/Claude/claude-booping/_booping/.booping.log` (against a fixture playbook carrying the legacy key).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `ReviewGate` model (`gate: str`, `importance: Literal["high","medium","low"]`) and **replace** `Step.review_gate: str \| None` with `Step.review_gates: list[ReviewGate]`; parse `review_gates:` in `_load_step` with `importance` defaulting to `medium`; a non-mapping item, missing/empty `gate`, or unknown `importance` value emits new blocking `GraphProblem` kind `malformed_review_gate` (add to the `kind` Literal); mechanically update every `step.review_gate` read (`_playbook_step.j2`, any test referencing the field) to the list field so the suite is green at end of M1 — bullet format itself unchanged until M2 | `booping-python/src/booping/context/playbook.py`, `src/templates/_partials/_playbook_step.j2`, `booping-python/tests/context/playbook_test.py`, `booping-python/tests/test_render_playbook.py` | 3 | pending |
| 1.2 | Accept legacy `review_gate: <string>` as `[{gate: <string>, importance: medium}]`; when both keys present, `review_gates:` wins; each legacy load appends `<iso8601-utc>: [render-playbook] deprecated review_gate: <playbook>/<step> — rename to review_gates` to the vault `_booping/.booping.log` via the existing log helper | `booping-python/src/booping/context/playbook.py` | 2 | pending |
| 1.3 | Add pure resolver `gate_survives(importance, level)` (`low` keeps all; `medium` keeps medium+high; `high` keeps high; `autonomous` keeps none) next to `resolve_detached` — plain function only, not registered as a Jinja global | `booping-python/src/booping/context/playbook.py` | 1 | pending |

#### Task 1.1 DoD

- [ ] A step with `review_gates: [{gate: "...", importance: high}, {gate: "..."}]` loads with two gates, the second `medium`.
- [ ] A step with `review_gates: [{importance: high}]` (no `gate`) produces a `malformed_review_gate` problem and renders as an in-band STOP notice.
- [ ] `review_gates: "text"` (non-list) and `review_gates: [{gate: "x", importance: urgent}]` each produce `malformed_review_gate`.
- [ ] Tests in `booping-python/tests/context/playbook_test.py` cover the three cases above and pass.
- [ ] Full suite green at end of M1 — no `step.review_gate` reference survives outside the legacy parse path.

#### Task 1.2 DoD

- [ ] A step with only `review_gate: "text"` loads as one gate `{gate: "text", importance: medium}` and no problem.
- [ ] `review_gate: ""` and `review_gate: null` both load as no gates and emit no log line (same as key absent).
- [ ] The `.booping.log` line appears exactly once per legacy step per load, in the stated format.
- [ ] A step with both keys loads `review_gates:` and still logs the deprecation line.
- [ ] Tests cover legacy-only, both-keys, and log-line emission; `just test` passes.

#### Task 1.3 DoD

- [ ] `gate_survives` returns the documented keep/drop for all 4 levels × 3 importances (12-case table test).
- [ ] The resolver is importable from `booping.context.playbook` and appears in no Jinja `globals_` registration.

---

### M2: Render-time filtering — 7 SP | pending

**Goal**: `booping render-playbook <name> --review-level <level>` omits filtered gates from the composed render; surviving gates render one bullet each with their importance.

**Verify**: `uv run --project booping-python booping render-playbook groom --review-level autonomous | grep -c "Review gate"` prints `0`; `--review-level low` prints one `Review gate (` bullet per declared gate; `just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Register `--review-level {low,medium,high,autonomous}` (default `medium`) in `add_parser`; thread a `review_level` param through `compose()` and `_run()` following the `include_lessons` pattern, and apply the filtering inside `compose()`: build each step's template context with its `review_gates` filtered through `gate_survives(importance, review_level)` — no unfiltered gate list reaches Jinja (`--step` output unaffected — it carries no gate chrome) | `booping-python/src/booping/commands/render_playbook.py` | 2 | pending |
| 2.2 | Render gates in the step partial from the pre-filtered list only: one `Review gate (<importance>):` bullet per gate handed in; empty list → no gate bullet at all; no filtering logic in the template; identical treatment in the plain and subgraph-inner branches; sync the `Review gate:` wording in `_playbook_driving.j2` protocol step 5 (and its subgraph gate line) to the new bullet shape so drivers keep parsing correctly | `src/templates/_partials/_playbook_step.j2`, `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 2.3 | Render tests: filtering matrix across the four levels, gate prose rendered verbatim (extend `test_gate_directive_verbatim`), subgraph-inner parity, multi-gate step ordering, `malformed_review_gate` STOP notice text; fixtures: retrofit `render-playbook-home/_playbooks/composed/{gather,draft}` to `review_gates:` with mixed importances (one multi-gate step), keep `playbooks-home/_playbooks/alpha/gather` on the legacy key as the deliberate legacy-path fixture | `booping-python/tests/test_render_playbook.py`, `booping-python/tests/__fixtures__/render-playbook-home/_playbooks/composed/*/prompt.md`, `booping-python/tests/__fixtures__/playbooks-home/_playbooks/alpha/*/prompt.md` | 3 | pending |

#### Task 2.1 DoD

- [ ] `booping render-playbook <name> --help` documents the flag and its default.
- [ ] An invalid value (`--review-level none`) exits non-zero with an argparse error on stderr.
- [ ] Omitting the flag renders identically to `--review-level medium`.

#### Task 2.2 DoD

- [ ] A `high` gate renders under `--review-level high`; a `medium` gate does not; output diff confirms no residual marker for the dropped gate.
- [ ] A step whose every gate is filtered renders byte-identically to the same step with no gates declared.
- [ ] Subgraph-inner step sections filter identically to plain ones.
- [ ] `_playbook_driving.j2` gate-enforcement wording matches the rendered bullet shape (no reference to the old single-gate format).
- [ ] `grep gate_survives src/templates/` returns no hits — the template carries no filtering logic.

#### Task 2.3 DoD

- [ ] Filtering matrix test asserts presence/absence per level for fixture gates at all three importances.
- [ ] Legacy-key fixture renders as a `medium` gate through the same matrix.
- [ ] `just test`, `just lint`, `just typecheck` pass.

---

### M3: Driver protocol, migration, docs — 5 SP | pending

**Goal**: drivers infer the review level from user prose, pass it on every render call, persist it on stateful runs; committed playbooks and docs speak `review_gates:`.

**Verify**: `bin/booping render src/templates/_partials/_playbook_driving.j2` renders without error and contains the level-inference table, the `--review-level` render instruction, and the `frontmatter-update ... review_level=` persistence call; `grep -rn "review_gate:" playbooks/ booping-python/tests/__fixtures__/ documentation/ CLAUDE.md` returns only intentional legacy-path fixtures.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Update the driving protocol: the driver infers the level from the user's run-request prose ("review each step" → `low`; no signal → `medium`; "only main steps" → `high`; explicit autonomy → `autonomous`), announces it at run start, passes `--review-level <level>` on every `render-playbook` call, and on stateful runs persists it itself — `booping frontmatter-update <workdir>/<outer-machine artifact per the ## State section> review_level=<level>` right after workdir creation (driver-written channel like the `agents:` mapping; no booping-infra change) — reusing the persisted value on resume with explicit new prose winning and re-persisted; state that `autonomous` never bypasses state-machine gates | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 3.2 | Migrate committed gate frontmatter to `review_gates:` (2 gates in `playbooks/groom/`, 12 in `playbooks/playbook-authoring/`) grading importance as: `high` = user approval/scope-settling gates (e.g. groom's present/intake), `medium` = artifact-confirmation gates, `low` = informational check-ins; and update `playbook-authoring`'s `step-prompt` prompt text (+ its `_specs/steps/step-prompt/` index and test-plan) so newly authored playbooks emit the new shape | `playbooks/groom/*/prompt.md`, `playbooks/playbook-authoring/*/prompt.md`, `playbooks/playbook-authoring/step-prompt/prompt.md`, `playbooks/playbook-authoring/_specs/steps/step-prompt/index.md`, `playbooks/playbook-authoring/_specs/steps/step-prompt/test-plan.md` | 2 | pending |
| 3.3 | Docs refresh: `documentation/playbook.md` frontmatter table + YAML example + gate bullets + repeat-semantics prose; repo `CLAUDE.md` Playbooks bullet (frontmatter shape, gate rendering sentence) and the `render-playbook` CLI bullet (new flag) | `documentation/playbook.md`, `CLAUDE.md` | 1 | pending |

#### Task 3.1 DoD

- [ ] Rendered partial carries the four prose→level mappings, the persistence invocation, the resume rule, and the autonomous/state-gate boundary sentence.
- [ ] `/playbook` and `/groom-playbook` skill renders (`bin/booping render src/templates/skills/playbook.md.j2`) include the updated protocol with no Jinja errors.

#### Task 3.2 DoD

- [ ] `grep -rn "review_gate:" playbooks/` returns no hits.
- [ ] `booping render-playbook groom` and `booping render-playbook playbook-authoring` render with zero deprecation lines appended to `.booping.log`.
- [ ] Every migrated gate keeps its prose byte-identical; importance values recorded in the diff.

#### Task 3.3 DoD

- [ ] `documentation/playbook.md` shows the `review_gates:` list shape, the legacy note, and the `--review-level` flag.
- [ ] `CLAUDE.md` Playbooks bullet and CLI bullet mention `review_gates` and `--review-level`; no stale `review_gate` single-key claim remains outside the legacy-compat note.

---

## I/O contract

- **Arguments / flags**: `booping render-playbook <name> [--step <step>] [--project <path>] [--output <path>] [--no-lessons] [--review-level {low,medium,high,autonomous}]` — `--review-level` sets the minimum gate importance that renders; default `medium`; `autonomous` renders no gates; no effect on `--step` output.
- **stdin**: not read.
- **stdout**: composed procedure as plain markdown (unchanged shape); surviving gates as `Review gate (<importance>):` bullets.
- **stderr**: unknown playbook/step diagnostics (unchanged); argparse error for an invalid `--review-level` value.
- **Exit codes**: `0` on success including in-band STOP notices (`malformed_review_gate` follows the existing graph-problem convention), `2` argparse usage error, `1` unknown playbook/step (unchanged).

## Final Verification

- [ ] `booping render-playbook --help` reflects `--review-level` accurately.
- [ ] Happy path: `--review-level high` on a mixed-importance fixture renders only high gates; failure path: invalid level value exits non-zero with stderr message.
- [ ] Exit codes match the contract above.
- [ ] `/playbook` and `/groom-playbook` skills render cleanly with the updated driving partial (`bin/booping render src/templates/skills/playbook.md.j2`, `.../groom-playbook.md.j2`).
- [ ] `just lint`, `just typecheck`, `just test` all green.

## Out of scope

- Changing what a surviving gate does when it fires (presentation + explicit confirmation unchanged).
- Plan-lifecycle gates (`plan.statuses.*.transitions[].gates` in `src/config.yaml`).
- State-machine `gates` on `playbook-transition` edges.
- Authoring-time tooling beyond the mechanical `step-prompt` shape update.
- Per-gate run-time overrides — the level is run-wide.
- Removing the legacy `review_gate:` path (future major).

## CLAUDE.md impact

Update the Playbooks bullet (frontmatter shape `summary,review_gates`, gate-rendering sentence, legacy-compat note) and the `render-playbook` CLI bullet (`--review-level` flag) — covered by Task 3.3.
