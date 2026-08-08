---
title: Code review as a separate track — codereview artifacts own review state
type: feature
status: done
sp: 30
split_from: null
created: 2026-08-08 11:56
planned: null
started: 2026-08-08 13:00
completed: 2026-08-08 13:42
code_review: null
retro: null
goal: null
summary: "Code-review runs persist as codereviews/{dir}/{ts}.md artifacts with own
  statuses; plans link them via code_reviews: list"
commit: 6dbf8dd6b20df29db000ca5fb60af10c5e1949cf
agents:
  research-codebase: a68837e86489fd49d
  develop-loop-g1: ac8e89dd522280419
  develop-loop-g2: a558023b3a7441305
  develop-loop-g3: a87a72368c14ebcdc
  develop-loop-g4: aab601cf010eefab6
  develop-loop-g5: a307ad45ce2ee837b
  verify: aaa6fc1c3aed4d13a
reviewed_at: 2026-08-08 12:56
sessions:
- 046bbec9-061e-417d-a1e5-5e52c29d03be
- d6eab032-9c01-43a1-a6e3-fe8894890e13
metrics_active_minutes: 54
metrics_models:
- claude-fable-5
metrics_tokens_input: 436
metrics_tokens_output: 181447
metrics_tokens_cache_creation: 718709
metrics_tokens_cache_read: 21509851
---

# Code review as a separate track — codereview artifacts own review state

## Context

The `code-review` playbook is ephemeral: no workdir, no persisted state, no review artifact — findings live in the conversation and the only trace is a `code_review:` date stamped onto the plan by an in-step `frontmatter-update` call in `resolve`. Retro/learn already moved to their own artifact track (`retrospectives/{slug}.md` with own statuses, plans stay `done`). After this plan, every code-review run writes its own artifact `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` (ad-hoc scopes use a target slug instead of a plan dirname), the artifact owns the state machine `in-agent-review → human-review → done`, and the plan links its reviews through a new `code_reviews:` list key. The review queue becomes all `done` plans with their review history visible. Review templates gain the missing global tier.

## Decisions

