---
status: done
title: Flat lessons dir with targets frontmatter
type: feature
plan_status: ready-for-dev
sp: 41
split_from: null
created: 2026-08-03 11:29
planned: null
started: 20260803 07:28
completed: 2026-08-03 08:53
retro: null
goal: null
summary: "Targeted lessons in flat _lessons/ roots (global+vault) with targets: routing
  to playbooks/steps/agents; legacy wiring retired"
commit: 89498f749b71dae4406bde83be24d1a2f6672709
agents:
  research-codebase: a0d42de1157784f84
  research-web: a88fa5ac61083084a
  cross-review: a5c5731b5d7e2b370
reviewed_at: 20260803 07:28
sessions:
- a3729414-c4fc-4408-980f-9dc1c77e4e17
- f53857a4-fcae-44c5-a018-0a92cf9d8e0c
metrics_active_minutes: 85
metrics_models:
- claude-fable-5
- claude-opus-5
metrics_tokens_input: 555
metrics_tokens_output: 294984
metrics_tokens_cache_creation: 1625975
metrics_tokens_cache_read: 33114992
---

# Flat lessons dir with targets frontmatter

## Framing

See [request](request.md) for the full framing brief.

## Context

Lesson scope is currently encoded by location, twice over: vault `lessons/` reaches legacy skills wholesale via `_lessons.j2`, and playbook lessons live in four `_lessons/` directory scopes (per discovery root + per playbook) narrowed by a `step:` frontmatter key — the same rule wanted in two places means two files, which is where the tree stands today (0004–0007 duplicated into `_playbooks/groom/_lessons/`).

After this plan: one flat lesson shape in exactly two roots — `{home_dir}/_lessons/` (global) and `{vault}/_lessons/` (project) — where each lesson carries a `targets:` frontmatter list naming the playbooks, playbook steps, and internal agents it binds to. `booping render-playbook` injects matching lessons at the harness level (no author wiring), internal agent bodies inject `agent:`-targeted lessons at load time, and the learn playbook writes only this shape, choosing targets against a rendered target-space table of every playbook. The old playbook `_lessons/` scopes and the `step:` key are removed; legacy structures produce a migration notice and are otherwise skipped. Legacy skills and vault `lessons/` stay untouched.

## Decisions

- **Roots**: exactly two — `{home_dir}/_lessons/` (global) and `{vault}/_lessons/` (project); project shadows global by filename. No core root, no per-playbook dirs, no playbook-root-level dirs.
- **`targets:` vocabulary**: YAML list (a bare scalar string normalizes to a one-entry list at parse time); entry forms `{playbook}` (e.g. `groom`), `{playbook}/{step}` (e.g. `groom/draft-plan`), `agent:{id}` (e.g. `agent:booping-developer`). Exact names only — no globs, no negation, no wildcards. Skills are not expressible by construction.
- **Opt-in semantics**: a lesson in a new root with a missing/empty `targets:` or a malformed entry is not injected anywhere and produces a non-blocking Note (Copilot `applyTo` model — absent means never auto-applied).
- **Injection is harness-level**: `render-playbook` composes lesson sections itself, for plain and `jinja: true` playbooks alike — playbook authors never include a lessons partial. Presentation stays overridable by shadowing `_playbook_lessons.j2` through the existing loader chain.
- **System B removed now**: the four playbook `_lessons/` scopes and the `step:` key die in this plan — not parallel deprecation. Legacy content is skipped with a migration notice.
- **Legacy skills untouched**: vault `lessons/`, `_lessons.j2`, and every `src/templates/skills/*.j2` body keep working unchanged; shared partials the old `/learn` skill renders (`_learn_targets.j2`, `_lesson_template.j2`) are shadowed playbook-locally, never edited.
- **Agent reach**: internal booping-rendered agents only (`booping-developer`, `booping-researcher`); only targeted lessons enter agent bodies. External/global agents are out of reach v1.
- **Learn playbook routes against the full target space**: a render-time table of every playbook (steps + summaries + existing targeted lessons + per-playbook agent roster) built from `context.playbooks` and config — the model narrows to affected playbooks and picks exact targets at run time.
- **Unknown-target handling**: `{playbook}/{step}` whose step is unknown → non-blocking Note on that playbook's render (successor of `orphan_lesson`). A target naming a playbook that does not exist is silent (may exist in another project's roots); `agent:` ids are not validated at render time.

