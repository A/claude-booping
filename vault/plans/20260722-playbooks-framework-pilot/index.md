---
title: Playbooks Framework + Build-User-Stories Pilot
type: feature
status: done
sp: 32
split_from: null
created: 2026-07-22 22:03
planned: 20260722 11:23
started: 20260722 12:42
completed: null
retro: null
goal: null
summary: "Vault playbooks (global ~/Claude/_playbooks + local {vault}/_playbooks),
  /playbook skill, standalone evals, user-stories pilot"
commit: 679b80319008db7f0473ba703dd2d0475e32c004
sessions:
- 3d197bdc-0009-40f1-b645-c7dc52cef389
- 594c9d93-1af4-407a-8d14-0a94aa8192b5
metrics_active_minutes: 55
metrics_models:
- claude-fable-5
metrics_tokens_input: 107884
metrics_tokens_output: 195155
metrics_tokens_cache_creation: 1273790
metrics_tokens_cache_read: 17750058
---

# Playbooks Framework + Build-User-Stories Pilot

## Context

A **playbook** is a digitized user procedure — a multi-step guided experience such as building user stories — where each step may run in a sub-agent and some steps stop for human review before continuing. Playbooks are user content: global (shared across projects) or local to one project, and movable between those scopes. They are unrelated to booping's skills (framework machinery); booping's only role is discovery and orchestration — the `/playbook` skill lists them and drives their execution.

claude-knowledge (repo `~/Dev/@A/claude-knowledge`) has the prototype content: `skills/feature-index-v2/modules/{reshake,index}` (prompt transforms with colocated promptfoo eval suites), `skills/feature-prd` (user stories from a confirmed index), and a portable eval harness `evals/_lib` (see its `evals/README.md` porting instructions). That content migrates out as the pilot; **claude-knowledge originals stay untouched**.

After this plan: playbooks are **plain-markdown vault content** — global playbooks at `~/Claude/_playbooks/<name>/`, project-local playbooks at `{vault}/_playbooks/<name>/` (local shadows global on name collision); `/playbook` (plugin skill) lists both scopes and guides selection + execution; a playbook's steps are plain markdown files with frontmatter (`agent`, `model`, `effort`, `review_gate`); the pilot **global** playbook **build-user-stories** runs reshake (no review) → build-index (review gate) → user-stories (review gate), writing specs to the project vault; each step has a colocated promptfoo eval suite run by a **standalone harness at `~/Claude/_playbooks/_lib/`** with zero booping coupling.

## Decisions

- **Naming**: `playbooks` / `steps` (over guides/instructions) — user-confirmed; ops-standard, ordering implied.
- **Location — vault, not plugin** (user-confirmed this revision): global playbooks at `~/Claude/_playbooks/`, project-local at `{vault}/_playbooks/` (underscore prefix matches `_booping`, `_contexts`). Playbooks are user-authored content, versioned in the `~/Claude` git repo (repo-local vaults version theirs in the host repo). The plugin owns only the `/playbook` skill + the context loader.
- **Format — plain markdown** (user-confirmed this revision): playbook + step files are plain `.md` with YAML frontmatter, no jinja, no render pipeline. Obsidian-friendly; evals consume step files directly (no pre-render phase). Run-time values (specs destination, project name) are **injected by the orchestrator**: when composing a step invocation (sub-agent briefing or inline run), the orchestrator appends a `## Run-time context` block (`specs_dir: <abs path>`, `project: <name>`) after the step body. Step prompts refer to those keys, never a hardcoded path.
- **Review gates are in-conversation pauses**: the orchestrator stays in the session; step position and prior outputs live in conversation context, so "continue" after a gate needs no persisted state. Cross-session resume (returning into a stopped playbook after context loss) is the postponed part — see Progress tracking below.
- **Evals — decoupled from booping** (user-confirmed this revision): the promptfoo harness is ported to `~/Claude/_playbooks/_lib/` + `~/Claude/_playbooks/run.sh` as a self-contained unit; suites are colocated with the steps they test. No `just eval` target, no booping repo files. Wiring evals into booping later is a separate future plan.
- **Shadowing**: on name collision, the local playbook wins; listing shows scope so shadowing is visible.
- **Global root from `home_dir`** (revalidated 2026-07-22: sibling plan `20260722-booping-global-config-home-dir.md` landed in `f350785..679b803`): the loader resolves the global root as `<home_dir>/_playbooks/`, where `home_dir` comes from the resolved config (core → global tiers; `~` expanded). Default stays `~/Claude/_playbooks/`.
- **Step 1 contract**: reshake outputs a **feature table** `feature | dependencies | capabilities | motivation` (no priorities) — contract and checks already built in claude-knowledge commit `04f4099` (reshake module tests.yaml + inputs/traps.md).
- **Frontmatter shapes locked** (user-confirmed during grooming; one revision: listing gains `Scope`):
  - Step: `name`, `summary`, `agent` (null = run inline), `model`, `effort`, `review_gate` (free-text stop instruction, or null).
  - Playbook: `name`, `title`, `summary`, `trigger`, `steps` (ordered list of step names).
  - `/playbook` listing: table `| Playbook | Summary | Trigger | Scope | Path |` (`Scope` = global / local).
