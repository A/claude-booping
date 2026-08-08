---
title: Learn targets consolidation — extra-instructions retirement, code-review 
  skill removal, skill:playbook lesson target
type: feature
sp: 34
split_from: null
created: 2026-08-07 21:33
planned: null
started: 2026-08-08 00:38
completed: 2026-08-08 20:15
code_review: null
retro: null
goal: null
summary: "Lessons become the one behavior channel: skill:{name} target, extras + /code-review
  skill removed, log to vault root, migration 004"
commit: 071f23b282d62f19dd3ce9541fc41547a6a6726a
status: done
reviewed_at: 2026-08-08 00:38
sessions:
- fd1ff233-2826-41c3-9acb-7484c719e897
- 4aca81f3-87b4-4fee-89a9-226996404736
- 5a8c526f-60f5-4f1e-9902-4e78fd319c9f
metrics_active_minutes: 101
metrics_models:
- claude-fable-5
metrics_tokens_input: 698
metrics_tokens_output: 300753
metrics_tokens_cache_creation: 2571484
metrics_tokens_cache_read: 35458397
---

# Learn targets consolidation — extra-instructions retirement, code-review skill removal, skill:playbook lesson target

## Context

Learn routes accepted candidates to four destinations (routing matrix in `playbooks/learn/_partials/_learn_targets.j2`): lessons, `_booping/skill_*.md` skill extras, `_booping/agent_*.md` agent extras, repo `CLAUDE.md`. Agent extras duplicate `agent:{id}` lessons; skill extras serve a skill surface shrinking to `/playbook` alone. After this plan: the `/code-review` skill is deleted (the `code-review` playbook stays), the `_extra_instructions.j2` channel is removed end to end, lessons gain a generic `skill:{name}` target injected into skill bodies at render time, learn's target docs consolidate into one partial, the invocation log moves to `{vault}/.booping.log`, and migration 004 converts existing vault extension files into targeted lessons.

## Decisions

- **Lessons are the only behavior channel**: skill extras and agent extras die; `skill:{name}` + `agent:{id}` lessons replace them — one mechanism, one injection path, no duplicate surface.
- **Generic `skill:{name}` parser form**, not a pinned literal — mirrors `agent:{id}`; only `playbook` exists today but the form outlives the roster.
- **Consolidated doc keeps the `_learn_targets.j2` name**: old routing-matrix file deleted, `lesson_target_toc.md` renamed onto `playbooks/learn/_partials/_learn_targets.j2` (content carries a Jinja loop → `.j2`). Sections: `## Targets` (four lesson forms + per-playbook toc + static skills line), `## Repo CLAUDE.md` (the one non-lesson destination), `## Global scope` (never write `~/.claude/CLAUDE.md`; behavior caused by project `CLAUDE.md` is fixed there).
- **`core.code_review_playbook` narrows**: `queries.review_candidates` and `status` dropped (skill-only consumers); `queries.scope_candidates` and `agents` stay (playbook reads them).
- **Migration 004 deletes what it converts**: each `_booping/skill_*.md` / `agent_booping-*.md` becomes a `_lessons/NNNN_*.md` with proper `targets:`, then the source file is deleted; the `_booping/` dir itself is left for manual cleanup. Mapping: `agent_booping-X.md` → `targets: [agent:booping-X]`; `skill_playbook.md` → `targets: [skill:playbook]`; `skill_{retired-skill}.md` → `targets: [{name}]` (the playbook of the same name). Content conversion is agent-judged; numbering continues the vault's `NNNN` sequence.
- **Log at vault root**: `{vault}/.booping.log`; `_booping/` leaves the setup scaffold; gitignore seed ignores `.booping.log` instead of `_booping/*.log`.
- **External agents doc keeps registration only**: an external agent's prompt is the user's own; the plugin wires it via the config `agents` block and nothing else — all `_booping/skill_*` briefing-shaping content is removed, not ported.
- **Evals not run this sprint**; prompt/fixture text kept consistent so suites stay runnable later.

## Architecture

Load-time lesson injection gains one channel: `Lesson.load_targeted` already parses `targets:`; `parse_target` learns `skill:{name}` (new `LessonTarget` kind `skill`); `src/templates/_partials/_skill_lessons.j2` (mirror of `_agent_lessons.j2`) filters `context.targeted_lessons` by `kind == "skill"` and is rendered by `src/templates/skills/playbook.md.j2` in the exact slot the `_extra_instructions.j2` call vacates. `context.extra_instructions` disappears from `Context`. The learn playbook's write step routes to two destinations only (`_lessons/`, repo `CLAUDE.md`); its target-space doc is the consolidated `_learn_targets.j2`. Migration gate math is untouched — migration 004 raises `latest_shipped_id()` to 4, the fixture vault watermark follows.

