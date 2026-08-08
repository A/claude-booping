---
status: cancelled
title: Review-gate importance levels for playbook steps
type: feature
plan_status: awaiting-plan-review
sp: 26
split_from: null
created: 2026-08-02 15:00
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Review gates become review_gates list with high|medium|low importance, filtered
  at render by --review-level"
commit: null
agents:
  research-codebase: ac586837174fe70d9
  cross-review: a9411039e6b4a4585
sessions:
- 7b822f3b-829c-40e4-b7f6-e59ad3c10fef
metrics_active_minutes: 12
metrics_models:
- claude-fable-5
metrics_tokens_input: 124
metrics_tokens_output: 77530
metrics_tokens_cache_creation: 269565
metrics_tokens_cache_read: 5497777
---

# Review-gate importance levels for playbook steps

## Context

`booping render-playbook` renders each step's `review_gate:` frontmatter — today a single prose string — into the step table and step chrome; when a gate is present the driver always pauses for user confirmation. Interruption density is fixed by the playbook author and not tunable by the runner.

After this plan: each step carries `review_gates:` — a list of `{gate, importance}` with importance `high|medium|low` (absent → `medium`) — and `render-playbook` takes `--review-level {low,medium,high,none}` (default `medium`) that drops gates below the level from the render. The driver maps the user's prose at run start to the flag ("review each step" → `low`, "only main steps" → `high`, "autonomous" → `none`, silence → `medium`) and honors only the gates that rendered. The legacy `review_gate:` key becomes a blocking STOP; all core and vault playbooks are migrated in this sprint.

## Decisions

- **Frontmatter shape**: `review_gates:` — list of `{gate: str, importance: high|medium|low}`; `importance` optional, default `medium`; a step may carry several gates — user-chosen over a singular mapping.
- **Legacy handling**: `review_gate` key present (any value, including null) → blocking STOP (`legacy_review_gate_key`), mirroring the legacy `agent:` key — one shape, no drift; all playbooks migrated same sprint.
- **Filter semantics**: `--review-level` is the minimum importance that renders: `low` = all gates, `medium` = medium+high (default, preserves "main flow" feel), `high` = high only, `none` = autonomous, no gates render. Filtered gates leave no marker; a step with all gates filtered renders `—` in the table and no gate chrome.
- **Jinja treatment**: under `jinja: true`, each `gate` string is rendered like `summary`/`detached` (per-item logic; a Jinja error in a gate is a blocking in-band notice) — consistency with sibling fields.
- **Render format (locked)**: table cell joins gates with `<br>`, each `**{importance}** — {gate}`; step chrome renders `Review gates:` with one `**{importance}** — {gate}` bullet per gate (inline form) / one line per gate (detached paragraph form). Single-gate steps use the same prefixed form.
- **Migration tagging**: importance judged during migration — final-approval gates → `high`, confirm-and-continue gates → `medium`, none demoted to `low` initially; `review_gate: null` keys are deleted, not converted.
- **Stale vault `_dist/build-user-stories/`**: deleted as cleanup (discovery skips `_`-dirs, so it is inert either way).

## Architecture

All changes flow through the existing render pipeline: `Playbook.load_all` → `Step` model (`booping-python/src/booping/context/playbook.py`) → `render-playbook` compose (`booping-python/src/booping/commands/render_playbook.py`) → partials `_playbook_graph.j2` (step-table cell), `_playbook_step.j2` (per-step chrome, inline + detached branches), `_playbook_driving.j2` (driver protocol prose). No skill template references `review_gate` directly, so filtering centralizes in the CLI + these three partials. Callers: the `/playbook` and `/groom-playbook` skills invoke `render-playbook` per the driving partial; they consume the flag via the prose→level mapping added there. `--step` output carries no gate chrome and is unaffected by the filter (step-scoped lessons and bodies render as today).

## Milestones

### M1: Model + parsing — 5 SP | pending