## Architecture

`Lesson` (`booping-python/src/booping/context/lesson.py`) gains `targets: list[str]` parsed from frontmatter plus a class-level target-entry validator (three exact forms above). A new loader `Lesson.load_targeted(home_dir, vault)` merges the two `_lessons/` roots most-specific-wins by filename (same mechanics as `_merge_lessons`) and lands on `Context.targeted_lessons`, assembled in `Context.assemble` beside the legacy `context.lessons`.

`render-playbook` (`booping-python/src/booping/commands/render_playbook.py`) stops reading `Playbook.lessons` from `_lessons/` dirs (that discovery is deleted from `playbook.py`) and instead filters `context.targeted_lessons` per render: entries targeting `{name}` feed the composed `## Lessons` section, entries targeting `{name}/{step}` feed that step's `--step`/inline surface, both through the unchanged `_playbook_lessons.j2` formatter and both suppressed by `--no-lessons`. Two new non-blocking notices join the render: `legacy_lessons` (any populated legacy dir) and `untargeted_lesson` (opt-in violation).

Internal agent templates (`src/templates/agents/booping-researcher.md.j2`, `_partials/_developer_body.j2`) include a new `_agent_lessons.j2` partial that renders `agent:{id}`-targeted lessons into the agent body at load time — same pattern as `_extra_instructions.j2`.

The learn playbook's routing surface is a new core partial `playbooks/_partials/lesson_target_space.md` (playbook-domain knowledge lives under `playbooks/`), rendered inside learn's step bodies via the Jinja context env. Consumers: `booping render-playbook learn` (steps `extract-candidates`, `review-table`, `write`), the internal agent shells at load time, and `just playbook-reports`.

## Milestones

### M1: Lesson model + targeted discovery — 7 SP | done

**Goal**: `Context.targeted_lessons` holds validated, shadow-merged lessons from the two `_lessons/` roots.

