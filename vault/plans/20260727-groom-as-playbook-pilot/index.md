---
title: Groom-as-Playbook Pilot
type: feature
status: done
sp: 30
split_from: null
created: 2026-07-27 00:00
planned: 20260727 14:31
started: 20260727 15:21
completed: null
retro: null
goal: null
summary: Pilot playbooks as internal skill engine — dir-form steps, core scope, 
  jinja steps, shared driver, groom decomposed
commit: be1fbb3151de5968651c94a15905ae49208f291c
sessions:
- 1d9285d4-1faa-4d8c-971e-039057ad94d8
- 23ee2d99-ea09-4cec-8334-c3aa0d716a07
metrics_active_minutes: 60
metrics_models:
- claude-fable-5
metrics_tokens_input: 374
metrics_tokens_output: 270109
metrics_tokens_cache_creation: 1292370
metrics_tokens_cache_read: 17744545
---

# Groom-as-Playbook Pilot

## Context

`/groom` is today a monolithic Jinja template (`src/templates/skills/groom.md.j2`) rendered whole at skill load. Playbooks (vault-side, plain-markdown, graph-driven multi-step procedures) proved out with the user-stories playbook. This plan pilots playbooks as the *internal* engine for a plugin skill: `/groom` becomes a plugin-shipped ("core") playbook driven by the shared playbook protocol, while remaining its own skill entry (`/groom`) **and** appearing in the `/playbook` listing.

Outcome after shipping:

- `booping render-playbook groom` renders a composed groom procedure: intake → parallel research wave → design dialogue (gated) → draft → present (gated).
- `/groom` behaves as today from the user's perspective (same entry point, same lifecycle transitions, same craft) but loads context lazily per step instead of one monolithic body.
- The playbook mechanism gains four reusable capabilities: dir-form steps, a core discovery scope, opt-in Jinja step rendering, and per-step lazy rendering via `--step` (+ `--project` for out-of-project rendering).

**Success metric / kill criteria**: record rendered token count of today's `/groom` body vs the new `/groom` driver + wave-1 render. Target: material reduction (≥30%). No material drop → the pilot failed its own thesis; stop before extending the pattern to other skills.

## Decisions

- **Step = directory** (D1): a step is `<playbook>/<step>/prompt.md`, hardcoded filename. No `steps/` wrapper, no single-file form. Breaking loader change; existing global playbooks migrate in the same milestone.
- **`_`-prefix = not a step** (D2): step discovery is every non-`_` subdirectory of the playbook dir containing `prompt.md`. `_references/`, `_fixtures/` etc. are free workspace; no exclusion list. Non-`_` dir without `prompt.md` → warn + skip.
- **Only `prompt.md` is loaded** (D3): variants (`prompt.haiku-4-5.md`, …) are eval artifacts, ignored by booping. Promotion = editing frontmatter `agent:` in `prompt.md`.
- **`--step` prints body only** (D4): no section chrome — `agent:`, `review_gate:`, `Parallel with:` are driver-level facts already in the composed output, not part of the step prompt.
- **`agent:` grammar unchanged** (D5): `null` / `<model>:<effort>` / named — no versioned tiers.
- **No `--var`, no j2 target/input** (D6): run-time context (target, input) stays driver-prepended at invocation time. Eval prompt == production prompt.
- **Core discovery scope**: playbooks also discovered from `<plugin-root>/playbooks/` with scope `core`. Precedence `core < global < local` — a user can shadow the shipped groom procedure, consistent with the config tier model.
- **Jinja is opt-in per playbook**: manifest key `jinja: true` renders the preamble and step bodies through the full `Context` Jinja env (same env as `booping render`). Playbooks without the flag keep the existing plain-markdown contract untouched.
- **Jinja include paths are plugin-root-relative**: `{% include %}` / `tools.render` inside jinja playbooks resolve against `src/templates/` (and plugin root for `tools.render`), regardless of where the playbook lives. Documented explicitly in the authoring docs with an example; vault-side jinja playbooks flagged as an advanced surface. No vault-relative lookup in this pilot.
- **Driving protocol extracted to a partial**: the Execute/gate/wave-walking prose moves from `playbook.md.j2` into `_partials/_playbook_driving.j2`, included by both `/playbook` and the rewired `/groom`. One protocol, two entry points.
- **Loops via gate prose, no graph change**: the graph stays a DAG. Groom's present→revise iteration is encoded in the gate text ("on change request, re-enter the design/draft step"), enforced by the driving skill. No cycle semantics in this pilot.
- **research-web is driver-skippable, not self-skipping**: `intake` ends by declaring whether web research is warranted (a flag in its output). The driver spawns `research-web` only when flagged — no sub-agent round-trip to hear "nothing to research". Conditional lives at driver level, graph stays static.
- **Full decomposition**: all groom phases become steps, including a parallel research wave — a real test of wave parallelism, not a hybrid shell.
- **Structured facts stay in config**: transitions table, agents table, task types, sprint scale render into the preamble/steps via existing partials — nothing hardcoded into step prose.

