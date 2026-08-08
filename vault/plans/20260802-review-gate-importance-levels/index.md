---
title: Playbook Review-Gate Importance Levels
type: feature
status: cancelled
sp: 17
split_from: null
created: 2026-08-02 11:41
planned: 20260802 04:41
started: null
completed: null
retro: null
goal: null
summary: Per-gate importance (high|medium|low) on playbook review gates, 
  threshold-filtered at render via --review-gates
commit: 446a48165350c185fdba4611be6630b864308e41
sessions:
- 7efa4155-e786-4367-ad0d-066419a2d5c1
metrics_active_minutes: 6
metrics_models:
- claude-fable-5
metrics_tokens_input: 84
metrics_tokens_output: 66451
metrics_tokens_cache_creation: 386190
metrics_tokens_cache_read: 4101141
---

# Playbook Review-Gate Importance Levels

## Context

`booping render-playbook` composes a playbook's procedure; each step may carry one `review_gate: <string>` frontmatter key, rendered as a `Review gate:` bullet that the driver (`_playbook_driving.j2`) enforces after the step — always, with no way to tune review pressure per run.

After this ships:

- A step declares gates as a list — `review_gates: [{gate: <text>, importance: high|medium|low}]`, `importance` optional (default `medium`). Multiple gates per step allowed.
- `render-playbook` filters gates by a threshold flag `--review-gates low|medium|high|none` (default `medium`). A filtered-out gate is absent from the render — the driver never stops there. `none` = fully autonomous run.
- The driver derives the threshold from the user's prose: "review every step" → `low`, "only main steps" → `high`, "autonomous / don't ask" → `none`, nothing said → omit flag (medium).
- Legacy singular `review_gate:` key → blocking STOP (same pattern as the `agent:` → `detached:` rename).
- Core playbooks (groom, playbook-authoring) migrated to the new shape; structural gates tagged `high`.

## Decisions

- **Frontmatter shape**: `review_gates:` list of `{gate, importance}` mappings — user-chosen; supports several gates per step; `importance` omitted → `medium`.
- **Flag semantics**: threshold, not mode words — `--review-gates <level>` keeps gates with importance ≥ level; `none` drops all. One vocabulary shared between frontmatter and flag.
- **Filtered gate fate**: dropped from render entirely — no non-stopping residue; matches "leaves only high ones".
- **Legacy key**: blocking STOP, no dual parse path — core playbooks migrated in this sprint; vault playbooks get an explicit rename instruction in the STOP text.
- **Malformed entry**: not-a-list, item not a mapping, missing `gate`, or importance outside {high, medium, low} → blocking STOP (consistent with existing malformed-node handling).
- **High-tag set**: groom `present`; playbook-authoring `manifest`, `decompose`. Rest implicit medium.
- **`--step` surface**: unchanged — gates render only in composed sections, never in step bodies.
- **Parse before pydantic**: `_load_step` validates the raw frontmatter value by hand (shape checks on the dict/list) and only then constructs `ReviewGate` — a malformed entry becomes a `GraphProblem`, never a pydantic `ValidationError`. Legacy detection is a plain `"review_gate" in fm` check on the raw dict, same as the existing `"agent" in fm` check.
- **Problem aggregation**: gate problems follow the existing `compose()` convention — every problem is collected and every notice emitted (no fail-fast); any blocking one suppresses graph + step sections.

## Architecture

- `booping-python/src/booping/context/playbook.py` — `ReviewGate` pydantic model (`gate: str`, `importance: Literal["high","medium","low"] = "medium"`); `Step.review_gates: list[ReviewGate]`; `_load_step` parses the list and reports two new `GraphProblem` kinds: `legacy_review_gate_key`, `bad_review_gate`.
- `booping-python/src/booping/commands/render_playbook.py` — `--review-gates` argparse choice (`low|medium|high|none`, default `medium`); `compose()` filters each step's gates by rank (low=0 < medium=1 < high=2; `none` → drop all) and passes the surviving list to the step template; two new STOP message templates.
- `src/templates/_partials/_playbook_step.j2` — receives `gates` (filtered list); renders one bullet per gate: `Review gate (<importance>): stop after this step — "<text>"; continue only on explicit user confirmation.`
- `src/templates/_partials/_playbook_driving.j2` — prose rule mapping user ask → flag value at render time; wave-protocol step 5 pluralized to honor each gate bullet. Live template, no rebuild.
- Consumers: `/playbook` and `/groom-playbook` drive via `_playbook_driving.j2` — no skill-body changes needed.