**Goal**: `Step.review_gates` parses the new list shape with defaults and STOPs; the legacy key STOPs.

**Verify**: `cd booping-python && uv run pytest tests/context/playbook_test.py tests/test_render_playbook.py -q` — green, including new cases.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `ReviewGate` dataclass (`gate: str`, `importance: Literal["high","medium","low"]`); `Step.review_gate` → `Step.review_gates: list[ReviewGate]`; parse `review_gates:` in `_load_step` — absent key → `[]`, absent importance → `medium`; non-list value, non-mapping item, missing/empty `gate`, or importance outside the enum → new `GraphProblem` kind `malformed_review_gates` rendered as STOP | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | pending |
| 1.2 | Legacy `review_gate` key (any value) → `GraphProblem` kind `legacy_review_gate_key` + STOP message mirroring `_LEGACY_AGENT_KEY` ("rename to `review_gates:` list form"); test mirroring `test_legacy_agent_key_notice` | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] `review_gates:` list parses into `Step.review_gates` with importance defaulting to `medium`.
- [ ] Absent key parses as empty list; existing no-gate steps unaffected.
- [ ] Each malformed shape (non-list, non-mapping item, missing/empty `gate`, bad importance) produces a `**STOP — tell the user:**` notice naming step and defect, exit 0.
- [ ] Unit tests cover default, explicit levels, multi-gate, and each malformed shape.

#### Task 1.2 DoD

- [ ] A fixture step with `review_gate: anything` (and one with `review_gate: null`) renders only the STOP notice + preamble, exit 0.
- [ ] STOP text names the step and the exact rename target `review_gates:`.
- [ ] Test asserts the notice for both value shapes.

---

### M2: Render filtering — 10 SP | pending

**Goal**: `--review-level` filters gates out of the composed render; surviving gates render in the locked format; `jinja: true` renders gate strings.

**Verify**: `bin/booping render-playbook groom --review-level high --project /home/anton/Dev/@A/notes/projects/claude-booping | grep -c '\*\*high\*\*'` ≥ 1 and `--review-level none` output contains no `Review gate` text; `cd booping-python && uv run pytest -q` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `--review-level {low,medium,high,none}` argparse flag (default `medium`), threaded into compose like `include_lessons`; filter applied once when building the render model so table + chrome see the same surviving set; `--help` documents semantics; flag value appended to the `.booping.log` line | `booping-python/src/booping/commands/render_playbook.py` | 3 | pending |
| 2.2 | Template updates for list rendering in the locked format: `_playbook_graph.j2` cell (`**{importance}** — {gate}` joined by `<br>`, `—` when none survive), `_playbook_step.j2` inline-bullet branch (`Review gates:` + one bullet per gate) and detached-paragraph branch (one line per gate); no chrome when none survive | `src/templates/_partials/_playbook_graph.j2`, `src/templates/_partials/_playbook_step.j2` | 2 | pending |
| 2.3 | Under `jinja: true`, render each surviving gate string through the step's loader chain (extend `_render_step_fields` with per-item list handling); Jinja error in a gate → blocking in-band notice, same as `summary`/`detached` | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/test_render_playbook.py` | 3 | pending |
| 2.4 | Regenerate/adjust golden fixture and render tests: fixture step prompts to `review_gates:` form with mixed importance, `composed-prejinja.golden.md` to the locked format; add filter-level assertions (`medium` drops `low`, `none` drops all, `low` keeps all) | `booping-python/tests/__fixtures__/composed-prejinja.golden.md`, `booping-python/tests/__fixtures__/render-playbook-home/**/prompt.md`, `booping-python/tests/__fixtures__/playbooks-home/**/prompt.md`, `booping-python/tests/test_render_playbook.py` | 2 | pending |

#### Task 2.1 DoD

- [ ] `--review-level` accepts exactly `low|medium|high|none`; anything else → argparse error, exit ≠ 0.
- [ ] Default (flag omitted) renders medium+high gates only.
- [ ] `none` renders zero gate text anywhere in composed output.
- [ ] `--help` states the minimum-importance semantics and the default.