## Milestones

### M1: skill:{name} lesson target engine — 4 SP | done

**Goal**: a lesson with `targets: [skill:playbook]` renders inside the `/playbook` skill body; `skill:` entries parse as first-class targets.

**Verify**: `just pytest`; `bin/booping render src/templates/skills/playbook.md.j2` with a `skill:playbook` lesson present in the vault shows the lesson block.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `_SKILL_RE` mirroring `_AGENT_RE`; extend `LessonTarget` with kind `skill` + `skill` field; add `parse_target` branch; extend parametrized legal/rejection cases | `booping-python/src/booping/context/lesson.py`, `booping-python/tests/context/lesson_test.py` | 2 | done |
| 1.2 | Author `_skill_lessons.j2` mirroring `_agent_lessons.j2` (filter `kind=="skill"`, `skill==kwargs.skill_id`); render it from the playbook skill template; add render test | `src/templates/_partials/_skill_lessons.j2`, `src/templates/skills/playbook.md.j2`, `booping-python/tests/templates/test_skill_lessons.py` | 2 | done |

#### Task 1.1 DoD

- [x] `parse_target("skill:playbook")` returns `LessonTarget(kind="skill", skill="playbook")`; `skill:` and `skill:*` reject.
- [x] Existing target forms unchanged (all prior parametrized cases green).

#### Task 1.2 DoD

- [x] Rendered playbook skill shows a `skill:playbook`-targeted lesson; no lesson means no empty heading.
- [x] Test renders `src/templates/skills/playbook.md.j2` both with and without a matching lesson.

---

### M2: extra-instructions channel removal — 3 SP | done

**Goal**: `context.extra_instructions` and its partial are gone; no template renders `_booping/` extension files.

**Verify**: `just pytest`; `grep -rn "extra_instruction" src/ booping-python/` returns nothing; `bin/booping render src/templates/agents/booping-researcher.md.j2` renders clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Delete the loader and its `Context`/debug wiring; delete loader tests, the `assemble_test` assert, and the `skill_groom.md` fixture file | `booping-python/src/booping/context/extra_instructions.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/src/booping/commands/debug.py`, `booping-python/tests/context/extra_instructions_test.py`, `booping-python/tests/context/assemble_test.py`, `booping-python/tests/__fixtures__/vault-full/_booping/skill_groom.md` | 2 | done |
| 2.2 | Delete the partial and its two surviving call sites (developer body, researcher); delete the partial's render tests | `src/templates/_partials/_extra_instructions.j2`, `src/templates/_partials/_developer_body.j2`, `src/templates/agents/booping-researcher.md.j2`, `booping-python/tests/templates/test_extra_instructions.py` | 1 | done |

#### Task 2.1 DoD

- [x] `Context` has no `extra_instructions` attribute; `debug-context` output carries no such key.
- [x] No test references `extra_instructions`.

#### Task 2.2 DoD

- [x] `grep -rn "extra_instruction" src/templates/` empty.
- [x] Both agent templates render without error (`bin/booping render`).

---

### M3: code-review skill deletion — 3 SP | done

**Goal**: the plugin ships one skill (`/playbook`); the `code-review` playbook keeps everything it reads.

**Verify**: `just build` (clean, no code-review artefact regenerated); `just pytest`; `bin/booping render-playbook code-review` still renders.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Delete the skill artefacts and its build inputs; drop its `config_files.yaml` entry; run `just build` | `skills/code-review/`, `src/files/skills/code-review/`, `src/templates/skills/code-review.md.j2`, `src/config_files.yaml` | 1 | done |
| 3.2 | Drop `queries.review_candidates` and `status` from `core.code_review_playbook` (keep `queries.scope_candidates`, `agents`); update `CORE_QUERY_PATHS`; delete the skill-template test file | `src/config.yaml`, `booping-python/tests/context/config_test.py`, `booping-python/tests/templates/test_available_agents.py` | 2 | done |

#### Task 3.1 DoD

- [x] `skills/` holds only `playbook/`; `git status` shows deletions, no regenerated code-review output.
- [x] `src/config_files.yaml` has no `code-review` key.

#### Task 3.2 DoD

- [x] `core.code_review_playbook` carries `queries.scope_candidates` + `agents` only.
- [x] `bin/booping render-playbook code-review` renders the scope step's query and agents table unchanged.

---

### M4: invocation log to vault root — 4 SP | done

**Goal**: every CLI call logs to `{vault}/.booping.log`; scaffolded vaults have no `_booping/`.