**Verify**: `cd booping-python && uv run pytest tests/context/ -q` green; `bin/booping debug-context | grep -A5 targeted_lessons` shows lessons from a scratch vault `_lessons/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `targets: list[str]` to `Lesson`, parsed from frontmatter; add `parse_target(entry)` classifying the three entry forms (`playbook`, `playbook/step`, `agent:id`) and rejecting anything else | `booping-python/src/booping/context/lesson.py` | 2 | done |
| 1.2 | Add `Lesson.load_targeted(home_dir, vault)`: read `{home_dir}/_lessons/` then `{vault}/_lessons/`, filename-sorted, project shadowing global by filename; wire result onto `Context.targeted_lessons` in `Context.assemble` (empty list when no roots exist; global root still read with no vault attached) | `booping-python/src/booping/context/lesson.py`, `booping-python/src/booping/context/__init__.py` | 3 | done |
| 1.3 | Tests: targets parsing (three forms, malformed entries), two-root shadowing, missing dirs, assemble wiring with/without vault | `booping-python/tests/context/lesson_test.py`, `booping-python/tests/context/assemble_test.py` | 2 | done |

#### Task 1.1 DoD

- [x] `Lesson` exposes `targets` (default `[]`) read from frontmatter list or scalar string.
- [x] `parse_target` returns a typed result (playbook / step / agent + names) for the three legal forms and a rejection for anything else.
- [x] Legacy loaders (`load_dir`, `load_all`) behave byte-identically for lessons without `targets:`.

#### Task 1.2 DoD

- [x] `load_targeted` returns the union of both roots — a global-only lesson is included; a same-filename pair keeps only the project copy — output filename-sorted.
- [x] `Context.targeted_lessons` populated when either root exists; `[]` when neither does; global-only works without an attached project.
- [x] `debug-context` output includes `targeted_lessons`.

#### Task 1.3 DoD

- [x] Every DoD bullet of 1.1/1.2 has a test invoking the loader and diffing observed fields.
- [x] A malformed-entry lesson appears in `targeted_lessons` with its rejection recorded (consumed by M2's notice), not dropped silently at load.

---

### M2: render-playbook injection swap + legacy retirement — 11 SP | done

**Goal**: `render-playbook` injects only targeted lessons, on both surfaces; `_lessons/` dir discovery and the `step:` key are gone; legacy structures produce a migration notice.

**Verify**: `cd booping-python && uv run pytest tests/ -q` green; `bin/booping render-playbook groom --project playbooks/_fixtures/vault --set now=19700101-00-00` renders no `## Lessons` (fixture has none), and the same render against a scratch vault with `_lessons/0001_x.md` (`targets: [groom/draft-plan]`) appends the lesson only to `--step draft-plan` output.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Filter `context.targeted_lessons` per render: playbook-name targets → composed `## Lessons`; `{name}/{step}` targets → that step's `--step` and inline surfaces; `--no-lessons` suppresses both; `_playbook_lessons.j2` signature unchanged | `booping-python/src/booping/commands/render_playbook.py` | 3 | done |
| 2.2 | Delete system-B discovery: `_merge_lessons` / `_attach_lessons` / `_ROOT_LESSON_SCOPES` and the `orphan_lesson` problem (`playbook.py:273-308`), the `Playbook.lessons` field (`playbook.py:187`) and its population in `load_all` (`playbook.py:257-268`), `step:`/`scope:` reading in `load_dir` (`lesson.py:20-38`); replace with an `unknown_step_target` non-blocking Note raised at render for `{name}/{step}` targets whose step is not in the graph | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/context/lesson.py`, `booping-python/src/booping/commands/render_playbook.py` | 3 | done |
| 2.3 | Migration + opt-in notices: `legacy_lessons` Note when vault `lessons/` is non-empty or any `_playbooks/**/_lessons/` dir at any discovery root has content (listing the paths, stating playbooks no longer read them); `untargeted_lesson` Note per new-root lesson with missing/empty/malformed `targets:` | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/context/playbook.py` | 2 | done |
| 2.4 | Rewrite lesson-related tests: render_playbook lesson suites target the new filtering (composed/step/inline/`--no-lessons`/notices), playbook_test drops union/scope/orphan cases, lesson-format lock tests keep passing unchanged | `booping-python/tests/test_render_playbook.py`, `booping-python/tests/context/playbook_test.py` | 3 | done |

#### Task 2.1 DoD

- [x] A `targets: [groom]` lesson renders in `render-playbook groom` composed `## Lessons` and in no step output.
- [x] A `targets: [groom/draft-plan]` lesson renders in `--step draft-plan` output and in inline-mode `draft-plan` section, absent from the composed section and other steps.
- [x] A lesson targeting another playbook renders nowhere in this playbook's output.
- [x] `--no-lessons` output is byte-identical to a no-lessons vault render.

#### Task 2.2 DoD

- [x] `grep -rn "_attach_lessons\|_merge_lessons\|orphan_lesson" booping-python/src/` returns nothing.
- [x] A `_playbooks/{name}/_lessons/` dir no longer contributes to any render.
- [x] `targets: [groom/nonexistent]` produces the `unknown_step_target` Note in `render-playbook groom` output, exit 0.

#### Task 2.3 DoD

- [x] Populated vault `lessons/` or any legacy `_lessons/` dir → exactly this block, one path per line: `**Note — tell the user:** legacy lessons detected ({paths}) — playbooks no longer read them; migrate to _lessons/ with targets: frontmatter.`
- [x] New-root lesson without valid targets → exactly: `**Note — tell the user:** lesson {file} has no valid targets: — not injected.`; lesson injected nowhere.
- [x] Both notices absent when neither condition holds (fixture-vault reports unchanged).

#### Task 2.4 DoD