## Architecture

Load-time flow after this plan:

```
/groom thin shell (skills/groom/SKILL.md — unchanged frontmatter)
  └─ !`booping render src/templates/skills/groom.md.j2`
       ├─ _partials/_project_context.j2
       ├─ _partials/_playbook_driving.j2   (shared with /playbook)
       └─ instructs: run `booping render-playbook groom`
            ├─ playbooks/groom/playbook.md   (jinja: true → preamble rendered w/ Context)
            │    ├─ _partials/_plan_transitions.j2
            │    ├─ _partials/_lessons.j2, _extra_instructions.j2 (skill_groom)
            │    └─ graph: intake → {research-codebase ∥ research-web} → design → draft → present
            └─ playbooks/groom/<step>/prompt.md — wave-1 embedded rendered; later waves as
                 `booping render-playbook groom --step <name>` commands (body only)
```

`Playbook.load_all` gains a third root: `(core, <plugin-root>/playbooks/)` loaded first, shadowed by global then local. `Context.assemble` already holds the plugin root (`root`) and passes it through. Step resolution moves from `steps/*.md` files to `<step>/prompt.md` directories everywhere (all scopes).

Execution order is milestone order below: the driving-partial refactor first (pure, keeps later diffs readable), then loader, then render machinery, then authoring, then rewire. The vault-side `_playbooks` eval/migration work is a separate plan (`plans/20260727-playbooks-eval-migration.md`, backlog) that slots after M3.

## Milestones

### M1: Shared driving-protocol partial — 2 SP | done