**Verify**: `just pytest`; a `bin/booping config-get home_dir` call appends to the repo-local vault's root `.booping.log`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Point `logger.py` at `vault / ".booping.log"`; update every test asserting the old path | `booping-python/src/booping/logger.py`, `booping-python/tests/test_logger.py`, `booping-python/tests/commands/scaffold_test.py`, `booping-python/tests/commands/frontmatter_update_test.py`, `booping-python/tests/commands/marker_set_test.py`, `booping-python/tests/test_render_playbook.py`, `booping-python/tests/conftest.py` | 2 | done |
| 4.2 | Remove `_booping:` from `core.setup_playbook.scaffold`; change the `.gitignore` seed to ignore `.booping.log`; relocate the log in all five fixture vaults and prune their empty `_booping/` dirs; delete this repo's own `_booping/` | `src/config.yaml`, `playbooks/_fixtures/vault/_booping/`, `booping-python/tests/__fixtures__/vault-full/_booping/`, `booping-python/tests/__fixtures__/vault-minimal/_booping/`, `booping-python/tests/__fixtures__/vault-with-config-override/_booping/`, `booping-python/tests/__fixtures__/playbooks-home/claude-booping/_booping/`, `_booping/` | 2 | done |

#### Task 4.1 DoD

- [x] `logger.py` builds `vault / ".booping.log"`; no `_booping` segment anywhere in `booping-python/src/`.
- [x] All path-asserting tests updated, green.

#### Task 4.2 DoD

- [x] `booping scaffold core.setup_playbook.scaffold` output tree has no `_booping/`; seeded `.gitignore` ignores `.booping.log`.
- [x] `grep -rln "_booping" booping-python/tests/__fixtures__ playbooks/_fixtures` empty.

---

### M5: learn target-doc consolidation — 8 SP | done

**Goal**: learn's rendered output carries one consolidated targets doc (four lesson forms incl. `skill:{name}`, repo-CLAUDE.md case, global-scope rule) and no `_booping/` destination anywhere.

**Verify**: `bin/booping render-playbook learn --project playbooks/_fixtures/vault` reviewed; `just snapshots-accept learn && just mdcheck`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Delete the routing-matrix file; `git mv` `lesson_target_toc.md` onto `_learn_targets.j2`; write the three sections (`## Targets` with four forms + toc + static skills line, `## Repo CLAUDE.md`, `## Global scope`); rewrite the preamble's Single-location rule + include | `playbooks/learn/_partials/_learn_targets.j2`, `playbooks/learn/_partials/lesson_target_toc.md`, `playbooks/learn/playbook.md` | 3 | done |
| 5.2 | Sweep step bodies off the routing matrix and `_booping/` destinations: extract-candidates (base + fable-5 + prompt), dedup-sweep lookup set, review-table Targets bullets (add `skill:{id}`), write destinations (two only), transition commit prose; drop `--stage _booping` from the hook line; fix the `tests.yaml` value regex | `playbooks/learn/extract-candidates/base.md`, `playbooks/learn/extract-candidates/fable-5.md`, `playbooks/learn/extract-candidates/prompt.md`, `playbooks/learn/dedup-sweep/base.md`, `playbooks/learn/review-table/base.md`, `playbooks/learn/write/base.md`, `playbooks/learn/write/fable-5.md`, `playbooks/learn/transition/base.md`, `playbooks/learn/playbook.yaml`, `playbooks/learn/extract-candidates/tests.yaml` | 3 | done |
| 5.3 | Rewrite the report rules for the new doc structure; re-accept the learn snapshot | `playbooks/learn/_reports/rules.yaml`, `playbooks/learn/_reports/output.md` | 2 | done |

#### Task 5.1 DoD

- [x] One partial file remains; rendered preamble shows the three sections in order; no "routing matrix" phrase survives in the render.
- [x] `skill:{name}` listed with the static skills line (`playbook`).

#### Task 5.2 DoD

- [x] `grep -rn "_booping" playbooks/learn/` returns nothing (fixtures included; sole exception `_reports/_old_skill.md`, a frozen historical capture).
- [x] Hook line reads `--stage _lessons` only; `tests.yaml` regex accepts the `agent:booping-developer` form alone.

#### Task 5.3 DoD

- [x] `just snapshots` clean after accept; `just mdcheck` green with the rewritten rules.

---

### M6: migration 004 — 4 SP | done

**Goal**: `/playbook migrate` converts a vault's `_booping/` extension files into targeted lessons and deletes the converted sources.