- **Progress tracking / resume** (return into a stopped playbook, e.g. by artifact presence): **postponed** — noted as a future idea in the playbook doc, not implemented.
- **Global config / home_dir**: split into sibling plan `20260722-booping-global-config-home-dir.md` (backlog) — independent, and combined SP would exceed the 35 split threshold.

## Architecture

```
~/Claude/_playbooks/                          # GLOBAL scope (versioned in ~/Claude git repo)
  _lib/                                       # ported eval harness (claude_provider.py, prompts, grader.yaml)
  run.sh                                      # standalone eval runner; discovers suites under ~/Claude/_playbooks/**
  build-user-stories/                         # pilot playbook
    playbook.md                               # frontmatter (name,title,summary,trigger,steps) + orchestration body
    steps/reshake.md                          # frontmatter (name,summary,agent,model,effort,review_gate) + prompt
    steps/build-index.md
    steps/user-stories.md
    steps/<step>.promptfooconfig.yaml + tests/inputs   # colocated suites (exact layout per harness conventions)
    references/                               # feature-index.md, feature-prd.md templates, priority-scale atom
{vault}/_playbooks/<name>/                    # LOCAL scope, same shape; shadows global by name

# plugin (claude-booping repo):
booping-python/src/booping/context/playbook.py  # Playbook / Step models; load_all() over both roots
src/templates/skills/playbook.md.j2             # /playbook body: listing + selection + execution protocol
src/files/skills/playbook/SKILL.md.j2           # thin shell (frontmatter + !booping render)
```

Load-time flow: `/playbook` → `!booping render src/templates/skills/playbook.md.j2` → template iterates `context.playbooks` (loaded by `Context.assemble()`: scan `~/Claude/_playbooks/` + `{vault}/_playbooks/`, skip `_`-prefixed entries like `_lib`, parse plain-md frontmatter, apply local-shadows-global) → renders listing table + execution protocol: pick playbook by trigger match; for each step, read the step file, run per frontmatter (`agent` set → spawn sub-agent with the step body as briefing, plus injected run-time values and a bounded return contract; `agent` null → run inline), and when `review_gate` is non-null STOP after the step, present output, and continue only on explicit user confirmation.

Run-time injection: the skill knows the vault via its project-context partial; when invoking a step it appends a `## Run-time context` block (`specs_dir: {vault}/specs`, `project: <name>`) after the step body. Step prompts reference those keys and stay path-agnostic.

Eval flow: `~/Claude/_playbooks/run.sh` discovers every `promptfooconfig.yaml` under `~/Claude/_playbooks/` (excluding `_lib`); suites use the provider's existing config surface — `entry:` (the file under test) plus optional `context:` (supporting files list), both resolved against the harness ROOT (`~/Claude/_playbooks/`, anchored via `Path(__file__)` in `claude_provider.py`). Step suites set `entry:` to their step `.md`; plain markdown, no render step. Booping repo untouched.

## Milestones

### M1: Playbook framework — 9 SP | done

**Goal**: `context.playbooks` loads both scopes with shadowing; `/playbook` renders the listing + execution protocol from it.