**Goal**: the wave-walking / gate / agent-spawning protocol lives in one partial included by `/playbook` (and later `/groom`). Pure refactor, no dependency on later milestones.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` output is semantically unchanged (diff review); `just build` clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Extract the Execute section (wave loop, run-time context block, agent resolution, failure stop, gate enforcement) into `_partials/_playbook_driving.j2`; `/playbook` includes it; keep Select/listing/completion in the skill | `src/templates/_partials/_playbook_driving.j2`, `src/templates/skills/playbook.md.j2` | 2 | done |

#### Task 1.1 DoD
- [x] Rendered `/playbook` body carries the same protocol content as before extraction (no lost rules).
- [x] Partial takes no skill-specific assumptions (usable from `/groom` in M5).
- [x] Partial is plan-status-agnostic: it carries only the generic hook sentence "a playbook's preamble may define resume rules for re-entering a procedure mid-run" — domain resume rules (e.g. groom's status mapping) live in that playbook's preamble, never in this partial.

---

### M2: Core scope + dir-form step loader — 6 SP | done

**Goal**: playbooks in `<plugin-root>/playbooks/` are discovered with scope `core`; step resolution is dir-form (`<step>/prompt.md`) across all scopes; existing global playbooks migrated. Must land before M4 so groom's steps are authored in the surviving shape.

**Verify**: `just test` green; `bin/booping render src/templates/skills/playbook.md.j2` lists migrated playbooks with correct scopes; `bin/booping render-playbook build-user-stories` renders clean post-migration.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `core` to the `scope` literal; extend `Playbook.load_all(vault, home_dir, plugin_root)` with a `(core, plugin_root / "playbooks")` entry **prepended to the scan tuple**. Precedence mechanics are the existing replace-on-collision loop (`by_name`: a later-scanned playbook with the same name replaces the earlier entry), so scan order core → global → local yields precedence `core < global < local`. Do not change the resolution to first-match. Pass `root` from `Context.assemble` | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/context/__init__.py` | 2 | done |
| 2.2 | Rewrite step resolution to dir form (D1/D2/D3): steps = non-`_` subdirs of the playbook dir containing `prompt.md`; step name = dir name; only `prompt.md` loaded; missing `prompt.md` → warn + skip; drop `steps/` scanning. Migrate the two existing global playbooks under `~/Claude/_playbooks/` to dir form (minimal move — deeper restructure belongs to the eval-migration plan); mechanically fix eval-suite configs whose `entry:` paths point at old `steps/*.md` locations so existing suites still run (harness rebuild per D7/D8 stays in the eval-migration plan); update `steps/` references in `CLAUDE.md` + `documentation/` | `booping-python/src/booping/context/playbook.py`, `~/Claude/_playbooks/*/`, `CLAUDE.md`, `documentation/*.md` | 3 | done |
| 2.3 | Tests: core discovery, global-shadows-core, local-shadows-global-shadows-core, dir-form step loading, `_`-dir skipped, non-`_` dir without `prompt.md` warns + skips, variant files ignored, missing root degrades silently | `booping-python/tests/context/` | 1 | done |

#### Task 2.1 DoD
- [x] `scope` accepts `core`; core scanned first, replace-on-collision preserved, so a same-name global/local playbook shadows the core one (asserted by test, not assumed).
- [x] `Context.assemble` passes the plugin root; no call site left on the old signature.
- [x] `/playbook` listing renders core playbooks (scope column shows `core`) with no template change needed.

#### Task 2.2 DoD
- [x] Loader accepts only `<step>/prompt.md`; `prompt.<anything>.md` variants and `_`-prefixed dirs invisible to booping.
- [x] Both existing global playbooks render without notices post-migration.
- [x] Existing eval suites run against the migrated layout (`entry:` paths updated; no broken references at sprint close — lesson 0005).
- [x] No `steps/` reference remains in `CLAUDE.md` or `documentation/`.

#### Task 2.3 DoD
- [x] All listed cases covered; `just test` green.

---

### M3: Opt-in Jinja rendering + `--step` + `--project` — 8 SP | done

**Goal**: a playbook with `jinja: true` renders its preamble and step bodies through the full Context Jinja env; later-wave sections point at `booping render-playbook <name> --step <step>` (body only); `--project <path>` renders against an explicit vault so `requires_project` playbooks are evaluable outside a real project.

