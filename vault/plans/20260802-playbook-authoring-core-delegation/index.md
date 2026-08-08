---
title: Playbook-authoring into core + delegation-level model
type: feature
status: done
sp: 24
split_from: null
created: 2026-08-02 01:38
planned: 20260801 18:05
started: 20260801 18:14
completed: 2026-08-01 18:38
retro: null
goal: null
summary: "Move playbook-authoring to core, rename agent: to detached:, drop inputs/outputs,
  teach delegation levels"
commit: 926d0848a7774613bc30f6991d684731fd386113
sessions:
- 979938b0-1a6b-4c3a-8951-24a6ebe2e555
- 173d8d14-cac6-4a43-8908-dd0e4ca7be4e
metrics_active_minutes: 56
metrics_models:
- claude-fable-5
metrics_tokens_input: 1304
metrics_tokens_output: 271684
metrics_tokens_cache_creation: 1421328
metrics_tokens_cache_read: 20922280
---

# Playbook-authoring into core + delegation-level model

## Context

The `playbook-authoring` playbook lives in the global vault root (`~/Dev/@A/notes/projects/_playbooks/playbook-authoring/`) while the playbooks it teaches people to author increasingly ship in core (`<repo>/playbooks/`). Its eval suites depend on the shared `_lib/` harness, which the repo currently reaches through an untracked, machine-specific symlink (`playbooks/_lib -> …/notes/projects/_playbooks/_lib`) that groom's own core suites already rely on.

Separately, the step-frontmatter vocabulary predates the delegation-level model settled in `playbooks/groom/_specs/index.md`: three levels — **inline** (runner performs the step), **assisted** (runner performs, delegates heavy reads/research to a configured agent that returns a compressed summary), **detached** (an agent fetches and performs the step body; runner sees only the receipt). Levels 1–2 need no mechanics; only detachment does. Today's `agent:` field conflates all three, and `inputs:`/`outputs:` add advisory frontmatter the runner no longer operates from.

After this plan: `playbook-authoring` is a core playbook with its suites and a real committed `playbooks/_lib/`; step frontmatter carries `detached:` (only when detached) and no `inputs:`/`outputs:`; playbook-authoring teaches delegation levels and task-nature-dependent gate design.

## Decisions

- **`detached:` replaces `agent:`**: presence = the step runs inside an agent from the start; value keeps today's grammar (`<model>:<effort>` or named agent). Absent = inline or assisted — both are runner-performed; assisted is guidance-level (the step prompt tells the runner what to delegate to the researcher agent the config maps), so it needs no frontmatter. Field name states the one thing the framework must know.
- **Legacy `agent:` key → blocking STOP notice** ("`agent:` was renamed to `detached:`"): silent ignore would degrade agent-bearing steps to inline with no signal; vault playbooks outside this repo (e.g. `user-stories`) must fail loudly, not quietly change behavior.
- **`inputs:`/`outputs:` dropped framework-wide**: the runner assembles a detached step's bootstrap inputs from run-time context plus prior receipts, and the return contract becomes the existing uniform fallback — "artifacts written + outcome, ≤ 5 lines". Contracts live in step specs (`_specs/steps/*/index.md` Needs / Output files), not frontmatter.
- **Value-preserving sweep in existing playbooks**: groom's and playbook-authoring's step prompts get `agent: X` → `detached: X` with today's values, `inputs:`/`outputs:` keys deleted. No behavior change — groom's rework to inline/assisted per its new specs is a separate plan.
- **Move is wholesale, `_lib` becomes real and canonical in-repo**: step dirs incl. `tests.yaml`/`promptfooconfig.yaml`/`_fixtures`, `_specs/`, manifests all move (core groom precedent); the depth-2 `../../_lib` relative paths survive unchanged. `playbooks/_lib/` is committed as real files (no `__pycache__`); the vault's `_playbooks/_lib` becomes a symlink pointing at the repo so remaining vault playbooks keep resolving. One source of truth, portable repo.
- **Gate-design guidance is task-nature-dependent**: *plan-preparing* playbooks (intent clear; LLM prepares, asks only on important options; few gates, late) vs *narrowing* playbooks (intent unclear; gates narrow understanding top-down, level by level). Taught in `decompose` (gates are cut with the steps), referenced from `step-spec` (per-step `review_gate` line).

## Architecture