## Milestones

### M1: Loader — `review_gates` schema — 5 SP | pending

**Goal**: `Step` carries a parsed `review_gates` list with importance defaults; legacy/malformed shapes surface as graph problems.

**Verify**: `just test` green; `uv run --project booping-python pytest tests/context/playbook_test.py -q` covers new cases.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `ReviewGate` model; `Step.review_gate` → `Step.review_gates: list[ReviewGate]`; `_load_step` hand-validates the raw `fm.get("review_gates")` value (list of mappings, `gate` present, importance in the literal set) before constructing any `ReviewGate` — malformed shapes yield `GraphProblem` kind `bad_review_gate` with `detail`, never a pydantic `ValidationError`; legacy singular key detected via `"review_gate" in fm` on the raw dict (pattern of the existing `"agent" in fm` check) → kind `legacy_review_gate_key` | `booping-python/src/booping/context/playbook.py` | 3 | pending |
| 1.2 | Loader tests: list parse, importance default, multi-gate step, legacy-key problem, each malformed shape; migrate alpha fixtures to new key | `booping-python/tests/context/playbook_test.py`, `booping-python/tests/__fixtures__/playbooks-home/_playbooks/alpha/gather/prompt.md`, `.../alpha/draft/prompt.md` | 2 | pending |

#### Task 1.1 DoD

- [ ] `review_gates: [{gate: "x"}]` parses with `importance == "medium"`.
- [ ] `review_gate: "x"` (singular) yields `legacy_review_gate_key` problem naming the step.
- [ ] `review_gates: {gate: x}` (non-list), item without `gate`, and `importance: critical` each yield `bad_review_gate` with a distinct `detail`.
- [ ] Key absent → `review_gates == []`, no problem.

#### Task 1.2 DoD

- [ ] All new parse branches covered by a test each.
- [ ] Alpha fixtures use `review_gates:` list form; suite green.

---

### M2: Render — threshold flag + gate bullets — 5 SP | pending

**Goal**: `render-playbook --review-gates <level>` filters gate bullets by importance; default medium; STOP notices for legacy/malformed gates.

**Verify**: `uv run --project booping-python pytest tests/test_render_playbook.py -q`; manual: `bin/booping render-playbook groom --review-gates high | grep "Review gate"` shows only the `present` gate.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `--review-gates {low,medium,high,none}` (default `medium`) on the parser; `compose()` rank-filter, threading the surviving list into `render_step`; two new module-level string constants beside `_LEGACY_AGENT_KEY` — `_LEGACY_REVIEW_GATE_KEY` ("...key was replaced by the `review_gates:` list...") and `_BAD_REVIEW_GATE` — each a new `elif` branch in `_shape_notice`; problems aggregate per the existing notices loop (no fail-fast) | `booping-python/src/booping/commands/render_playbook.py` | 3 | pending |
| 2.2 | `_playbook_step.j2`: `gates` param, one `Review gate (<importance>):` bullet per gate; instructions-block condition swapped to `gates`; render tests for each threshold incl. `none` and multi-gate steps; migrate composed fixtures | `src/templates/_partials/_playbook_step.j2`, `booping-python/tests/test_render_playbook.py`, `booping-python/tests/__fixtures__/render-playbook-home/_playbooks/composed/{plain,gather,named-step,draft}/prompt.md` | 2 | pending |

#### Task 2.1 DoD

- [ ] `--review-gates` accepts exactly the four values; anything else → argparse error, exit ≠ 0.
- [ ] Default run == `--review-gates medium` byte-for-byte.
- [ ] `none` renders zero `Review gate` bullets; step sections otherwise intact.
- [ ] Legacy key and each malformed shape render blocking STOP (graph + step sections omitted).

#### Task 2.2 DoD

- [ ] A step with `[{gate: a, importance: high}, {gate: b}]` renders two bullets at `low`, two at `medium`, one at `high`.
- [ ] Bullet format: `Review gate (high): stop after this step — "a"; continue only on explicit user confirmation.`
- [ ] `--step` output unchanged by any flag value.

---

### M3: Driver prose + core playbook migration — 4 SP | pending

**Goal**: the driver picks the threshold from the user's ask; core playbooks carry the new schema with high tags.