- [x] Every DoD bullet of 2.1–2.3 has a test.
- [x] `## Lessons` format-lock tests (heading shape, body never Jinja-parsed) pass without edits to `_playbook_lessons.j2`.

---

### M3: Agent-body injection — 4 SP | done

**Goal**: `agent:{id}`-targeted lessons render into the two internal agent bodies at load time.

**Verify**: `bin/booping render src/templates/agents/booping-researcher.md.j2` against a scratch vault with an `agent:booping-researcher` lesson shows the lesson block; without one, output is byte-identical to today.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | New `_agent_lessons.j2` partial (takes `agent_id`, filters `context.targeted_lessons` on `agent:{agent_id}`, renders title + body per lesson, empty output when none); include in both internal agent templates | `src/templates/_partials/_agent_lessons.j2`, `src/templates/agents/booping-researcher.md.j2`, `src/templates/_partials/_developer_body.j2` | 2 | done |
| 3.2 | Template tests: agent render with a matching lesson, with only non-matching lessons, and with none | `booping-python/tests/templates/test_agent_lessons.py` | 2 | done |

#### Task 3.1 DoD

- [x] Matching lesson appears in the rendered agent body under a `## Lessons` heading; non-matching and legacy lessons never do.
- [x] No lessons → partial contributes zero bytes.

#### Task 3.2 DoD

- [x] Three render scenarios asserted by output diff.

---

### M4: Learn playbook writes the new shape — 8 SP | done

**Goal**: the learn playbook routes candidates against the full target space and writes only `{vault}/_lessons/{N}_{kebab}.md` files with `targets:`.

