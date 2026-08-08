---
title: Playbook Review-Gate Importance Levels
type: feature
status: cancelled
sp: 20
split_from: null
created: 2026-08-02 03:22
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Step review gates gain high|medium|low importance; driver + render-playbook
  filter gates by user-chosen review depth"
sessions:
- 4c669e7b-45f2-4611-9d8c-1e639576d8f1
metrics_active_minutes: 5
metrics_models:
- claude-fable-5
metrics_tokens_input: 38
metrics_tokens_output: 47621
metrics_tokens_cache_creation: 186226
metrics_tokens_cache_read: 1322033
---

# Playbook Review-Gate Importance Levels

## Context

Playbook steps declare review gates via `review_gate: "<prose>"` frontmatter — a single unstructured string, all-or-nothing. Every gate always pauses the run; a user who wants to review "only main steps" or "every step" has no lever.

After this ships: each gate carries an importance (`high|medium|low`, default `medium`). The driver reads the user's prose at run start — "review each step" → `low` (all gates), default → `medium` (medium+high), "only main steps" → `high` (high only) — and passes `--gate-level` to `render-playbook`, which drops gate bullets below the threshold. Enforcement stays mechanical: the driver pauses only where a bullet rendered.

## Decisions

- **Frontmatter shape**: new canonical field `review_gates:` — a list of `{gate: <prose>, importance: high|medium|low}` items; `importance` omitted → `medium`. A step may carry multiple gates. (User-chosen over structured single mapping.)
- **Legacy compat**: `review_gate: "<str>"` keeps loading — adapted to one gate at `medium` — and `render-playbook` appends a deprecation line to `.booping.log`. Both keys on one step → blocking STOP (precedent: `graph:` in both manifests).
- **Validation**: invalid `importance` value, non-list `review_gates`, or malformed item (missing/empty `gate`, unknown key) → blocking STOP via a new `bad_review_gate` `GraphProblem` kind. No silent fallback — a bad value silently weakening gating is worse than a hard stop.
- **Filtering locus**: render-time `--gate-level` flag, not driver judgment per gate. Driver picks the level once from user prose; rendered output is the contract.
- **`--step` output**: unaffected — step-body output carries no gate chrome today and gains none.
- **State-machine `gates`** (transition preconditions in `states:`): out of scope — different vocabulary.

## Architecture

- **Model** (`booping-python/src/booping/context/playbook.py`): new `ReviewGate` model (`gate: str`, `importance: Literal["high","medium","low"] = "medium"`); `Step.review_gates: list[ReviewGate]` replaces `Step.review_gate: str | None`. `_load_step` parses the list, adapts the legacy key, records a per-step deprecation marker, and appends `bad_review_gate` problems.
- **Render** (`src/templates/_partials/_playbook_step.j2` + `booping-python/src/booping/commands/render_playbook.py`): one bullet per gate at-or-above threshold, tagged `(importance)`; `--gate-level` argparse option threaded into `compose()`; deprecation markers logged to `.booping.log` at render time.
- **Driver** (`src/templates/_partials/_playbook_driving.j2`): level-selection prose + flag pass-through. Live template — no rebuild.
- **Consumers**: `/playbook` and `/groom-playbook` skills drive via `_playbook_driving.j2`; no skill-body change needed. Core playbooks (`playbooks/groom/`, `playbooks/playbook-authoring/`) migrate to the new shape in-sprint.

## Milestones

### M1: Model + parsing + validation — 7 SP | pending

**Goal**: `Playbook.load_all` parses `review_gates` lists (with legacy adaptation and STOP problems); `render-playbook` logs deprecations.

**Verify**: `cd booping-python && uv run pytest tests/context/playbook_test.py -q` green; `bin/booping render-playbook groom --project <fixture>` on a fixture with a legacy `review_gate` appends a `deprecated review_gate` line to the fixture vault's `_booping/.booping.log`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `ReviewGate` model; `Step.review_gates: list[ReviewGate]`; `_load_step` parses list shape, defaults `importance` to `medium`, adapts legacy `review_gate` string to a one-item medium list and marks the step deprecated | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | pending |
| 1.2 | `bad_review_gate` `GraphProblem` kind (blocking STOP): invalid importance, non-list value, malformed item, both `review_gate` + `review_gates` present. STOP template constant + `_shape_notice` branch | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/` | 2 | pending |
| 1.3 | Deprecation logging: `render-playbook` (composed and `--step`) writes one `.booping.log` line per deprecated step: `<iso8601-utc>: [render-playbook] deprecated review_gate in <playbook>/<step> — use review_gates` | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/` | 2 | pending |

#### Task 1.1 DoD