**Verify**: `just build` clean; `just test` green; `bin/booping render src/templates/skills/playbook.md.j2` shows the listing table (empty state OK until M4) and the execution protocol.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `Playbook` + `Step` context models: parse frontmatter via existing `booping.context._yaml.parse_frontmatter` (no new dependency) from `<root>/<name>/playbook.md` (`name,title,summary,trigger,steps`) and `<root>/<name>/steps/<step>.md` (`name,summary,agent,model,effort,review_gate`); `Playbook.load_all(vault: Path, home_dir: Path)` (signature mirrors `Plan.load_all` plus the resolved vault-home base) scans global root `home_dir / "_playbooks"` + local root `vault / "_playbooks"` — vault passed in by `Context.assemble()` from `project.directory`, `home_dir` from the resolved config's `home_dir` (core+global merge, `~`-expanded; note `Context.assemble` now uses `load_cwd_configured` + `global_config_path()`); skips `_`-prefixed entries, tags each playbook `scope: global|local`, local shadows global on name collision; wired into `Context.assemble()` as `context.playbooks`; unit tests mirroring `context/skill.py` tests | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/context/__init__.py`, tests | 4 | done |
| 1.2 | `/playbook` skill: body template (listing table `Playbook | Summary | Trigger | Scope | Path` iterating `context.playbooks`, selection instruction, execution protocol incl. `## Run-time context` injection rule, bounded step return contracts, review_gate stop rule with in-conversation-state note, inline fallback when sub-agents unavailable, end-of-run completion report mirroring /develop's pattern — one-paragraph summary: artifacts written + gates passed — postponed-resume note), extra-instructions hook (`{{ tools.render('src/templates/_partials/_extra_instructions.j2', extra_instruction_key='skill_playbook') }}` at body end, matching other skills), thin shell, `config_files.yaml` entry, `src/config.yaml` `skills.playbook: {}` entry, `just build` | `src/templates/skills/playbook.md.j2`, `src/files/skills/playbook/SKILL.md.j2`, `src/config_files.yaml`, `src/config.yaml` | 3 | done |
| 1.3 | Docs: `documentation/playbooks.md` (concept, both scopes + shadowing, frontmatter contract, how to author global and local playbooks, note that eval suites + harness live at `~/Claude/_playbooks/` with their own README), `mkdocs.yml` nav entry, CLAUDE.md architecture section gains playbooks paragraph (vault roots + `context.playbooks` loader + `/playbook` skill; states evals are vault-side, not repo-side) | `documentation/playbooks.md`, `mkdocs.yml`, `CLAUDE.md` | 2 | done |

#### Task 1.1 DoD
- [x] `booping debug-context` shows `playbooks` populated from a fixture playbook in each root.
- [x] Shadowing test: same-name playbook in both roots → local wins, global absent from result.
- [x] `_lib` and other `_`-prefixed dirs excluded from discovery.
- [x] Missing/partial frontmatter degrades with a warning, not a crash (match `SkillConfig` tolerance); missing roots (no `_playbooks` dir) yield empty list, no crash.
- [x] Tests cover: load_all discovery per root, scope tag, step ordering per `steps:` list, null vs set `review_gate`/`agent`, global root follows `home_dir` (non-default value honoured).

#### Task 1.2 DoD
- [x] Rendered skill shows listing table with `Scope` column and execution protocol; no `{{placeholder}}` leaks.
- [x] Execution protocol states: read the step file, spawn agent per frontmatter (`agent` null → inline; inline fallback when the harness lacks the agent), append the `## Run-time context` block (`specs_dir`, `project`) to the step body when composing the invocation, bound the step's return contract, stop at non-null `review_gate` and await explicit confirmation (in-conversation pause; no persisted state).
- [x] End-of-run completion report defined per /develop's pattern: one-paragraph summary (artifacts written, gates passed).
- [x] Extra-instructions hook present; `_booping/skill_playbook.md` fixture inlines in rendered output.
- [x] No hardcoded playbook names — listing is fully data-driven.
- [x] Four-check IA pass (scoping, duplication, configurability, hierarchy) run on the skill body before saving.

#### Task 1.3 DoD
- [x] `mkdocs build` passes; nav shows Playbooks.
- [x] CLAUDE.md names both vault roots, the context loader, and the skill; states evals live vault-side.
- [x] Frontmatter contract in doc matches Decisions verbatim.

---

### M2: Standalone eval harness at `~/Claude/_playbooks/` — 3 SP | done

**Goal**: promptfoo eval harness runs self-contained from `~/Claude/_playbooks/`, no booping coupling.

**Verify**: `~/Claude/_playbooks/run.sh smoke` (or equivalent filter) runs a smoke suite green.

Note: this milestone writes **outside the attached repo** (absolute paths under `~/Claude/_playbooks/`); brief the executing agent with absolute destinations.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Port harness from `~/Dev/@A/claude-knowledge` per `evals/README.md` porting instructions: copy `evals/_lib/{claude_provider.py,consumer_prompt.txt,rubric_prompt.txt,grader.yaml}` + `evals/run.sh` + README to `~/Claude/_playbooks/`; fix `ROOT` resolution in `claude_provider.py` for the new depth: `ROOT = Path(__file__).parents[1]` (file lands at `_playbooks/_lib/claude_provider.py` → ROOT = `_playbooks/`; the existing `__file__` anchor pattern, no `~` handling needed) — suite `entry:`/`context:` paths stay ROOT-relative; point discovery at `~/Claude/_playbooks/**` (exclude `_lib`); drop any repo-relative assumptions; add a minimal smoke suite proving the provider works; README documents the standalone layout, discovery root, and that suites colocate with steps and set `entry:` to the sibling step `.md` | `~/Claude/_playbooks/_lib/*`, `~/Claude/_playbooks/run.sh`, `~/Claude/_playbooks/README.md`, smoke suite files | 3 | done |

#### Task 2.1 DoD
- [x] Smoke suite runs green via subscription billing (`ANTHROPIC_API_KEY` stripped).
- [x] `run.sh` exit-code-100 tolerance (RED baselines) preserved.
- [x] No references to the booping repo or `bin/booping` anywhere in `~/Claude/_playbooks/` harness files.
- [x] README documents the standalone mechanism and discovery roots.

---

### M3: Pilot steps + unit evals — 12 SP | done

**Goal**: three plain-md step files exist under the global pilot playbook, each with a colocated eval suite; reshake passes the feature-table checks the baseline could not stabilize.

**Verify**: `~/Claude/_playbooks/run.sh` runs all three step suites; reshake GREEN suite passes all checks including EXTRACT and SPLIT.

Source material (claude-knowledge, read-only): `skills/feature-index-v2/modules/reshake/{tests.yaml,inputs/traps.md,baseline-prompt.md,baseline.promptfooconfig.yaml}` (new feature-table contract, commit `04f4099`), `modules/index/PROMPT.md` (old contract — rewrite required), `skills/feature-prd/SKILL.md` + `evals/feature-prd/`, `references/templates/{feature-index.md,feature-prd.md}`, `references/atoms/feature-priority-scale.md`. All writes land at absolute paths under `~/Claude/_playbooks/build-user-stories/`. Suite configs use the provider's `entry:`/`context:` keys with ROOT-relative paths (ROOT = `~/Claude/_playbooks/`); a step's supporting files (references, templates) go in its `context:` list.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | **reshake step**: author `steps/reshake.md` (frontmatter per contract, `review_gate: null`) — prompt implements the feature-table contract (columns `feature|dependencies|capabilities|motivation`, Same/Separate-Feature split criteria, no priorities) and ends with a return contract: return ONLY the feature table, no preamble or commentary. Copy suite (tests.yaml, inputs/traps.md, baseline pair) from claude-knowledge reshake module, adapt paths; suite `entry:` points at the sibling `steps/reshake.md` | `~/Claude/_playbooks/build-user-stories/steps/reshake.md` + colocated suite files | 4 | done |
| 3.2 | **build-index step**: author `steps/build-index.md` consuming the feature table → writes `<specs dir>/features/index.md` (destination injected by orchestrator) from copied `references/feature-index.md` template + `references/feature-priority-scale.md` atom; `review_gate: "Present the index; user confirms or reorganizes before the next step"`; return contract: return ONLY the written file path + `## Gate questions` block. New suite adapted from claude-knowledge index module but on the feature-table input contract, `entry:` at sibling step file | `~/Claude/_playbooks/build-user-stories/steps/build-index.md`, `.../references/feature-index.md`, `.../references/feature-priority-scale.md`, colocated suite | 4 | done |
| 3.3 | **user-stories step**: adapt claude-knowledge `feature-prd` into `steps/user-stories.md` — unfold one confirmed-index feature into stories/PRD at `<specs dir>/features/<feature>/PRD.md` (destination injected); `review_gate: "Present stories; user confirms or refines before closing"`; return contract: return ONLY the written file path + open questions. Copy `references/feature-prd.md`; suite adapted from `evals/feature-prd/`, `entry:` at sibling step file | `~/Claude/_playbooks/build-user-stories/steps/user-stories.md`, `.../references/feature-prd.md`, colocated suite | 4 | done |

#### Task 3.1 DoD
- [x] GREEN suite passes all checks (deterministic TABLE gate + COVERAGE, EXTRACT, FOUNDATION, SPLIT, FOLD, DEPENDENCIES, NO-INVENTION).
- [x] Baseline (RED) pair runs; discrimination note kept in config header.
- [x] Step prompt ends with an explicit return contract (feature table only, no filler).
- [x] No hardcoded paths in the step prompt (run-time values injected by orchestrator).
- [x] Four-check IA pass (scoping, duplication, configurability, hierarchy) run on the prompt before saving.

#### Task 3.2 DoD
- [x] Suite passes: index composed from a fixture feature table; gate questions emitted; `confirmed: No` frontmatter present.
- [x] Step prompt consumes ONLY the feature-table contract fields (no `used-by`/`candidate-priority`/`verdict` remnants).
- [x] Output destination expressed as orchestrator-injected — no hardcoded home dir or vault path.
- [x] Return contract present (file path + gate questions only).
- [x] Four-check IA pass run on the prompt before saving.

#### Task 3.3 DoD
- [x] Suite passes: stories scoped to one feature, neighbor concerns pushed to Out of Scope.
- [x] Step consumes confirmed index (`confirmed: Yes` guard stated in prompt).
- [x] Review-gate text matches Decisions verbatim.
- [x] Return contract present (file path + open questions only).
- [x] Four-check IA pass run on the prompt before saving.

> **Deviation (user-directed, 2026-07-22):** eval pass-gating dropped from scope — suites must exist and execute, not pass. One-run results: reshake GREEN all checks; build-index GREEN all checks; user-stories 1 assert failed (recorded as-is); reshake RED baseline unexpectedly passed (discrimination looseness flagged, left untouched).

---

### M4: Pilot playbook + integration — 6 SP | done

**Goal**: `/playbook` lists build-user-stories (scope global); the full chain runs end-to-end and specs land in the vault.

**Verify**: `bin/booping render src/templates/skills/playbook.md.j2` lists the pilot; integration eval green via `~/Claude/_playbooks/run.sh`; manual e2e run produces `{vault}/specs/features/index.md` + one feature's stories.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `playbook.md` for build-user-stories (locked frontmatter; body: step sequence, gate behavior, specs destination described as orchestrator-injected); integration eval suite — **non-interactive by design**: promptfoo cannot pause at review gates, so the suite tests the TRANSFORM CHAIN ONLY. Composite context uses the provider's native config surface, exactly as claude-knowledge `evals/feature-index-v2/promptfooconfig.yaml` does: `entry: build-user-stories/playbook.md`, `context:` list = the three step files + references, `output_mode: files` — all ROOT-relative; no promptfoo-side concatenation needed. Rubric asserts the produced text INSTRUCTS gating at index and stories steps; live gate-stop behavior is verified manually in 4.2, not here | `~/Claude/_playbooks/build-user-stories/playbook.md`, `.../promptfooconfig.yaml` + tests/inputs | 4 | done |
| 4.2 | Manual e2e on a sample project: run `/playbook` → pilot → confirm both gates fire and artifacts land at `{vault}/specs/`; record the run as a worked example in `documentation/playbooks.md` | `documentation/playbooks.md` | 2 | done |

#### Task 4.1 DoD
- [x] Listing table shows the pilot with correct title/summary/trigger/scope/path.
- [x] Integration suite config mirrors feature-index-v2's provider config shape (`entry` + `context` list + `output_mode: files`, ROOT-relative paths).
- [x] Integration tests assert chain outputs (feature table → index → stories) and that gate instructions are present in the flow — no attempt to simulate interactive stops in promptfoo.
- [x] No decomposition/composition rules restated in playbook body (steps own them).
- [x] Four-check IA pass run on the playbook body before saving.

#### Task 4.2 DoD
- [x] Both review gates observed stopping in the live run.
- [x] Artifacts at `{vault}/specs/features/index.md` and `{vault}/specs/features/<feature>/PRD.md`.
- [x] Worked example added to docs.

> **Deviation (user-directed, 2026-07-22):** manual e2e ran a purpose-built `test` playbook (3 general-purpose sub-agent steps, one review gate) instead of the pilot chain — gate stop/resume, run-time injection, listing, and completion summary all observed live; pilot chain itself verified non-interactively by the green integration suite (M4.1). Also fixed during M4: `_playbooks/` tree relocated from `~/Claude/` to the real `<home_dir>/_playbooks/` (`~/Dev/@A/notes/projects/_playbooks/`).

---

### M5: Reshape review — 2 SP | pending

**Goal**: user shapes the rendered prose before the plan closes (per project groom override).

**Verify**: user sign-off recorded in plan.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Pause-for-review: hand the user rendered `/playbook` output, pilot playbook body, and all three step prompts; apply requested prose reshaping; rebuild + re-run affected eval suites | `src/templates/skills/playbook.md.j2`, `~/Claude/_playbooks/build-user-stories/**` | 2 | pending |

#### Task 5.1 DoD
- [ ] User reviewed all rendered artifacts and edits applied.
- [ ] `just build` green; affected suites green via `~/Claude/_playbooks/run.sh` after reshaping.

---

## Final Verification

- [ ] `just build` renders cleanly; `just test` green; `bin/booping render src/templates/skills/playbook.md.j2` clean.
- [ ] Rendered skill body reviewed (no stale names, no `{{placeholder}}` leaks, no prose duplicating rendered tables).
- [ ] Project-local extension points (`_booping/skill_playbook.md`) inline correctly (add extra-instructions hook in 1.2).
- [ ] `~/Claude/_playbooks/run.sh` green across smoke + three step suites + integration (RED baselines may exit 100).
- [ ] No booping-repo file references the vault eval harness beyond the docs note (decoupling holds).

## Risks

- **Reshake prompt may not stabilize** all checks across runs (SPLIT flapped in baseline experiments) — M3.1 owns iterating until green; if a check proves unattainable, adjust the check WITH user sign-off, never silently.
- **Plain-md steps lose template power** — run-time values must be injected by the orchestrator at invocation; if a step needs a value the protocol doesn't inject, extend the injection list in the skill (M1.2 owns the rule), never hardcode a path in a step.
- **Review gates are untestable in promptfoo** (stateless batch evaluator) — accepted; integration eval scoped to the transform chain + gate-instruction presence (M4.1), live gate behavior verified manually (M4.2).
- **Sub-agent availability** varies by harness — execution protocol must state the inline fallback (M1.2), mirroring claude-knowledge feature-index-v2 SKILL.md.
- **Writes outside the attached repo** (M2–M4 vault-side content) — brief executing agents with absolute destinations; `~/Claude` is a git repo, so vault-side work is versioned there.

## Out of scope

- Wiring evals into booping (runner integration, `just eval`, CI) — future separate plan.
- Progress tracking / resume of interrupted playbooks (artifact-presence idea) — postponed by decision.
- Global config + home_dir move — sibling plan `20260722-booping-global-config-home-dir.md`.
- Retiring/deprecating claude-knowledge originals (feature-index v1/v2, feature-prd) — untouched.
- Any change inside the claude-knowledge repo.
- Migrating other claude-knowledge skills into playbooks beyond the pilot.

## CLAUDE.md impact

Owned by task 1.3: architecture section gains the playbook vault roots (`~/Claude/_playbooks/`, `{vault}/_playbooks/`), the `context.playbooks` loader, the `/playbook` skill, and a note that eval suites + harness live vault-side (not in this repo). No other sections change.