- **Link key**: new `code_reviews:` frontmatter key, list of review-file paths, seeded `null`. The legacy `code_review:` date key is ignored everywhere — no migration; legacy plans simply show no history.
- **Queue predicate**: `scope_candidates` becomes `where: {status: done}` with a `code_reviews` column — every done plan stays reviewable (re-review is first-class), history is visible in the table.
- **State addressing**: retro pattern — no `artifact:` in the machine; workdir is the vault root and every `playbook-state`/`playbook-transition` call passes `--target codereviews/{dir}/{YYYYMMDDHHmm}.md`.
- **Statuses**: `in-agent-review` (artifact created at scope close, detached review pass running) → `human-review` (findings written to the artifact, verdict pending) → `done` (verdict resolved; terminal).
- **Plan append mechanism**: new hook script `close-code-review` in `playbooks/code-review/_scripts/`, modeled on `playbooks/_scripts/close-working-set` — appends the artifact path to the plan's `code_reviews:` list (creating the list from `null`), stamps nothing else on the plan, commits the vault. Ad-hoc runs (no plan) skip the append and only commit.
- **Review artifact format** (locked content): frontmatter `status`, `plan` (repo-relative plan path or `null` for ad-hoc), `scope` (one-line diff-range/target description), `created` (run clock to the minute); body sections in order — H1 title, `## Scope`, `## Findings` (severity-grouped, as `present` shows them today), `## Verdict` (user's decision per finding), `## Resolution` (what `resolve` did).
- **Ad-hoc scopes**: latest-commits / named-target runs persist too, under `codereviews/{target-slug}/{YYYYMMDDHHmm}.md`, `plan: null`, no plan append.
- **Review templates**: `ReviewTemplate.load_all` gains the global tier — core `docs/review_templates` → `{home_dir}/review_templates/` → vault `review_templates/`, later tiers override by `name`, mirroring `Lesson.load_targeted`.
- **Plannotator**: stays userland (lesson or external wiring) — nothing in this plan touches it.
- **No migration**: `codereviews/` is created lazily by the run (`mkdir -p`) in existing vaults and added to scaffold surfaces for new ones.

## Architecture

The playbook keeps its flat graph `scope → review → present → resolve` and gains a `states:` block whose machine is addressed by `--target`. The lifecycle joins the plan track exactly like retro does: plan status never moves; the join is the `code_reviews:` list written by the `close-code-review` hook on the `human-review → done` edge. The queue is the existing `core.code_review_playbook.queries.scope_candidates` spec with a widened predicate. Rendered surfaces consuming this: the scope step's candidates table, CLAUDE.md/README/documentation narrative; `sprints.md` untouched.

## Milestones

### M1: State machinery — 6 SP | done

**Goal**: `playbooks/code-review/playbook.yaml` carries the artifact-owned state machine and the close hook exists and works.

**Verify**: `bin/booping render-playbook code-review` shows the `## State` section; a scratch-vault dry run of `playbook-transition code-review done --target …` appends the path to a scratch plan's `code_reviews:` and commits.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `states:` block to the manifest: statuses `in-agent-review → human-review → done`, `initial: in-agent-review`, no `artifact:` key (runs address by `--target`); `done` edge hooks: `frontmatter-update reviewed_at` stamp on the artifact + `script close-code-review` | `playbooks/code-review/playbook.yaml` | 3 | done |
| 1.2 | Write `close-code-review` hook: stdlib-only Python modeled on `close-working-set`; reads `BOOPING_ARTIFACT`, parses artifact frontmatter, appends the artifact's vault-relative path to the linked plan's `code_reviews:` list (`null` → one-element list; skip when `plan: null`), `git add` + commit with `codereview` prefix | `playbooks/code-review/_scripts/close-code-review` | 3 | done |

#### Task 1.1 DoD

- [x] `booping render-playbook code-review` renders a `## State` section with the three statuses and both hooks on the closing edge.
- [x] `booping playbook-state code-review --workdir {vault} --target {file}` reports the frontier for a hand-made artifact at each status.

#### Task 1.2 DoD

- [x] Append works from `code_reviews: null` and from an existing list, and is idempotent — the same path is never appended twice.
- [x] `plan: null` artifact → no plan touched, vault still committed.
- [x] Script lives in the playbook's own `_scripts/`, resolved by hook lookup (most specific wins).

---

### M2: Step bodies — 10 SP | done

**Goal**: the four steps run the persisted lifecycle — artifact created at scope close, findings and verdict written into it, close via transition instead of an in-step date stamp.

**Verify**: `just snapshots` diff read for code-review; rendered step bodies show the artifact-path protocol and no `code_review=` stamp anywhere.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rewrite `scope`: candidates table from the widened query (history column visible), resolve the artifact path — `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` for plan scope, `codereviews/{target-slug}/{ts}.md` ad-hoc — create it (`mkdir -p` + the locked frontmatter), post `## Review scope` | `playbooks/code-review/scope/opus-5.md` | 3 | done |
| 2.2 | Update `review` + `present`: findings from the detached pass are written into the artifact's `## Findings`, run transitions `in-agent-review → human-review`; `present` records the per-finding verdict into `## Verdict` | `playbooks/code-review/review/opus-5.md`, `playbooks/code-review/present/opus-5.md` | 2 | done |
| 2.3 | Rewrite `resolve`: write `## Resolution`, drop the `frontmatter-update {plan} code_review=…` call, close the run via `playbook-transition code-review done --target {file}` (hooks own the plan append + commit); update the closing report wording | `playbooks/code-review/resolve/opus-5.md` | 3 | done |
| 2.4 | Rewrite `playbook.md` preamble: drop every ephemeral-run claim, add the resume rule (re-enter from the `playbook-state` frontier by `--target`), keep the hard rules that survive (no hand commits — the hook commits; no style noise; lesson violations BLOCKER) | `playbooks/code-review/playbook.md` | 2 | done |

#### Task 2.1 DoD

- [x] Rendered scope step names the exact artifact path formula and the locked frontmatter keys.
- [x] The ad-hoc route produces `plan: null` and a slug path.

#### Task 2.2 DoD

- [x] The findings section shape in the artifact matches what `present` posts in chat — one source of truth, no duplicate formats.
- [x] The transition to `human-review` happens after findings are written, before the user is asked.

#### Task 2.3 DoD

- [x] No `code_review` key write remains anywhere in the playbook.
- [x] The closing report tells the user the artifact path and that the plan's `code_reviews:` list was extended (plan runs only).

#### Task 2.4 DoD

- [x] No stale "no persistent report / no workdir" prose survives.
- [x] The resume rule covers a run interrupted at each non-terminal status.

---

### M3: Config, seeds, fixtures — 4 SP | done

**Goal**: config and every seeded frontmatter surface speak `code_reviews:`; new vaults get `codereviews/`.

**Verify**: `just lint typecheck pytest` green; `git grep -n 'code_review:' playbooks src` shows no seed surface writing the legacy key.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Widen `core.code_review_playbook.queries.scope_candidates` to `where: {status: done}`, columns `[sp, title, code_reviews]`; add a `codereviews` dir to `core.setup_playbook.scaffold` and to both `mkdir -p` blocks in `bin/booping-create-project` | `src/config.yaml`, `bin/booping-create-project` | 2 | done |
| 3.2 | Seed swap: `code_review: null` → `code_reviews: null` in the plan-frontmatter partial, its static doc mirror, the hermetic fixture plans, and the python test fixtures referencing the old key/path | `playbooks/_partials/plan_frontmatter.md`, `docs/template_plan_frontmatter.md`, `playbooks/_fixtures/vault/plans/*/index.md`, `booping-python/tests/context/config_test.py`, `booping-python/tests/__fixtures__/vault-disable-internal-agents/config.yaml` | 2 | done |

#### Task 3.1 DoD

- [x] `booping query --config core.code_review_playbook.queries.scope_candidates` lists all done plans with the history column.
- [x] Fresh scaffolds (`booping scaffold` and `booping-create-project`) both create `codereviews/`.

#### Task 3.2 DoD

- [x] New plans seed `code_reviews: null`; no seed surface still writes `code_review:`.
- [x] `just pytest` green.

---

### M4: Global review-template tier — 4 SP | done

**Goal**: review templates load core → global → project, later tiers overriding by `name`.

**Verify**: unit test covers the three-tier override; `bin/booping render-playbook code-review` shows a global-tier template when one exists in `{home_dir}/review_templates/`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Extend `ReviewTemplate.load_all` with the `{home_dir}/review_templates/` tier between core and project, mirroring `Lesson.load_targeted`; add unit tests for the override order | `booping-python/src/booping/context/review_template.py`, `booping-python/tests/` | 3 | done |
| 4.2 | Surface the tier in the rendered table (source label core/global/project) and update the vault doc's `review_templates/` section | `src/templates/_partials/_review_template.j2`, `documentation/vault.md` | 1 | done |

#### Task 4.1 DoD

- [x] A same-`name` template in a later tier wins; a test proves core < global < project.
- [x] `just lint typecheck pytest` green.

#### Task 4.2 DoD

- [x] The rendered template table distinguishes the three sources.

---

### M5: Docs, narrative, snapshots — 6 SP | done

**Goal**: every narrative surface describes the persisted track; committed reports regenerate; `just ci` green.

**Verify**: `just ci` passes end to end; `git grep -in 'ephemeral' documentation playbooks/code-review` returns nothing stale.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Documentation sweep: rewrite `code_review.md` for the persisted lifecycle; fix queue/lifecycle claims in `quick_start.md`, `develop.md`, `vault.md` (plan-frontmatter keys + a new `codereviews/` section), `project_config.md` (query example), `playbook.md`, `index.md`, `integrating-external-agents.md` | `documentation/*.md` | 3 | done |
| 5.2 | CLAUDE.md track-join sentence (`code_review: null` queue → `code_reviews:` history-list semantics, widened queue) and the README Statuses section for the new `states:` block | `CLAUDE.md`, `README.md` | 1 | done |
| 5.3 | Regenerate the committed report and update the mdcheck rules for the new H2 sequence (adds `## State`); run full `just ci` | `playbooks/code-review/_reports/output.md`, `playbooks/code-review/_reports/rules.yaml` | 2 | done |

#### Task 5.1 DoD

- [x] No page claims the run is ephemeral or that a `code_review:` date is stamped.
- [x] `vault.md` documents `codereviews/` and the `code_reviews:` key.

#### Task 5.2 DoD

- [x] The README Statuses narrative names the three review statuses and the join-by-list semantics.

#### Task 5.3 DoD

- [x] `just snapshots` clean, `just mdcheck` green, `just ci` green.

---

## Final Verification

- [x] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck).
- [x] `bin/booping render-playbook code-review` reviewed: `## State` section present, no stale ephemeral prose, no `{{placeholder}}` leaks.
- [x] End-to-end dry run in a scratch vault: scope → artifact created (`in-agent-review`) → findings (`human-review`) → close (`done`), plan's `code_reviews:` extended, vault committed by the hook.
- [x] Targeted lessons still inline into the rendered playbook.

## Out of scope

- Plannotator presentation — userland lesson / external wiring only.
- Migration of legacy `code_review:` date values — the key is simply ignored.
- Eval suites for code-review steps — none exist today; adding one is a follow-up, not this sprint.
- Retro/learn playbooks — untouched.

## CLAUDE.md impact

Covered by task 5.2: the Lifecycle section's track-join sentence changes (`code_review: null` queue → `code_reviews:` history list, widened queue predicate).