- [ ] `review_gates` list with mixed explicit/omitted `importance` parses; omitted → `medium`.
- [ ] Legacy `review_gate: "<str>"` loads as `[ReviewGate(gate=<str>, importance="medium")]` and the step is marked deprecated.
- [ ] `review_gate: null` / absent both fields → empty `review_gates`.
- [ ] Existing `test_step_review_gate_and_detached_absent_vs_set` updated to the new field; suite green.

#### Task 1.2 DoD

- [ ] `importance: critical` → blocking STOP naming step + offending value + `expected high|medium|low`.
- [ ] `review_gates: "oops"` (non-list) and item without `gate` → blocking STOP.
- [ ] Step with both `review_gate` and `review_gates` → blocking STOP.
- [ ] STOP renders in-band (exit 0), output reduced to notices + preamble per existing blocking behavior.

#### Task 1.3 DoD

- [ ] Log line format matches spec exactly; one line per deprecated step per invocation.
- [ ] No deprecation in the loaded playbook → no log line.
- [ ] Diagnostics stay off stdout (composed output byte-stable aside from gate bullets).

---

### M2: Render + `--gate-level` flag — 5 SP | pending

**Goal**: gate bullets render per-gate with importance tag; `--gate-level` filters them.

**Verify**: `bin/booping render-playbook groom --project <fixture> --gate-level high` shows only high bullets; without the flag shows all; `--gate-level silly` exits 1 with stderr usage error. `uv run pytest booping-python/tests -q` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `_playbook_step.j2`: replace single gate bullet with a loop — exact bullet: `- Review gate (<importance>): stop after this step — "<gate prose>"; continue only on explicit user confirmation.` | `src/templates/_partials/_playbook_step.j2` | 2 | pending |
| 2.2 | `--gate-level {high,medium,low}` argparse option (choices-validated, exit 1 + stderr on bad value); threshold threading into `compose()` so below-threshold gates are dropped before template render; no flag → all gates. Rendering tests | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/` | 3 | pending |

#### Task 2.1 DoD

- [ ] Multi-gate step renders one bullet per gate, in list order, each tagged `(high)`/`(medium)`/`(low)`.
- [ ] Zero-gate step renders no gate bullet (and drops out of the "any instructions" check when nothing else applies).

#### Task 2.2 DoD

- [ ] `--gate-level low` → all gates; `medium` → medium+high; `high` → high only.
- [ ] Flag absent → identical to `--gate-level low` output (all gates shown).
- [ ] Invalid value rejected by argparse: exit ≠ 0, stderr message, nothing on stdout.
- [ ] `--help` documents the flag and its threshold semantics.

---

### M3: Driver prose + core playbook migration — 6 SP | pending

**Goal**: driver selects the level from user prose and passes the flag; both core playbooks use `review_gates` (no deprecation lines on their render).

**Verify**: `bin/booping render-playbook groom` and `... playbook-authoring` render clean (no STOP, no deprecation log lines); `grep -r "review_gate:" playbooks/` → no hits outside `_lib`/fixtures; playbook eval harness suites for touched steps pass.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `_playbook_driving.j2`: on run start derive gate level from the user's request prose — "review each step"-intent → `low`, "only main steps"-intent → `high`, otherwise `medium` — and append `--gate-level <level>` to every `render-playbook` invocation the protocol issues | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 3.2 | Migrate all 13 gated step `prompt.md` files to `review_gates` lists with importance per the table below (sentinel prose kept, importance `low`) | `playbooks/groom/{intake,present}/prompt.md`, `playbooks/playbook-authoring/*/prompt.md` | 2 | pending |
| 3.3 | Stale-teaching cleanup: `playbook-authoring` step bodies that teach the wrapper frontmatter shape (`step-spec`, `step-prompt`) now teach `review_gates`; eval assert `^review_gate:` → `^review_gates:` and grader wording in `step-prompt/tests.yaml` | `playbooks/playbook-authoring/step-spec/prompt.md`, `playbooks/playbook-authoring/step-prompt/prompt.md`, `playbooks/playbook-authoring/step-prompt/tests.yaml` | 2 | pending |

Importance assignment (3.2; adjust only if a gate's prose plainly contradicts it):

| Playbook | Step | Importance |
|----------|------|------------|
| groom | intake | medium |
| groom | present | high |
| playbook-authoring | interview | high |
| playbook-authoring | decompose | high |
| playbook-authoring | states | medium |
| playbook-authoring | manifest | medium |
| playbook-authoring | step-spec | medium |
| playbook-authoring | step-prompt | medium |
| playbook-authoring | fixtures | medium |
| playbook-authoring | llm-tests | medium |
| playbook-authoring | step-suite | medium |
| playbook-authoring | smoke-optimizer | low |
| playbook-authoring | regress-optimizer | low |
| playbook-authoring | record-decision | low |

#### Task 3.1 DoD

- [ ] Driving partial names the three prose→level mappings and the default explicitly.
- [ ] Every `render-playbook` invocation in the protocol carries the flag; `--step` fetches do not (no gate chrome there).
- [ ] Level chosen once per run, not re-judged per wave.

#### Task 3.2 DoD

- [ ] All 13 files use `review_gates:`; zero legacy `review_gate:` keys remain under `playbooks/` step dirs.
- [ ] `render-playbook` on both core playbooks: no STOP notices, no new deprecation log lines.
- [ ] Sentinel steps (`record-decision`, `smoke-optimizer`, `regress-optimizer`) keep their prose, importance `low`.

#### Task 3.3 DoD

- [ ] `step-spec` / `step-prompt` bodies show the list shape with an `importance` example.
- [ ] `step-prompt/tests.yaml` regex + grader value updated; suite passes via the eval harness.
- [ ] No other `playbooks/` prose still teaches the singular shape (`grep -ri "review_gate[^s]" playbooks/ --include='*.md'` clean).

---

### M4: Docs — 2 SP | pending

**Goal**: public docs and CLAUDE.md describe the new shape and flag.

**Verify**: `grep -n "review_gates" documentation/playbook.md CLAUDE.md` shows updated sections; `grep -n "review_gate[^s]" documentation/ CLAUDE.md` shows only the legacy-compat note.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `documentation/playbook.md`: field table + yaml example + per-instance gate prose updated to `review_gates` (+ legacy-compat and `--gate-level` docs). `CLAUDE.md` playbook paragraph: frontmatter list (`summary,review_gates`), gate rendering sentence, `render-playbook` synopsis gains `--gate-level` | `documentation/playbook.md`, `CLAUDE.md` | 2 | pending |

#### Task 4.1 DoD

- [ ] `documentation/playbook.md` documents: list shape, default `medium`, legacy string compat + deprecation log, `--gate-level` threshold semantics, driver prose→level mapping.
- [ ] CLAUDE.md paragraph and CLI section reflect the same — no stale `review_gate` singular except the compat note.
- [ ] Audience check (lesson 0006): `documentation/` covers user-facing behavior only; internal model/dataclass detail stays out.

---

## I/O contract

- **Arguments / flags**: `booping render-playbook <name> [--step <step>] [--project <path>] [--output <path>] [--no-lessons] [--gate-level {high,medium,low}]` — `--gate-level` = minimum importance rendered; absent → all gates.
- **stdout**: composed markdown; gate bullets exactly `- Review gate (<importance>): stop after this step — "<gate prose>"; continue only on explicit user confirmation.`
- **stderr**: argparse usage error on invalid `--gate-level`; existing diagnostics unchanged.
- **`.booping.log`**: `<iso8601-utc>: [render-playbook] deprecated review_gate in <playbook>/<step> — use review_gates` per deprecated step per invocation.
- **Exit codes**: unchanged — 0 incl. in-band STOP notices; 1 unknown playbook/step or bad flag value.

## Final Verification

- [ ] `just lint`, `just typecheck`, `just test` green.
- [ ] `bin/booping render-playbook groom` / `playbook-authoring` clean; `--gate-level high` on groom leaves only the `present` gate bullet.
- [ ] `--help` shows `--gate-level`.
- [ ] Failure paths: invalid flag value (exit ≠ 0), invalid `importance` frontmatter (in-band STOP).

## Out of scope

- State-machine transition `gates` (in `states:` / `plan.statuses`) — different vocabulary, untouched.
- Converting sentinel "none — …" gates to `null` (user deselected).
- Per-gate driver judgment beyond the single run-level threshold; no persistence of the chosen level.
- Gate chrome in `--step` output.

## CLAUDE.md impact

Covered by Task 4.1: playbook paragraph (frontmatter fields, gate rendering, driver flag pass-through) + `render-playbook` synopsis in `## CLI`.

---

# Quality Checklist

## Frontmatter

- [x] Frontmatter matches plan frontmatter template.
- [x] `sp` equals the sum of per-task SP across milestones (3+2+2 + 2+3 + 2+2+2 + 2 = 20).

## Content

- [x] Context names the user-visible CLI behavior change.
- [x] DoD bullets are verifiable by invocation + output diff.
- [x] Every task lists exact files.
- [x] Every task DoD uses checkboxes, not prose.
- [x] Every milestone has a `Verify` invocation.
- [x] Each milestone executable from a fresh session with only the plan as context.

## I/O contract

- [x] Argument / flag shape is enumerated.
- [x] Output format for stdout is specified.
- [x] Exit codes are defined for every failure mode the CLI distinguishes.

## Anti-patterns (must be absent)

- [x] No "TBD", "TODO", "implement later".
- [x] No task spanning unrelated concerns.
- [x] No "add a command for X" without argument shape + output.
- [x] No silent failures.
- [x] No stdout/stderr duplication.

## External references validated

- [x] No new dependencies; no external commands added.

## CLAUDE.md impact

- [x] Covered by Task 4.1.