Load path unchanged: `Playbook.load_all` scans core → global → local; after the move `playbook-authoring` resolves at core scope (name-unique rule requires the global copy deleted in the same milestone). Frontmatter flows `prompt.md` → `_load_step()` → `Step` → `_playbook_step.j2` (section metadata) → `_playbook_driving.j2` (bootstrap prompt). The rename and the io-drop each cut one field out of that chain end-to-end; eval harness (vault justfile/`_scripts`) keeps running vault-side against both roots via `booping render-playbook` global resolution.

## Milestones

### M1: Move playbook-authoring into core + materialize `_lib` — 4 SP | done

**Goal**: `playbooks/playbook-authoring/` and a real committed `playbooks/_lib/` exist in the repo; the global copy and the machine-specific symlink are gone; nothing references the old location.

**Verify**: `bin/booping render-playbook playbook-authoring | head -30` renders with no clash/STOP notices; `git status` shows no symlink; `ls -la playbooks/_lib` shows a real directory.

| Task | Description                                                                                                                                                                                                                                                                                                                | Files                                                                             | SP  | Status  |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | --- | ------- |
| 1.1  | **First `rm playbooks/_lib`** (it is a symlink — copying without unlinking would write into the vault source), then copy the vault `_lib/` (asserts/, tests/, *.md, *.py, *.txt, grader.yaml; exclude `__pycache__`) from `/home/anton/Dev/@A/notes/projects/_playbooks/_lib/` into a real `playbooks/_lib/` and commit it | `playbooks/_lib/**`                                                               | 1   | done    |
| 1.2  | Move `playbook-authoring/` wholesale from `/home/anton/Dev/@A/notes/projects/_playbooks/playbook-authoring/` into `playbooks/playbook-authoring/` (step dirs incl. suites + `_fixtures`, `_specs/`, `playbook.md`, `playbook.yaml`); delete the vault copy in the same change                                              | `playbooks/playbook-authoring/**`                                                 | 1   | done    |
| 1.3  | Invert the symlink: `ln -s` `/home/anton/Dev/@A/notes/projects/_playbooks/_lib` → repo `playbooks/_lib` (remove the real vault dir after 1.1's copy is committed; orchestrator-run, vault-side)                                                                                                                            | `/home/anton/Dev/@A/notes/projects/_playbooks/_lib`                               | 1   | done    |
| 1.4  | Update stale references: repo `CLAUDE.md` ("eval suites … not in this repo" sentence, playbooks/layout list); `/home/anton/Dev/@A/notes/projects/_playbooks/README.md` self-contained claim + `/home/anton/Dev/@A/notes/projects/_playbooks/CLAUDE.md` root note (orchestrator-run for vault files)                        | `CLAUDE.md`, `/home/anton/Dev/@A/notes/projects/_playbooks/{README.md,CLAUDE.md}` | 1   | done    |

#### Task 1.1 DoD
- [x] `playbooks/_lib` is a real directory in git, byte-identical to the vault `_lib` (minus `__pycache__`).
- [x] `playbooks/groom/*/promptfooconfig.yaml` still resolve `../../_lib/claude_provider.py` and `../../_lib/grader.yaml`.

#### Task 1.2 DoD
- [x] `bin/booping render-playbook playbook-authoring` renders from core scope, no `name_clash` STOP.
- [x] All 10 step `promptfooconfig.yaml` files resolve `../../_lib/*` unchanged (depth-2 preserved).
- [x] Vault root no longer contains `playbook-authoring/`.

#### Task 1.3 DoD
- [x] Vault `_playbooks/_lib` is a symlink to the repo `playbooks/_lib`; vault-side suites of remaining playbooks still resolve `../../_lib/*`.

#### Task 1.4 DoD
- [x] Repo `CLAUDE.md` no longer claims eval suites live only vault-side; layout list names `playbooks/playbook-authoring/` and `playbooks/_lib/`.
- [x] Vault README/CLAUDE.md describe the inverted `_lib` arrangement.

---

### M2: `agent:` → `detached:` framework rename — 7 SP | done

**Goal**: the framework parses, validates, renders, and documents `detached:`; a step prompt still carrying `agent:` produces a blocking STOP notice; all committed step prompts are swept value-preserving.

**Verify**: `just test && just lint && just typecheck`; `bin/booping render-playbook groom | grep -i "sub-agent"` shows agent bullets intact; a scratch prompt with `agent: opus:low` renders the STOP notice.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rename field end-to-end in python: `Step.agent` → `Step.detached`, `resolve_agent` → `resolve_detached`, parse site; add legacy-key detection emitting a blocking problem notice; update parallel-wave check + `_INLINE_PARALLEL` wording | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py` | 3 | done |
| 2.2 | Update partials: `_playbook_step.j2` (resolve call, condition, sub-agent bullets), `_playbook_driving.j2` (agent-bullet protocol prose, parallel-instances rule) | `src/templates/_partials/_playbook_step.j2`, `src/templates/_partials/_playbook_driving.j2` | 2 | done |
| 2.3 | Sweep step prompts value-preserving (`agent: X` → `detached: X`, incl. `agent: null` → key dropped): groom 8, playbook-authoring 12, and remaining vault playbooks at `/home/anton/Dev/@A/notes/projects/_playbooks/` (`user-stories`, plus any other dir with step prompts — enumerate at execution); update the named test sites: `booping-python/tests/context/playbook_test.py` (`test_step_review_gate_and_agent_null_vs_set`, `test_resolve_agent`), `booping-python/tests/test_render_playbook.py` (`test_model_agent_directive`, `test_named_agent_directive`, `test_inline_in_parallel_notice`, `test_inline_steps_sharing_an_inner_wave_notice`, `test_step_body_only_jinja_rendered`, `_build`/`_sy` helpers), fixtures under `booping-python/tests/__fixtures__/**` | `playbooks/groom/*/prompt.md`, `playbooks/playbook-authoring/*/prompt.md`, vault `_playbooks/*/`, `booping-python/tests/**` | 1 | done |
| 2.4 | Docs: `documentation/playbook.md` (frontmatter list, example, agent-grammar section → detached grammar, render/driving paragraphs, **plus a new canonical "Delegation levels" section defining inline/assisted/detached** — the single source M4 references), repo `CLAUDE.md` playbook paragraph | `documentation/playbook.md`, `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD
- [x] `resolve_detached` keeps the three-way grammar (null/model:effort/named); all callers renamed.
- [x] `agent:` in any step frontmatter → a `problems` entry rendered through the existing in-band blocking-notice channel (`**STOP — tell the user:**`, same mechanism as malformed-node/nested-subgraph notices — no exception raised); covered by a test.
- [x] Parallel-wave check reads "must be `detached:`"; existing wave tests updated and green.

#### Task 2.2 DoD
- [x] Rendered step sections show the same sub-agent bullets as before the rename (diff on `render-playbook groom` limited to wording the rename requires).
- [x] Driving partial contains no `agent:` vocabulary.

#### Task 2.3 DoD
- [x] No committed `prompt.md` carries an `agent:` key; detached values byte-identical to prior agent values.
- [x] `just test` green.

#### Task 2.4 DoD
- [x] `documentation/playbook.md` and `CLAUDE.md` mention `agent:` only as the renamed legacy key.

---

### M3: Drop `inputs:`/`outputs:` framework-wide — 6 SP | done

**Goal**: the framework neither parses nor renders step io frontmatter; bootstrap prompts use run-time context + prior receipts for inputs and the uniform fallback receipt for returns.

**Verify**: `just test && just lint && just typecheck`; `bin/booping render-playbook groom | grep -E "Inputs:|Outputs:"` returns nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Remove `StepInput`, `Step.inputs`/`Step.outputs`, `_entries`/`_parse_inputs`/`_parse_outputs`, parse sites; delete/update their tests | `booping-python/src/booping/context/playbook.py`, `booping-python/tests/context/playbook_test.py` | 2 | done |
| 3.2 | Remove `Inputs:`/`Outputs:` rendering + condition from `_playbook_step.j2`; rework `_playbook_driving.j2` bootstrap build — `## Inputs` from run-time context + prior receipts only, `## Return` always the fallback receipt ("artifacts written + outcome, ≤ 5 lines"); update render tests | `src/templates/_partials/_playbook_step.j2`, `src/templates/_partials/_playbook_driving.j2`, `booping-python/tests/test_render_playbook.py` | 2 | done |
| 3.3 | Sweep `inputs:`/`outputs:` keys out of all committed step prompts (groom 8, playbook-authoring 12), remaining vault playbooks at `/home/anton/Dev/@A/notes/projects/_playbooks/` (`user-stories` + any others), and test fixtures | `playbooks/groom/*/prompt.md`, `playbooks/playbook-authoring/*/prompt.md`, vault `_playbooks/*/`, `booping-python/tests/__fixtures__/**` | 1 | done |
| 3.4 | Docs: `documentation/playbook.md` (io frontmatter spec, YAML example, bootstrap paragraphs), repo `CLAUDE.md` playbook paragraph | `documentation/playbook.md`, `CLAUDE.md` | 1 | done |

#### Task 3.1 DoD
- [x] `playbook.py` has no io types/fields/parsers; `just typecheck` green.
- [x] io-specific tests removed, remaining suite green.

#### Task 3.2 DoD
- [x] Rendered sections carry no `Inputs:`/`Outputs:` bullets; driving partial's bootstrap contract states context+receipts and the fallback return.
- [x] Render tests for io bullets replaced by an absence assertion.

#### Task 3.3 DoD
- [x] `grep -rl "^inputs:\|^outputs:" playbooks/*/*/prompt.md` empty.

#### Task 3.4 DoD
- [x] Docs describe frontmatter as `summary`, `review_gate`, optional `title`, optional `detached`.

---

### M4: Teach delegation levels + gate design in playbook-authoring — 7 SP | done

**Goal**: authored playbooks come out of playbook-authoring carrying delegation levels in their specs and `detached:`-only frontmatter; gate design is taught as task-nature-dependent.

**Verify**: `bin/booping render-playbook playbook-authoring --step step-prompt` and `--step decompose` show the new guidance; affected eval suites updated and referenced fixtures consistent.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite the frontmatter recipe in `step-prompt`: emit `detached:` only for detached steps (grammar + derivation), never io keys; assisted steps get body guidance naming what the runner delegates to the configured researcher | `playbooks/playbook-authoring/step-prompt/opus-5.md` | 2 | done |
| 4.2 | `decompose`: `## Steps` table gains a Delegation column; level definitions are **referenced from the canonical "Delegation levels" section in `documentation/playbook.md`** (added in 2.4), not duplicated; add gate-design guidance — plan-preparing vs narrowing playbook natures and their gate placement | `playbooks/playbook-authoring/decompose/opus-5.md` | 2 | done |
| 4.3 | `step-spec`: Contract keeps Needs / Output files as the io home; add a Delegation bullet; `review_gate` line references the task-nature guidance | `playbooks/playbook-authoring/step-spec/opus-5.md` | 1 | done |
| 4.4 | Update the three steps' eval suites to the new contracts (frontmatter recipe assertions, Delegation column, gate guidance); adjust fixtures | `playbooks/playbook-authoring/{step-prompt,decompose,step-spec}/tests.yaml`, same dirs `_fixtures/` | 2 | done |

#### Task 4.1 DoD
- [x] Recipe emits no `agent:`/`inputs:`/`outputs:`; detached grammar matches `documentation/playbook.md`.
- [x] Assisted-tier guidance present: runner-performed, researcher delegation named in body prose.

#### Task 4.2 DoD
- [x] Steps table spec includes Delegation column; level definitions referenced from `documentation/playbook.md`, not restated.
- [x] Gate-design section distinguishes plan-preparing vs narrowing natures with placement rules.

#### Task 4.3 DoD
- [x] Contract shape lists Needs / Value / Output files / Harness return / Review gate / Delegation.

#### Task 4.4 DoD
- [x] `just test` unaffected; suites in the three step dirs assert the new shapes; no fixture references the old frontmatter recipe.

---

## Final Verification

- [x] `just test && just lint && just typecheck` green.
- [x] `bin/booping render-playbook playbook-authoring` and `bin/booping render-playbook groom` render clean: no STOP/Note notices, no `agent:`/`Inputs:`/`Outputs:` vocabulary.
- [x] `playbooks/_lib` is a real committed directory; vault `_playbooks/_lib` symlinks to it; vault-side `just smoke` for a remaining vault playbook still resolves the harness.
- [x] Repo `CLAUDE.md` and `documentation/playbook.md` consistent with the new vocabulary and layout.

## Out of scope

- Groom playbook rework to inline/assisted per its new `_specs/index.md` (plan-as-directory, single present gate, agent-id tracking, mechanical research-web skip) — separate plan; this sprint only value-preserving sweeps of its prompts.
- Justfile regress/smoke selector filtering — own plan (`plans/20260801-12-02_justfile-eval-filtering`).
- Driver run-id tracking and any `_playbook_driving.j2` protocol change beyond the rename/io wording.
- Any change to the `/groom` skill or other skills/agents.

## CLAUDE.md impact

- Layout section: add `playbooks/playbook-authoring/`, `playbooks/_lib/`; drop "eval suites … live vault-side … not in this repo" claim (owned by task 1.4).
- Playbook paragraph: `agent` grammar → `detached` grammar, parallel-wave rule wording, remove `inputs`/`outputs` advisory sentences (owned by tasks 2.4, 3.4).