**Verify**: `just test` green; a jinja fixture playbook renders partials in preamble and wave-1 body; `--step` prints a single rendered body with no chrome; a non-jinja playbook's output is byte-identical to before; `--project` renders a `requires_project` fixture from a bare directory.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Parse `jinja: true` manifest key into the `Playbook` model. Extend the signature to `compose(pb, plugin_root=None, context=None)`: `_run` passes the already-assembled `Context` when `pb.jinja` (and `--step` does the same); `context=None` with `pb.jinja` → in-band STOP notice. When set, build the env via the same `booping.rendering` factory `render` uses (globals `context`/`config`/`tools`, `FileSystemLoader(src/templates)`), and render preamble + embedded (wave-1) step bodies via `env.from_string(body)`. Implementation note: `from_string` templates resolve `{% include %}`/`{% import %}` through the environment's loader, so `_partials/…` keep resolving even though step bodies live outside `src/templates/` — do not add a second loader. Non-jinja path untouched | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/rendering.py` | 3 | done |
| 3.2 | Add `--step <name>` to `render-playbook`: prints exactly the step body (rendered when `jinja: true`, verbatim otherwise) — no `agent:`/`review_gate:`/`Parallel with:` chrome (D4); unknown step → stderr + exit 1. In `_playbook_step.j2`, jinja playbooks' non-embedded sections emit the `--step` command instead of the Read link | `booping-python/src/booping/commands/render_playbook.py`, `src/templates/_partials/_playbook_step.j2` | 2 | done |
| 3.3 | Add `--project <path>` to `render-playbook`: resolve context against the given vault (expose the existing `Context.assemble` vault-override path); satisfies `requires_project` | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/context/__init__.py` | 1 | done |
| 3.4 | Tests: jinja preamble/step rendering (partial include resolves), `--step` happy path + body-only assertion + unknown step, `--project` happy path + `requires_project` satisfaction, non-jinja playbook output unchanged (regression), jinja render error surfaces as in-band STOP notice | `booping-python/tests/test_render_playbook.py` | 2 | done |

#### Task 3.1 DoD
- [x] `jinja` defaults false; absent key changes nothing for existing playbooks.
- [x] Jinja env for playbook rendering is the same construction as `render` (globals: `context`, `config`, `tools`), not the bare `compose()` env; `compose` receives it via the explicit `context` parameter, no module-level state.
- [x] `{% include "_partials/…" %}` resolves from inside a step body in any scope — covered by a test rendering a jinja step from a directory outside `src/templates/`.
- [x] A Jinja error in a step/preamble produces an in-band `**STOP — tell the user:**` notice, not a traceback.

#### Task 3.2 DoD
- [x] `--step` output = step body only; byte-comparable against the source body for non-jinja playbooks.
- [x] Non-embedded sections of jinja playbooks show the `--step` command; non-jinja playbooks keep the Read link.
- [x] `.booping.log` line records `--step` invocations.

#### Task 3.3 DoD
- [x] `--project` renders a `requires_project: true` playbook with no project marker in cwd.
- [x] Without `--project`, behavior is unchanged.

#### Task 3.4 DoD
- [x] All listed cases covered; `just test` green.

---

### M4: Author the groom core playbook — 5 SP | done

**Goal**: `playbooks/groom/` exists (dir-form steps, `jinja: true`, `requires_project: true`) and `booping render-playbook groom` renders the full groom procedure with no STOP notices.

**Verify**: `bin/booping render-playbook groom` clean; rendered preamble shows transitions table, lessons, `skill_groom` extension; wave list = intake → research-codebase ∥ research-web → design → draft → present; `--step draft` renders clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `playbook.md`: manifest (`name: groom`, `jinja: true`, `requires_project: true`, trigger, graph) + preamble (mission, hard rules, what-groom-does-NOT-do, `_plan_transitions.j2` render, lessons + `skill_groom` extension via `tools.render`, **and the groom resume rule**: on invocation with an existing `in-spec`/`awaiting-plan-review` plan for the same request, map plan status to the active wave — `in-spec` = pre-present, `awaiting-plan-review` = re-enter `present`) | `playbooks/groom/playbook.md` | 2 | done |
| 4.2 | Step dirs decomposed from `groom.md.j2`: `intake/` (inline; project context, task classification partial, challenge-scope craft; output contract: **last line MUST be exactly `web-research: yes` or `web-research: no`** — driver spawns `research-web` only on `yes`), `research-codebase/` + `research-web/` (agent `booping:booping-researcher`; bounded return contracts per lesson 0007), `design/` (inline; available-agents partial, draft-design craft; `review_gate` with re-enter-on-change-request prose), `draft/` (inline; sprint planning + plan-template partials, summary rule, estimation flow, local-vault branch offer), `present/` (inline; `review_gate` = explicit approval; on approval fire `booping transition`) | `playbooks/groom/*/prompt.md` | 3 | done |