**Verify**: `bin/booping render-playbook groom | grep -c "Review gate"` → 2; `--review-gates high` → 1 (present); `--review-gates none` → 0; `grep -rn "review_gate:" playbooks/` → empty.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `_playbook_driving.j2`: render bullet gains the ask→level mapping (each step → `low`; main steps → `high`; autonomous → `none`; unstated → omit flag); step 5 wording covers multiple `Review gate` bullets per member | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 3.2 | Migrate core playbooks: string gates → `review_gates:` list form; `review_gate: null` → key dropped; tag `high` on groom `present`, playbook-authoring `manifest` + `decompose`; rest medium (implicit) | `playbooks/groom/{intake,present,design,draft-plan,decompose-work,research-codebase,research-web,verify-references}/prompt.md`, `playbooks/playbook-authoring/{interview,decompose,states,manifest,step-spec,llm-tests,fixtures,step-prompt,step-suite,smoke-optimizer,regress-optimizer,record-decision}/prompt.md` | 2 | pending |

#### Task 3.1 DoD

- [ ] Mapping covers all four outcomes and states the default is omitting the flag.
- [ ] No other driving-protocol behavior reworded.
- [ ] Four-check IA pass (lesson 0004) run on the edited partial before saving.

#### Task 3.2 DoD

- [ ] `grep -rn "review_gate:" playbooks/` returns nothing.
- [ ] `bin/booping render-playbook groom` and `... playbook-authoring` render with zero STOP notices.
- [ ] Exactly three gates carry `importance: high` across core playbooks.

---

### M4: Docs + spec/eval reference sweep — 3 SP | pending

**Goal**: no stale `review_gate` singular references anywhere in the repo (lesson 0005).

**Verify**: `grep -rn "review_gate[^s]" --include="*.md" --include="*.yaml" . | grep -v ".git/"` → only historical plan/retro files outside the repo.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `documentation/playbook.md` (schema bullet, frontmatter example, repeat-semantics paragraph) + CLAUDE.md playbook blob (`summary,review_gate` → new key, gate-rendering sentence, `--review-gates` on the render-playbook CLI entry) | `documentation/playbook.md`, `CLAUDE.md` | 1 | pending |
| 4.2 | Playbook-authoring prompts/specs/eval files that teach the old key: update prose + assertions to `review_gates` list schema (incl. importance guidance for authors); groom spec index | `playbooks/playbook-authoring/step-prompt/{prompt.md,opus-5.md,tests.yaml}`, `playbooks/playbook-authoring/_specs/steps/step-prompt/{index.md,test-plan.md}`, `playbooks/groom/_specs/index.md` | 2 | pending |

#### Task 4.1 DoD

- [ ] `documentation/playbook.md` documents list shape, importance default, `--review-gates` flag incl. `none`.
- [ ] CLAUDE.md playbook paragraph and CLI section reflect the new schema/flag.

#### Task 4.2 DoD

- [ ] No `review_gate` singular mention left in `playbooks/` (prose, specs, or eval rows).
- [ ] step-prompt authoring guidance tells authors when to tag `high` vs default.
- [ ] Four-check IA pass (lesson 0004) run on each edited prompt artefact before saving.

---

## I/O contract

- **Flag**: `booping render-playbook <name> [--review-gates {low,medium,high,none}]` — minimum importance rendered; `none` suppresses all gates; default `medium`. Composed surface only; `--step` ignores it.
- **stdout**: composed render, gate bullets `Review gate (<importance>): stop after this step — "<text>"; continue only on explicit user confirmation.` — one per surviving gate.
- **stderr**: unchanged (diagnostics only).
- **Exit codes**: unchanged — `0` incl. in-band STOP notices; `≠0` only for unknown playbook/step and argparse errors (invalid `--review-gates` value).

## Final Verification

- [ ] `just lint && just typecheck && just test` green.
- [ ] `bin/booping render-playbook groom --review-gates high` → only `present` gate; `--review-gates none` → no gates; default → intake + present.
- [ ] `--help` shows the new flag.
- [ ] `/playbook` and `/groom-playbook` render cleanly (driving partial is live-rendered).

## Out of scope

- No per-run persistence of the chosen level (`states:` machines untouched — state-machine `gates:` are a separate concept and keep their name).
- No soft-compat parse of the singular key.
- No re-run of playbook-authoring eval suites to green (rows updated; a suite run is /develop's verify if cheap, else flagged).
- The canonical `/groom` skill untouched.

## CLAUDE.md impact

Covered by task 4.1: playbook paragraph (`prompt.md` frontmatter contract, gate rendering, driving) and `render-playbook` CLI entry gain the `review_gates` list + `--review-gates` flag.