#### Task 2.2 DoD

- [ ] Multi-gate step table cell shows each gate as `**{importance}** — {gate}` joined by `<br>`.
- [ ] Inline step chrome shows `Review gates:` with one prefixed bullet per surviving gate; detached form one prefixed line per gate.
- [ ] Step with no surviving gates: `—` cell, no gate chrome.

#### Task 2.3 DoD

- [ ] A gate containing `{{ config.* }}` resolves at render time under `jinja: true`.
- [ ] A gate with a Jinja error yields a blocking in-band notice naming step and error.
- [ ] Plain (non-jinja) playbooks render gate strings literally.

#### Task 2.4 DoD

- [ ] Golden fixture regenerated and hand-reviewed against the locked format.
- [ ] Tests assert each filter level's surviving set on a mixed-importance fixture.
- [ ] Full pytest suite green.

---

### M3: Driver + prose contract — 4 SP | pending

**Goal**: the driving partial maps user prose to `--review-level` and the authored docs state the new contract.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2 | grep -A4 'review-level'` shows the mapping; docs updated per DoD.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `_playbook_driving.j2`: render invocation carries `--review-level`; add the prose→level mapping ("review each step" → `low`, "only main steps" → `high`, autonomous/no-reviews ask → `none`, nothing said → `medium`); gate-confirmation flow honors only rendered gates (a filtered gate never pauses) | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 3.2 | Authored contract updates: `documentation/playbook.md` (field description, example frontmatter, step-table description, repeat semantics mentions) and the `CLAUDE.md` playbook paragraph (`summary,review_gate` → `summary,review_gates`, jinja-rendered field set, `render-playbook` flag list) | `documentation/playbook.md`, `CLAUDE.md` | 2 | pending |

#### Task 3.1 DoD

- [ ] Rendered `/playbook` and `/groom-playbook` skills show the flag in the render invocation and the four-way mapping.
- [ ] Protocol text states filtered gates never pause the run.

#### Task 3.2 DoD

- [ ] No `review_gate` (singular, as frontmatter key) remains in `documentation/playbook.md` or `CLAUDE.md` prose.
- [ ] `--review-level` documented with values, default, and semantics in `documentation/playbook.md`.

---

### M4: Migration — 7 SP | pending

**Goal**: every shipped and vault playbook carries the new shape; the authoring pipeline emits it; nothing STOPs.

**Verify**: each of the following prints `0` four times (once per level):

```sh
for l in low medium high none; do
  bin/booping render-playbook groom --review-level $l --project /home/anton/Dev/@A/notes/projects/claude-booping | grep -c 'STOP — tell the user'
  bin/booping render-playbook playbook-authoring --review-level $l --project /home/anton/Dev/@A/notes/projects/claude-booping | grep -c 'STOP — tell the user'
  bin/booping render-playbook user-stories --review-level $l --project /home/anton/Dev/@A/notes/projects/claude-booping | grep -c 'STOP — tell the user'