#### Task 4.1 DoD
- [x] Graph resolves to the 5-wave shape with the parallel research wave; no notices.
- [x] Preamble renders config-derived tables via partials — no hardcoded statuses, agents, or thresholds. *(Exception: the resume rule names `in-spec`/`awaiting-plan-review` literally — the plan's own Task 4.1 wording; no config key exists for groom's own statuses.)*

#### Task 4.2 DoD
- [x] Every current groom craft rule, hard rule, and user-specific instruction surface lands in exactly one step or the preamble (map recorded in the step summaries) — nothing dropped, nothing duplicated.
- [x] Researcher steps state bounded return contracts (lesson 0007).
- [x] `intake` prompt states the exact last-line flag contract (`web-research: yes|no`); groom preamble/driving prose parses that literal line, nothing looser.
- [x] Gate texts encode the revise loop (change request → re-enter design/draft).
- [x] `bin/booping render-playbook groom --step draft` renders clean.

---

### M5: A/B check, rewire `/groom`, docs cleanup — 6 SP | done

**Goal**: playbook-groom demonstrably matches old-groom quality on real briefs, then `/groom` switches to the shared protocol; all references to the old monolithic groom shape updated in the same sprint.

**Verify**: A/B diff reviewed by the user; `just build` clean, `git diff -- skills/ agents/` shows only intended drift; `bin/booping render src/templates/skills/groom.md.j2` renders driver + instructions; `just lint && just typecheck && just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | A/B check (only quality gate before groom evals exist): run old `/groom` and playbook-groom on the same 2–3 briefs; diff resulting plans on milestone count, SP spread, DoD specificity, and whether the branch offer / summary rule / explicit-approval gate all still fire. Record token counts (old body vs new driver + wave-1) against the ≥30% kill criterion. Present diff + counts to the user before proceeding | comparison notes in plan or `_references/` | 2 | done |
| 5.2 | ~~Rewrite `groom.md.j2` as driver~~ **Rescoped 2026-07-27 (kill criterion failed, user decision)**: author a NEW parallel skill `/groom-playbook` as the driver (project context + `_playbook_driving.j2` include + instruction to run `booping render-playbook groom` and walk its waves); old `/groom` untouched — switch deferred until composed-render context reduction passes the ≥30% target | `src/templates/skills/groom-playbook.md.j2`, `src/files/skills/groom-playbook/SKILL.md.j2`, `src/config.yaml`, `src/config_files.yaml` | 2 | done |
| 5.3 | Reference cleanup (lesson 0005): CLAUDE.md Playbooks bullet (dir-form steps, core scope, `jinja:`, `--step`, `--project`, `playbooks/` layout entry), CLI section, Layout section; `documentation/` playbooks page (authoring contract: dir-form, jinja flag + plugin-root-relative include paths, core scope, shadowing) — audience-scoped per lesson 0006 | `CLAUDE.md`, `documentation/*.md` | 2 | done |

#### Task 5.1 DoD
- [x] A/B run on ≥2 briefs; diff dimensions above recorded; user reviewed before rewire proceeded. *(Notes: `playbooks/groom/_references/ab-check.md`.)*
- [x] Token counts recorded; kill criterion evaluated explicitly. **Verdict: FAIL — NEW upfront +10% vs OLD (target −30%). User decision: keep old `/groom`, ship parallel `/groom-playbook` skill instead; switch deferred until composition levers (lazy wave-1, slim composed preamble) close the gap.**

#### Task 5.2 DoD *(rescoped: parallel `/groom-playbook` skill, old `/groom` untouched)*
- [x] `/groom-playbook` rendered body contains the driving protocol and the render-playbook instruction; no leftover monolithic sections; old `/groom` render byte-identical.
- [x] `skills/groom-playbook/SKILL.md` built; no other artefact drift.

#### Task 5.3 DoD
- [x] No reference anywhere in CLAUDE.md/documentation to a groom or playbook shape that no longer exists; new surfaces documented.
- [x] User docs mention only the user-facing authoring surface (lesson 0006).

---

### M6: Rendered-output reshape review — 3 SP | pending

**Goal**: user reviews the rendered artefacts (`render-playbook groom`, rendered `/groom` and `/playbook` bodies, each `--step` output) and shapes prose/IA before the plan transitions out. Sized for real iteration — a full re-author of groom prose lands its shaping here.

**Verify**: user has confirmed shaping is complete (or requested changes that were applied and re-rendered).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Pause-for-review: hand rendered outputs to the user; apply requested prose-shape edits to templates/steps; re-render and re-verify (four-check IA pass per lesson 0004); iterate until confirmed | `playbooks/groom/`, `src/templates/` | 3 | pending |

#### Task 6.1 DoD
- [ ] User explicitly confirmed the rendered shapes.
- [ ] Any edits passed the four-check IA pass (scoping, duplication, configurability, hierarchy).

---

## Final Verification

- [ ] `just build` renders cleanly; `git diff -- skills/ agents/` shows only intended changes.
- [ ] `bin/booping render src/templates/skills/groom.md.j2` and `.../playbook.md.j2` produce clean output (no `{{placeholder}}` leaks, no stale state names).
- [ ] `bin/booping render-playbook groom` and `--step <each step>` render clean with a project attached; `--project` path works from a bare dir.
- [ ] Migrated global playbooks render clean in dir form.
- [ ] `just lint && just typecheck && just test` green.
- [ ] Project-local extension points (`_booping/skill_groom.md`, `skill_playbook`) still inline correctly.
- [ ] Token-count metric recorded; kill criterion answered.

## Out of scope

- No graph cycle/loop semantics — revise loops live in gate prose.
- No cross-session playbook resume.
- No changes to other skills (`/develop`, `/retro`, `/learn`, `/chat`) or their templates.
- No changes to the user-authored playbook contract beyond dir-form steps (breaking, migrated here) and the additive `jinja:` flag.
- No conditional-branching graph semantics — the only conditional (research-web) is a driver-level skip keyed on intake's flag.
- No `--var` / template variables in step bodies (D6) — run-time context stays driver-prepended.
- Eval infrastructure (`_playbooks` migration, smoke/regress split, prompt loader, fixtures, groom eval suite) — separate plan `plans/20260727-playbooks-eval-migration.md`, slots after M3.

## CLAUDE.md impact

Owned by Task 5.3: Playbooks section (dir-form steps, core scope, `jinja:`, precedence, `playbooks/` root, `--step`/`--project`), Layout (new `playbooks/` entry), CLI section, and Task 2.2 for the immediate `steps/` reference fixes landing with the loader change.

## Risk register

- Jinja env inside `compose()` may need care around `LenientUndefined` vs strict errors — Task 3.1 DoD pins error handling to in-band STOP notices.
- Decomposition may lose groom nuance — Task 4.2 DoD requires a one-to-one mapping audit.
- Driving protocol via partial in two skills risks divergence later — single partial is the mitigation; no copies.
- `--step` is a Bash reflex, not a Read reflex: the model may skip lazy loads and improvise from the summary line. Detection = the M5 A/B diff (missing craft behaviors betray unloaded steps).
- Gate → session boundary: resuming a groom mid-procedure means re-locating the active wave. Addressed via an explicit injection boundary: the shared `_playbook_driving.j2` stays status-agnostic (generic "preamble may define resume rules" hook, Task 1.1), and groom's status→wave mapping lives in its own preamble (Task 4.1). Cross-validation flagged the coupling risk; this is the resolution, not a deferral.
- Success metric may not materialize: if rendered-context reduction < 30%, the pilot failed its thesis — evaluate at Task 5.1 before the rewire, not after.