**Verify**: `just snapshots-accept migrate && just snapshots`; `bin/booping query --config core.migrate_playbook.queries.pending` lists id 4.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Author the migration: mapping table (`agent_booping-X` to `agent:booping-X`, `skill_playbook` to `skill:playbook`, `skill_{retired}` to the playbook name), agent-judged content conversion continuing the vault's `NNNN` sequence, delete converted files, leave the dir; verification block | `migrations/004_extras_to_lessons/migration.md` | 3 | done |
| 6.2 | Bump the fixture watermark to 4; re-accept the migrate snapshot (report hardcodes recorded/latest ids) | `playbooks/_fixtures/vault/.booping`, `playbooks/migrate/_reports/output.md` | 1 | done |

#### Task 6.1 DoD

- [x] Frontmatter `id: 4`, `title`, `summary`; body carries the mapping table, conversion rules, deletion of converted sources, verification commands.
- [x] A file with no convertible content has a stated disposition (delete with a note in the report, never silently skipped).

#### Task 6.2 DoD

- [x] `just snapshots` green; migrate report names 4 as recorded and latest.

---

### M7: docs sweep — 7 SP | done

**Goal**: no shipped doc references the code-review skill, extension files, the `_booping/` log path, or the four-target routing matrix.

**Verify**: `grep -rn "extra_instruction\|_booping/skill_\|_booping/agent_\|skill_code-review" CLAUDE.md README.md docs/ documentation/` empty; `just ci`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | CLAUDE.md: one shipped skill, agent-wiring section onto lessons channels, vault-layout log bullet, `core.code_review_playbook` schema line, skill-authoring section re-exemplared on `playbook.md.j2` | `CLAUDE.md` | 2 | done |
| 7.2 | documentation/: retire `code_review.md` to a stub pointing at the playbook; strip `integrating-external-agents.md` to config-registration only (the external prompt is the user's); update `vault.md`, `index.md`, `develop.md`, `learn.md`, `quick_start.md`, `install.md`, `project_config.md` | `documentation/code_review.md`, `documentation/integrating-external-agents.md`, `documentation/vault.md`, `documentation/index.md`, `documentation/develop.md`, `documentation/learn.md`, `documentation/quick_start.md`, `documentation/install.md`, `documentation/project_config.md` | 3 | done |
| 7.3 | README skill/side-route mentions; `docs/learn_review_table.md` example rewrite (no `skill-ext` type, no `skill_code-review`); `docs/development_quality_checks.md` discovery ladder; `docs/plan_templates/claude_skill.md` Final-Verification extension-point bullet + example exclusion | `README.md`, `docs/learn_review_table.md`, `docs/development_quality_checks.md`, `docs/plan_templates/claude_skill.md` | 2 | done |

#### Task 7.1 DoD

- [x] CLAUDE.md grep-clean for the retired surfaces; the new-skill section's worked example renders from a file that exists.

#### Task 7.2 DoD

- [x] `code_review.md` stub links the playbook; the external-agents page has no extension-file wiring; remaining pages grep-clean.

#### Task 7.3 DoD

- [x] The milestone-header grep returns nothing; `just ci` green.

---

### M8: rendered-output reshape review — 1 SP | pending

**Goal**: the user shapes the rendered learn output and consolidated doc before the plan closes (recorded reshape expectation).

**Verify**: user reviewed `playbooks/learn/_reports/output.md` and the rendered `/playbook` skill; requested shape edits applied and re-accepted.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Hand the rendered artefacts back for prose-shape review; apply IA edits; re-accept touched snapshots | `playbooks/learn/_reports/output.md`, `playbooks/learn/_partials/_learn_targets.j2` | 1 | pending |

#### Task 8.1 DoD

- [ ] User confirmed the rendered shape; any edits re-rendered and re-accepted (`just snapshots`).

---

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck).
- [ ] `just build` clean; `bin/booping render src/templates/skills/playbook.md.j2` reviewed — no stale extension prose, no placeholder leaks.
- [ ] `grep -rn "extra_instruction" .` (repo-wide, excluding `.git`) returns nothing.
- [ ] `bin/booping render-playbook learn --project playbooks/_fixtures/vault` shows the consolidated doc; `render-playbook code-review` unaffected.
- [ ] Agent briefings during develop return changed-file lists only (bounded return contract).

## Out of scope

- Running eval suites (`just eval|smoke|regress`) — prompt/fixture text kept consistent, suites not executed.
- The `code-review` **playbook** — unchanged beyond its config block narrowing.
- `retro_playbook.status` and other playbooks' `status` keys — only `code_review_playbook`'s dies here.
- Applying migration 004 to this project's own vault — a normal `/playbook migrate` run after release.
- Removing the legacy `lessons/` dir or `_lessons.j2` partial — untouched by this plan.

## CLAUDE.md impact

Owned by M7.1: shipped-skill count, agent wiring (lessons channels replace extras), vault layout (`.booping.log` at root, `_booping/` gone), config schema (`core.code_review_playbook` narrowed), "Adding a new template-driven skill" exemplar.