done
```

(`user-stories` resolves through the global root `/home/anton/Dev/@A/notes/projects/_playbooks/`; `--project` supplies the context.)

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Migrate 17 core step prompts: delete `review_gate: null` keys; convert prose gates to `review_gates:` list with judged importance (approval gates — groom `present`, authoring `manifest`/`decompose`-class confirms — → `high`; confirm-and-continue → `medium`; advisory/optional → `low`); groom step suites' `tests.yaml` asserting gate text adjusted | `playbooks/groom/*/prompt.md`, `playbooks/playbook-authoring/*/prompt.md`, affected `playbooks/*/*/tests.yaml` | 2 | pending |
| 4.2 | `playbook-authoring` generator emits the new shape: `step-prompt/prompt.md` + `step-prompt/opus-5.md` output contract, `_specs/steps/step-prompt/index.md`, and `step-prompt/tests.yaml` assertions (`^review_gate:` → list-form check, rubric wording) | `playbooks/playbook-authoring/step-prompt/prompt.md`, `playbooks/playbook-authoring/step-prompt/opus-5.md`, `playbooks/playbook-authoring/_specs/steps/step-prompt/index.md`, `playbooks/playbook-authoring/step-prompt/tests.yaml` | 3 | pending |
| 4.3 | Vault migration (requires this machine's vault at `/home/anton/Dev/@A/notes/projects/_playbooks/` — local filesystem edit, no repo): convert the 5 `user-stories` step prompts — `build-index`, `story-map`, `stories`, `gherkin` (prose gates → list form), `reshake` (`review_gate: null` → key deleted); delete stale `_dist/build-user-stories/`; confirm `_test/steps/*.md` flat files are outside step discovery (dir-form only) and leave them | `/home/anton/Dev/@A/notes/projects/_playbooks/user-stories/{build-index,story-map,stories,gherkin,reshake}/prompt.md`, `/home/anton/Dev/@A/notes/projects/_playbooks/_dist/` | 1 | pending |
| 4.4 | Full-surface check: render all three playbooks at all four levels — zero STOP/Note regressions, gate sets match the judged tagging; `just lint && just typecheck && just test` green | — | 1 | pending |

#### Task 4.1 DoD

- [ ] No `review_gate:` key remains under `playbooks/`.
- [ ] Every converted gate carries an explicit importance matching the judged class.
- [ ] Groom/authoring eval suites referencing gate text pass or are updated.

#### Task 4.2 DoD

- [ ] A step prompt generated by `step-prompt` carries `review_gates:` list form.
- [ ] `step-prompt/tests.yaml` asserts the list form, not `^review_gate:`.

#### Task 4.3 DoD

- [ ] `user-stories` renders clean at all four levels.
- [ ] `_dist/build-user-stories/` no longer exists.

#### Task 4.4 DoD

- [ ] Four-level render loop prints zero STOPs for all three playbooks.
- [ ] `just lint`, `just typecheck`, `just test` all green.

---

## I/O contract

- **Arguments / flags**: `booping render-playbook <name> [--step <step>] [--project <path>] [--output <path>] [--no-lessons] [--review-level {low,medium,high,none}]` — `--review-level` sets the minimum gate importance rendered; default `medium`; `none` renders no gates.
- **stdin**: unused (unchanged).
- **stdout**: composed markdown; gates render as `**{importance}** — {gate}` (table cell `<br>`-joined; chrome one bullet/line per gate). `--step` output unchanged.
- **stderr**: unknown playbook/step diagnostics (unchanged); graph problems stay in-band on stdout.
- **Exit codes**: unchanged — `0` on render (including STOP notices), `1` unknown playbook/step, argparse error on invalid `--review-level` value.

## Final Verification

- [ ] Help text updated and accurate for `--review-level`.
- [ ] Happy path (`groom` at default level) + failure path (legacy-key fixture STOP, invalid flag value) verified.
- [ ] Exit codes match the documented contract.
- [ ] `/playbook` and `/groom-playbook` render cleanly and show the prose→level mapping.

## Out of scope

- No per-run persistence of the chosen review level (state machines unchanged; the level is a render-time argument).
- No importance on state-machine transition `gates` (`playbook.yaml`) — only step `review_gates`.
- No config-tier default for the review level (`src/config.yaml` untouched); a later plan may add one.
- No changes to `/groom` (canonical skill) or its templates.

## CLAUDE.md impact

Update the playbook paragraph in `CLAUDE.md`: `summary,review_gate` → `summary,review_gates` list shape, the jinja-rendered field set (summary, detached, gate strings), the legacy-key STOP list gains `review_gate`, and the `render-playbook` CLI line gains `--review-level`. Covered by task 3.2.

## Risk register

_(empty — populated by cross-review disposition if needed)_
