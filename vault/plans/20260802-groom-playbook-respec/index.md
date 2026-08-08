---
title: Groom playbook respec — inline/assisted, plan-as-directory, single gate
type: feature
status: done
sp: 34
split_from: null
created: 2026-08-02 03:01
planned: 20260801 18:09
started: 20260801 18:49
completed: 2026-08-01 20:01
retro: null
goal: null
summary: "Groom playbook runs inline/assisted with plan-as-directory artifacts and
  one approval gate at present"
commit: 11c81de39639572e0982f53d60e5db29a7db9be8
sessions:
- 242dc80d-46f9-4e5c-a154-0ad43953b096
- 345f0901-a3ed-47b3-8f39-37cbddbc0e08
metrics_active_minutes: 109
metrics_models:
- claude-fable-5
metrics_tokens_input: 1639
metrics_tokens_output: 556850
metrics_tokens_cache_creation: 1644698
metrics_tokens_cache_read: 58472341
---

# Groom playbook respec — inline/assisted, plan-as-directory, single gate

## Context

The core groom playbook (`playbooks/groom/`) still implements its pre-respec shape: every step
spawns its own sub-agent, four confirm statuses gate the flow, artifacts scatter across
`{vault}/_runs/groom/{slug}/`, and `research-web` judges novelty itself — the combination that
produced 700K-token runs with redundant web research. The target shape is fully specified in
`playbooks/groom/_specs/` (index.md, states.md, steps/*/index.md — already reviewed): inline and
assisted delegation levels, a single approval gate at `present`, the plan as a directory
`plans/{slug}/` holding `plan.md` + `index.md` + optional `research.md`, user-gated web research
executed mechanically, references verified proportionally, and delegated-agent continuity across
loopbacks.

After this plan: the playbook's real files (`playbook.yaml`, `playbook.md`, 8 step prompts and
bodies, `_scripts/`) implement those specs; `Plan.load_all` and every plan-path consumer handle
directory plans alongside flat files; the driving partial documents assisted delegation and
agent-id resume; groom's eval suites assert the new contracts.

**Dependency landed and verified** (`plans/20260802-playbook-authoring-core-delegation.md`,
commits `1bad828`…`11c81de`): `detached:` vocabulary in place (groom prompts carry
value-preserved `detached: <model>:<effort>`, no `agent:`/`inputs:`/`outputs:`),
`playbooks/_lib/` committed, playbook-authoring in core, partials renamed. This plan's file
lists were revalidated against that state on 2026-08-02.

## Decisions

- **Assisted is body-driven, zero framework parsing**: an assisted step keeps no frontmatter
  marker (no `detached:` key — the runner performs the step); its body instructs the runner to
  delegate the heavy reads to `{{ config.research_agent }}` with a bounded return contract
  (lesson 0007). Same mechanism as draft-plan's existing `cross_review` block. Rejected: a
  `delegation:` frontmatter field — more framework surface, no behavior gain.
- **New core config key `research_agent`**: `research_agent: "booping:booping-researcher"` in
  `src/config.yaml`, shape parallel to `cross_review.agent`, project-overridable. Groom's jinja
  bodies read it; nothing in python parses it.
- **Agent-id continuity is protocol, not machinery**: the runner records spawned agent ids in
  `index.md` frontmatter (`agents:` mapping) and resumes the same agent on a same-session
  loopback; a stale or cross-session id falls back to a fresh spawn. No CLI change.
- **Mixed-shape plans are permanent**: `Plan.load_all` discovers both `plans/*.md` (flat: skill
  plans, parked stubs) and `plans/*/plan.md` (directory plans). Intake's parked-stub adoption
  converts the stub file into a directory. A new `Plan.rel_link` property owns the
  vault-relative link so templates stop deriving it from `path.name`.
- **`research-web` never judges**: intake records the user's web-research decision in
  `index.md`; research-web branches on it mechanically — requested → `research.md`, not
  requested → one skip line. The Researched/Skipped verdict machinery and its novelty fixtures
  are retired.
- **Single review gate at `present`**: state chart per `_specs/states.md` — confirm statuses
  (`awaiting-framing-confirm`, `awaiting-design-confirm`, `awaiting-decomposition-confirm`)
  removed; intake's scope answers are its confirmation, design aligns in conversation,
  `awaiting-approval` is the only gate status.
- **Suites rewritten, harness untouched**: `claude_provider.py`, `grader.yaml`, `_lib/asserts/*`
  stay; fixtures and `tests.yaml` are rewritten per step against the new contracts.

## Architecture

Source of truth for every contract is `playbooks/groom/_specs/`: `index.md` (flow, delegation
levels, artifact model), `states.md` (state chart, hooks, scripts), `steps/{step}/index.md`
(per-step Needs / Output files / Step report / Review gate + examples). Implementation flows
spec → files: `playbook.yaml` mirrors states.md; `playbook.md` carries the preamble facts
(slug `{YYYYMMDD}-{kebab-title}`, workdir = `plans/{slug}/`); each step's `prompt.md` +
model-variant body implements its step spec; `_scripts/_plan_status.py` derives
vault = `workdir.parent.parent` and stamps `plans/{slug}/plan.md`. The driving partial
(`src/templates/_partials/_playbook_driving.j2`, shared by `/playbook` and `/groom-playbook`)
gains the assisted-delegation and agent-resume protocol; `booping-python` gains directory-plan
discovery consumed by `render-sprints` and the skill templates.

## Milestones

### M1: Directory-plan support in the plan model — 6 SP | done

**Goal**: a `plans/{slug}/plan.md` directory plan is discovered, linked, and committed exactly
like a flat plan, with both shapes coexisting.

**Verify**: `just test && just lint && just typecheck`; scratch vault with one flat + one
directory plan → `bin/booping render-sprints --output -` lists both with correct links.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `Plan.load_all` dual glob (`*.md` + `*/plan.md`); `Plan.slug` (dir name when nested, stem when flat) and `Plan.rel_link` (vault-relative link) properties; tests for mixed-shape discovery | `booping-python/src/booping/context/plan.py`, `booping-python/tests/context/plan_test.py` | 3 | done |
| 1.2 | Replace `plan.path.name` link derivation with `plan.rel_link` in the sprints template and the five skill templates that render plan links | `src/templates/sprints.md.j2`, `src/templates/skills/{chat,code-review,develop,learn,retro}.md.j2` | 1 | done |
| 1.3 | `vault_commit.resolve_vault` handles `plans/{slug}/plan.md` (grandparent-named-`plans` case); commit-message stem uses the slug for nested plans; tests | `booping-python/src/booping/commands/vault_commit.py`, `booping-python/tests/commands/vault_commit_test.py` | 2 | done |

#### Task 1.1 DoD
- [x] Mixed `plans/` (flat files, stubs, directories) loads without duplicates or misses; test covers all three.
- [x] Collision rule implemented + tested: when `plans/foo.md` and `plans/foo/plan.md` both exist, the directory plan wins and the flat file is skipped with a stderr warning.
- [x] `Plan.slug` returns the directory name for nested plans, the file stem for flat ones.
- [x] `just typecheck` green.

#### Task 1.2 DoD
- [x] `grep -rn "path.name" src/templates/` shows no plan-link derivation left.
- [x] Rendered sprints links resolve for both shapes.

#### Task 1.3 DoD
- [x] `vault-commit` on a directory plan stages `plans/{slug}/plan.md` + `sprints.md`, message carries the slug.
- [x] Flat-plan behavior byte-identical to before; tests cover both.

---

### M2: `research_agent` config key + driving-partial protocol — 4 SP | done

**Goal**: the shared driving protocol documents assisted delegation and agent-id resume; the
researcher agent is config-mapped.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2 | grep -A3 -i assisted`
shows the protocol; `bin/booping config-get research_agent` prints the default.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add core `research_agent: "booping:booping-researcher"` key; document it in the playbook docs page (config keys a playbook body may read) | `src/config.yaml`, `documentation/playbook.md` | 1 | done |
| 2.2 | Driving partial: assisted-delegation prose (a step body may direct the runner to delegate work to a config-named agent with a bounded return); agent-id protocol (record spawned ids in the run artifact's `agents:` frontmatter, resume same-session via id, stale id → fresh spawn); workdir wording allows a playbook preamble to name its own workdir convention instead of `_runs/` | `src/templates/_partials/_playbook_driving.j2` | 3 | done |

#### Task 2.1 DoD
- [x] `booping config-get research_agent` → `booping:booping-researcher`; project tier override wins.
- [x] Docs name the key beside `cross_review`.

#### Task 2.2 DoD
- [x] Partial renders in both `/playbook` and `/groom-playbook` bodies without stale `_runs/`-only wording.
- [x] Assisted and resume protocol are generic (no groom-specific paths).
- [x] Staleness check stated as an exact rule: resume only an id this conversation recorded from its own spawn; any id read back from the run artifact on a resumed run is stale by definition → fresh spawn.
- [x] Detached-spawn protocol unchanged for playbooks that use `detached:`.
- [x] Partial passes the lesson-0004 four-check pass (scoping, duplication, configurability, hierarchy).

---

### M3: Groom playbook structure — 6 SP | done

**Goal**: manifest, preamble, and scripts implement the plan-as-directory, single-gate machine.

**Verify**: `bin/booping render-playbook groom | head -80` — no STOP/Note notices; `## State`
section shows the collapsed chart; `grep -rn "_runs" playbooks/groom/playbook.{md,yaml}` empty.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Rewrite `states.run` per `_specs/states.md`: nine statuses, single `awaiting-approval` gate, hooks (`script plan-in-spec` on framing→researching, `script plan-awaiting-plan-review` on decomposing→verifying-references, approval edge stamps `reviewed_at` on index.md + `script plan-ready-for-dev`); artifact `index.md` | `playbooks/groom/playbook.yaml` | 2 | done |
| 3.2 | Rewrite the preamble: slug `{YYYYMMDD}-{kebab-title}`, workdir = `plans/{slug}/`, three-artifact model, web-research decision at intake, single-gate flow, `booping transition` prohibition kept | `playbooks/groom/playbook.md` | 2 | done |
| 3.3 | Rework `_plan_status.py`: vault = `workdir.parent.parent`, plan = `workdir/plan.md`, slug = workdir basename; sprints re-render via the mixed-shape loader; keep the three thin wrappers `plan-in-spec`, `plan-awaiting-plan-review`, `plan-ready-for-dev` | `playbooks/groom/_scripts/_plan_status.py`, `playbooks/groom/_scripts/plan-in-spec`, `playbooks/groom/_scripts/plan-awaiting-plan-review`, `playbooks/groom/_scripts/plan-ready-for-dev` | 2 | done |

#### Task 3.1 DoD
- [x] Statuses and edges byte-match `_specs/states.md`'s table (states, when, gates, hooks).
- [x] `booping playbook-state groom --workdir <scratch>` reports `not-started` → bootstrap to `framing`.

#### Task 3.2 DoD
- [x] Preamble names no `_runs/`, no confirm statuses, no old slug format.
- [x] `render-playbook groom` renders the preamble clean.

#### Task 3.3 DoD
- [x] Scripts stamp `plans/{slug}/plan.md`, render sprints, commit — verified against a scratch vault with a directory plan.
- [x] Non-zero exit on missing plan.md aborts the transition (existing contract preserved).

---

### M4: Step prompts — intake through design — 7 SP | done

**Goal**: the first wave's steps implement their specs: framing into `index.md`, assisted
research bodies, conversational design. Every step in this milestone drops its `detached:` key —
all four run inline or assisted per the specs' Delegation bullets.

**Verify**: `bin/booping render-playbook groom --step <step>` for each — bodies match specs, no
`_runs/`, no verdict machinery in research-web.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | intake per `_specs/steps/intake/index.md`: framing into `index.md` (machine bootstraps it), `plan.md` identity creation, web-research decision capture, soft gate, parked-stub → directory adoption in this exact order: create `plans/{slug}/` → write `plan.md` from the stub's content (status flipped) → delete the stub file; re-entry tolerant (dir already present + stub gone = done; both present = finish by deleting the stub, per the loader's dir-wins rule) | `playbooks/groom/intake/prompt.md`, `playbooks/groom/intake/fable-5.md` | 2 | done |
| 4.2 | research-codebase per its spec: assisted body — runner scopes the map, delegates bulk reads to `{{ config.research_agent }}` with a bounded return, writes `## Blast radius` into `index.md`; targeted single-fact web checks local-ground-truth-first | `playbooks/groom/research-codebase/prompt.md`, `playbooks/groom/research-codebase/opus-5.md` | 2 | done |
| 4.3 | research-web per its spec: mechanical branch on intake's decision — requested → `research.md` sized to open questions via the researcher agent; not requested → skip line in `index.md`; verdict machinery deleted | `playbooks/groom/research-web/prompt.md`, `playbooks/groom/research-web/opus-5.md` | 2 | done |
| 4.4 | design per its spec: conversational alignment (no confirm status), `## Design` section with settled trade-offs, loopback-to-research edge honored | `playbooks/groom/design/prompt.md`, `playbooks/groom/design/opus-5.md` | 1 | done |

#### Task 4.1 DoD
- [x] Body writes only the two files the spec names; report shape matches the spec's Return Format.
- [x] Web-research decision recorded on both paths (requested / not requested).
- [x] Adoption sequence spelled out in the body with the re-entry rule; no path leaves both stub and directory behind.

#### Task 4.2 DoD
- [x] Delegation instruction names `{{ config.research_agent }}` and bounds the return (changed-files/summary only).
- [x] No standalone research-codebase.md anywhere.

#### Task 4.3 DoD
- [x] `grep -i "verdict\|Researched\|Skipped" playbooks/groom/research-web/opus-5.md` shows no judgment path — only the mechanical branch.

#### Task 4.4 DoD
- [x] No `review_gate` confirm loop in frontmatter; open trade-offs asked in conversation per spec.

---

### M5: Step prompts — draft through present — 5 SP | done

**Goal**: the plan-writing wave implements its specs: plan.md targets, `index.md` sections,
proportional verification, single human-first gate. Every step in this milestone drops its
`detached:` key — all four run inline or assisted per the specs' Delegation bullets.

**Verify**: `bin/booping render-playbook groom --step <step>` for each — paths and gate wording
match specs.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | draft-plan: target `plans/{slug}/plan.md`, inputs from `index.md` sections, cross-review block kept as-is | `playbooks/groom/draft-plan/prompt.md`, `playbooks/groom/draft-plan/opus-5.md` | 1 | done |
| 5.2 | decompose-work: `## Refinement` section in `index.md`, gate removed (notes travel to present), plan edits on refined path only | `playbooks/groom/decompose-work/prompt.md`, `playbooks/groom/decompose-work/opus-5.md` | 1 | done |
| 5.3 | verify-references: assisted body — runner selects novel load-bearing refs, reuses `research.md` sources, delegates upstream checks to the researcher; `## References` section with `skipped — stable` verdicts; corrections into `plan.md` | `playbooks/groom/verify-references/prompt.md`, `playbooks/groom/verify-references/opus-5.md` | 2 | done |
| 5.4 | present: `## Approval` section with `### Summary` human-first prose, sole-gate wording, loopback routing, branch offer | `playbooks/groom/present/prompt.md`, `playbooks/groom/present/sonnet-5.md` | 1 | done |

#### Task 5.1 DoD
- [x] Only path changes vs current body; cross-review contract byte-preserved.

#### Task 5.2 DoD
- [x] No user-confirm wording; skip path leaves plan.md untouched per spec.

#### Task 5.3 DoD
- [x] Body names the skip classes (stable well-known syntax) and the `research.md` reuse rule.
- [x] Researcher return contract fixed in the body: one row per checked reference — reference, plan claim, upstream finding, verdict, source URL + retrieval date — and nothing else (lesson 0007).

#### Task 5.4 DoD
- [x] Gate states it is the run's only review gate; summary opens with stakeholder prose before mechanics.

---

### M6: Eval suites + stale-reference cleanup — 6 SP | done

**Goal**: groom's suites assert the new contracts; no repo doc still describes the old shape.

**Verify**: `just test`; a smoke run of one suite (`intake` or `research-web`) against the
harness passes; `grep -rn "_runs/groom" playbooks/groom/ CLAUDE.md` returns only `_specs/`
history (DECISIONS.md).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Fixtures: retire research-web's three novelty fixtures, add requested/not-requested pair; intake fixtures gain the web-decision; path updates across all step `_fixtures/` | `playbooks/groom/*/_fixtures/**` | 2 | done |
| 6.2 | `tests.yaml` per step: assertion targets moved to `plans/{slug}/` paths and `index.md` sections; research-web asserts mechanical branching; decompose/present assert the gate model | `playbooks/groom/*/tests.yaml` | 3 | done |
| 6.3 | Stale refs: repo `CLAUDE.md` groom-playbook paragraph (flow, gates, artifact model, slug); flip the loader open-question checkbox in `_specs/index.md` | `CLAUDE.md`, `playbooks/groom/_specs/index.md` | 1 | done |

#### Task 6.1 DoD
- [x] No fixture references `_runs/` or the old slug format; retired fixtures deleted, not orphaned.

#### Task 6.2 DoD
- [x] Every suite's file assertions point at `plans/{slug}/` shapes; suites for unchanged infra untouched.

#### Task 6.3 DoD
- [x] CLAUDE.md paragraph matches the implemented shape; `_specs/index.md` Questions list has no unresolved loader item.

---

## Final Verification

- [x] `just test && just lint && just typecheck` green.
- [x] Every prompt-bearing artifact this plan touched (driving partial, 8 step prompts + bodies, preamble) passed the lesson-0004 four-check pass.
- [x] `bin/booping render-playbook groom` renders clean — no STOP/Note notices, collapsed state chart, no `_runs/` or confirm-status vocabulary anywhere in output.
- [x] Scratch-vault dry run: directory plan created by hand → `playbook-state` reports frontier, `playbook-transition` bootstraps `framing`, `_scripts` stamp plan.md + render sprints + commit.
- [x] `bin/booping render-sprints --output -` lists flat and directory plans side by side with working links.

## Out of scope

- Everything `plans/20260802-playbook-authoring-core-delegation.md` owns: `detached:` rename, framework-wide `inputs:`/`outputs:` removal, `_lib` commit, playbook-authoring move + delegation/gate teaching.
- The `/groom` skill and every other skill — untouched.
- `/develop` claiming directory plans beyond what `Plan.rel_link` fixes — if its briefing flow needs more, separate plan.
- Justfile regress/smoke selector filtering (`plans/20260801-12-02_justfile-eval-filtering`).
- Automatic sibling-stub creation on split (spec's recorded out-of-scope).

## CLAUDE.md impact

- Playbooks paragraph: groom playbook description — delegation levels, plan-as-directory artifacts, single gate, `research_agent` key (owned by task 6.3).
- Layout: no new entries (dirs already listed); `_runs/` mention in the groom bullet corrected (task 6.3).