**Verify**: `bin/booping render-playbook learn --project playbooks/_fixtures/vault --set now=19700101-00-00` shows the target-space table in `extract-candidates`, a Targets column in the review-table step, and the `_lessons/` write path in `write`; `just playbook-reports` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Target-space partial `playbooks/_partials/lesson_target_space.md`: one `### {playbook}` section per entry in `context.playbooks`, each holding a steps table (columns `Step \| Summary`), then a `**Lessons:**` bullet list (`{title} — {one-line summary}`, from that playbook's targeted lessons) and an `**Agents:**` bullet list (`{agent} — {responsibilities}`, from `config.skills.{playbook}.agents` good_for plus step `detached` values); empty sub-lists omitted; include from `extract-candidates` step body | `playbooks/_partials/lesson_target_space.md`, `playbooks/learn/extract-candidates/base.md` | 3 | done |
| 4.2 | Write-path swap: create shadow copies under `playbooks/learn/_partials/` — `_learn_targets.j2` (Lesson row → `_lessons/{N}_{kebab}.md` + targets) and `_lesson_template.j2` (frontmatter gains `targets:` list) — which the loader chain resolves ahead of `src/templates/_partials/`; the core files are never edited. Review table gains a Targets column; write step resolves `{N}` from `ls _lessons/` | `playbooks/learn/_partials/_learn_targets.j2`, `playbooks/learn/_partials/_lesson_template.j2`, `playbooks/learn/review-table/base.md`, `playbooks/learn/write/base.md` | 3 | done |
| 4.3 | Sweep + commit surfaces: dedup-sweep's lookup set becomes both `_lessons/` roots plus legacy `lessons/` (read-only, dup context only) — detection itself stays model-judged per the step's existing new / update / conflict verdicts, no algorithm change; close-working-set stages `_lessons/` | `playbooks/learn/dedup-sweep/base.md`, `playbooks/learn/_scripts/close-working-set` | 2 | done |

#### Task 4.1 DoD

- [x] Rendered table covers every discovered playbook with step names + summaries; lesson and agent sub-lists render only when non-empty.
- [x] Old `/learn` skill render (`bin/booping render src/templates/skills/learn.md.j2`) byte-identical to before this milestone.

#### Task 4.2 DoD

- [x] `write` step names only `_lessons/` and `_booping/` and repo `CLAUDE.md` as write targets — vault `lessons/` appears nowhere in the learn playbook render.
- [x] Review-table step instructs one Targets cell per row using the three entry forms.
- [x] `src/templates/_partials/_learn_targets.j2` and `_lesson_template.j2` untouched (`git diff` clean on both).

#### Task 4.3 DoD

- [x] Sweep step lists both roots and the legacy dir with their roles.
- [x] Script stages `_lessons/` when present; scratch-vault replay of the M4 Verify transition commits a written lesson.

---

### M5: Docs + committed reports — 4 SP | done

**Goal**: every doc describing lessons matches the new system; committed playbook reports regenerated.

**Verify**: `grep -rn "step:" documentation/playbook.md` shows no lesson-scoping references; `just playbook-reports && git diff --stat -- playbooks/*/_reports/` shows only expected drift.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite lesson docs: `documentation/playbook.md` `## Lessons` (two roots, `targets:` forms, notices, shadowing), `documentation/learn.md` write paths, `documentation/vault.md` `_lessons/` entry (legacy `lessons/` marked legacy-skills-only) | `documentation/playbook.md`, `documentation/learn.md`, `documentation/vault.md` | 2 | done |
| 5.2 | Repo `CLAUDE.md` Playbooks/Lessons prose updated to the new system (audience: framework developers — no migration-history narrative); regenerate `playbooks/*/_reports/` via `just playbook-reports` | `CLAUDE.md`, `playbooks/*/_reports/output.md` | 2 | done |

#### Task 5.1 DoD

- [x] No doc references `_playbooks/{name}/_lessons/`, root-level playbook lesson dirs, or the `step:` key except as an explicit legacy/migration note.
- [x] `targets:` entry forms documented with one example each.
- [x] The v1 agent-reach limitation (internal booping agents only; external/global agents receive no targeted lessons) stated in `documentation/playbook.md`.

#### Task 5.2 DoD

- [x] CLAUDE.md Playbooks bullet and editing conventions match shipped behavior.
- [x] Reports regenerated; no unexplained diff.

---

### M6: Thin target-space fetch + pinned discovery roots — 7 SP | done

**Added mid-sprint at the user's direction**, after M4 shipped. Two problems M4 surfaced: the target-space table enumerates every discovered playbook including the machine-local global root, which made `playbooks/learn/_reports/output.md` machine-dependent; and rendering the full space for every playbook up front is the wrong shape — learn should see a table of contents, pick the playbooks a candidate touches, and fetch only those targets. Runs **before M5**, so M5's docs and report regeneration describe the final state.

**Goal**: `--project` pins playbook discovery to core + that project; `booping render` accepts `--set`; the learn playbook renders a playbook ToC and fetches per-playbook targets on demand, with the selection logic living in the template, not the CLI.

**Verify**: `bin/booping render-playbook learn --project playbooks/_fixtures/vault --set now=19700101-00-00` shows a ToC (name, summary, step names, fetch command) and no global-root playbook; `bin/booping render playbooks/_partials/lesson_target_space.md --set targets_for=groom,retro` prints the targets tables for exactly those two.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `--project <path>` pins playbook discovery to the core root + that project's `_playbooks/`, skipping the machine's global `{home_dir}/_playbooks/`; discovery without `--project` is unchanged (core → global → local) | `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/commands/render_playbook.py` | 2 | done |
| 6.2 | Add `--set <dotted.key>=<value>` to `booping render`, reusing `parse_set_overrides` and the same final-tier deep-merge `render-playbook` applies; lift the helper to a shared module rather than importing across commands | `booping-python/src/booping/commands/render.py`, `booping-python/src/booping/commands/render_playbook.py` | 2 | done |
| 6.3 | Split `lesson_target_space.md`: a ToC surface (per playbook — name, summary, step names only, and the `booping render … --set targets_for=…` command) and a targets surface filtered by `config.targets_for`, both driven from the template so the CLI stays unaware of learn's logic; `extract-candidates` renders the ToC and instructs the fetch | `playbooks/_partials/lesson_target_space.md`, `playbooks/_partials/lesson_target_toc.md`, `playbooks/learn/extract-candidates/base.md` | 3 | done |

#### Task 6.1 DoD

- [x] A render with `--project` lists only core + that project's playbooks; the same render on a machine with a populated global root is byte-identical.
- [x] A render without `--project` still discovers all three roots, name-clash reporting unchanged.
- [x] `just playbook-reports` output is reproducible across machines — no global-root playbook appears in any committed report.

#### Task 6.2 DoD

- [x] `booping render <template> --set k=v` deep-merges as the final config tier, repeatable, later pairs winning; a pair without `=` → stderr + exit 1.
- [x] `--set now=…` pins `now(...)` in a plain `render` the same way it does in `render-playbook`.
- [x] `parse_set_overrides` has exactly one definition in the tree.

#### Task 6.3 DoD

- [x] The ToC renders one entry per playbook: name, summary, step names only (no per-step summaries), and the exact fetch command for that playbook's targets.
- [x] `--set targets_for=groom,retro` renders the full targets tables (steps + summaries, Lessons, Agents) for exactly those playbooks; an unknown name in the list renders nothing for it and does not fail the render.
- [x] No `targets_for` set → the targets surface renders nothing, and the CLI carries no learn-specific flag or default.

---

## I/O contract

Behavioral surface changes:

- **`render {template} --set {k}={v}`** (new in M6): same semantics as `render-playbook --set` — repeatable, final-tier deep-merge, values stay strings, pair without `=` → stderr + exit 1.
- **`--project {path}`** (M6): additionally pins playbook discovery to core + that project, skipping the global root.

- **`render-playbook {name}` stdout**: `## Lessons` sections now sourced from targeted lessons only. New non-blocking notices (exit 0, in-band): `legacy_lessons` — `**Note — tell the user:** legacy lessons detected ({paths}) — playbooks no longer read them; migrate to _lessons/ with targets: frontmatter.`; `untargeted_lesson` — `**Note — tell the user:** lesson {file} has no valid targets: — not injected.`; `unknown_step_target` — Note naming the lesson and the unknown step.
- **`render-playbook {name} --step {step}`**: appends lessons whose targets contain `{name}/{step}`; unknown step still stderr + exit 1.
- **`--no-lessons`**: suppresses targeted-lesson injection on both surfaces (notices still render).
- **`debug-context`**: dump includes `targeted_lessons`.
- **Exit codes**: unchanged everywhere (0 with in-band notices; 1 usage errors; 2 hook failures).

## Final Verification

- [x] `just lint && just typecheck && just test` green.
- [x] `just playbook-reports` green; committed reports drift only where lessons sections changed.
- [x] Scratch-vault end-to-end: write a lesson with each of the three target forms → `render-playbook` composed + `--step` + agent render each show exactly their own.
- [x] Legacy vault (populated `lessons/` + `_playbooks/groom/_lessons/`) renders with the migration notice and no legacy lesson content.
- [x] `bin/booping render src/templates/skills/learn.md.j2` and `groom/chat/code-review/retro` skill renders byte-identical to pre-plan output.

## Out of scope

- Removing `_lessons.j2` / vault `lessons/` legacy-skill injection (dies with the skills themselves).
- Migrating existing lesson content (0004–0010) — user-driven, aided by the migration notice.
- Glob/wildcard/negation target syntax; external-agent lesson injection; a `booping lessons` management CLI.
- Any change to the old `/learn`, `/groom`, `/retro`, `/develop` skills or their shared partials.

## CLAUDE.md impact

Playbooks bullet: replace the four-scope `_lessons/` + `step:` description with the two-root `targets:` model and its notices. Editing conventions: lesson edits under `_lessons/` require `just playbook-reports` only when fixture-visible. Covered by task 5.2.

## Risk register

- `_lessons/` at the vault root vs `_playbooks/_lessons/` (old local playbook-root lessons dir): distinct paths, no collision — verified in research.
- The learn playbook's target-space table renders at skill-load of every learn run; with many playbooks it grows linearly (~6 rows per playbook today, acceptable).
