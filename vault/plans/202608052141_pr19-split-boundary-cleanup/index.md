---
title: PR-19 split-boundary cleanup — statuses, fossils, develop hooks
type: refactoring
status: done
sp: 27
split_from: null
created: 2026-08-05 21:41
planned: null
started: 2026-08-05 22:24
completed: 2026-08-05 23:05
retro: null
goal: null
summary: "Post-PR-19 cleanup: cancelled status via superstates, shared _scripts root,
  state-machine prose and retired-skill fossils removed"
commit: bea028658449c4679a62ac2aab58a7d7d544cd6b
agents:
  research-codebase: a560c01602120841e
  develop-loop-g1: a09edb5361b6de8b3
  develop-loop-g2: a25f24231a3cc5c67
  develop-loop-g3: a4c0c6271a9576f44
  develop-loop-g4: a58005216efec7bcd
  develop-loop-g5: a0f5af9fae5266deb
  develop-loop-g6: aca11185da19a8376
reviewed_at: 2026-08-05 22:24
code_review: null
sessions:
- 70166eef-8fbc-4dc0-80cd-165a8cd7279b
- f357a9cb-ab27-43fe-b7a7-f39b70f16f59
metrics_active_minutes: 69
metrics_models:
- claude-fable-5
metrics_tokens_input: 387
metrics_tokens_output: 213167
metrics_tokens_cache_creation: 1538732
metrics_tokens_cache_read: 21399582
---

# PR-19 split-boundary cleanup — statuses, fossils, develop hooks

## Context

The skills→playbooks refactor (PR #19) landed with the core ↔ playbook split structurally sound but with three residue families, catalogued by the PR-19 architecture review (https://github.com/A/claude-booping/pull/19#issuecomment-5193098672): playbook bodies inlining status literals and state-machine logic the rendered `## State` section already carries; retired-skill fossils in prose, partials, docs and engine code; and a cancellation status (`cancelled`) that the `latest_plans` query filters on but no state machine can write. After this plan: playbook bodies reference the machine instead of restating it, no retired surface is referenced anywhere in the repo, `cancelled` is a real terminal on both the groom and develop machines via superstate transitions, and the two near-identical `close-working-set` scripts collapse into one parameterized script in a new shared `playbooks/_scripts/` root resolved by an engine fallback. Observable behavior is unchanged except where drift itself was the bug.

## Decisions

- **Status literals in config**: allowed only inside query specs (`where.status…`); the per-playbook `status` key / query duplication is accepted — no reference mechanism in this plan.
- **Status literals in skills**: out of scope — `code-review`'s hardcodes stay.
- **Status literals in playbook bodies**: none survive — entry-validation prose references the run machine's initial status (rendered in `## State`) instead of spelling names; transition-restating blocks are deleted, the rendered `## State` section is the contract.
- **`cancelled` via superstates**: `resolve_edges` already inherits superstate `transitions:` (lifecycle.py:108-116), so groom declares the `to: cancelled` edge once on each of its two existing superstates (`in-spec`, `awaiting-plan-review`) and develop gets a new `cancellable` superstate over its three non-terminal statuses — zero engine change. Groom's edge hooks `script commit-plan`; develop's hooks `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`.
- **Commit rule**: a commit tied to a state transition is a `script` hook; one not tied to a transition stays prose under the git guide + `commit_message` config. Develop's mid-loop and wrap-up commits stay prose; the wrap-up `--workdir` bug evaporates with the deleted restated-transition block.
- **Shared scripts root**: `playbooks/_scripts/` (already invisible to discovery via the `_`-prefix skip). Engine `script` hook resolution falls back playbook-dir → discovery roots, and passes trailing hook tokens to the script as argv — per-playbook differences live in each `playbook.yaml` hook line.
- **`specs_dir`**: deleted from the bootstrap prompt — dead field, no consumer.
- **`evals.md` authority sentence**: dropped from `playbook-authoring` — step prompts stand on their own; no machine-local dependency survives.
- **No reshape milestone**: intake answer was no (lesson 0008/0009).

## Architecture

Load-time surfaces touched: `src/config.yaml` (query + `git.branches` wording), two `playbook.yaml` machines (rendered into `## State` by `render-playbook`), step `base.md` bodies (rendered inline via `inline_steps`), `src/templates/_partials/_playbook_driving.j2` (included by the `/playbook` skill), `src/templates/skills/code-review.md.j2` (runtime-rendered, no `just build`). Engine: `commands/playbook_transition.py` (`_dispatch_script`) grows root-fallback + argv pass-through; `context/lifecycle.py` loses the dead `Edge.skill`. Regeneration: `just playbook-reports` for groom, retro, learn, develop, playbook-authoring; README "Statuses" section is hand-maintained narrative over the machines and must follow the `cancelled` addition (CLAUDE.md editing convention).

## Milestones

### M1: `cancelled` as a machine status — 5 SP | done

**Goal**: `cancelled` is a terminal status reachable from every non-terminal status of the groom and develop machines, declared once per superstate; the `latest_plans` query's `cancelled` entry is backed by a real writer.

**Verify**: `bin/booping render-playbook groom --project playbooks/_fixtures/vault` and same for `develop` — `## State` tables show the inherited `cancelled` rows, no STOP notices; `just playbook-reports groom develop` clean; `just test`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `cancelled` terminal to both machines via superstate transitions: groom — `to: cancelled` transition (when: user cancels the run; hooks: `script commit-plan`) on the `in-spec` and `awaiting-plan-review` superstates, `cancelled` added to the `terminal` superstate; develop — new `cancellable` superstate over `awaiting-plan-review`, `ready-for-dev`, `in-progress` with one `to: cancelled` transition (when: user cancels the run; hooks: `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`), `cancelled` added to `terminal` | `playbooks/groom/playbook.yaml`, `playbooks/develop/playbook.yaml` | 2 | done |
| 1.2 | Rewrite the retired shared-lifecycle description block in the four groom intake fixtures to describe the current per-playbook machines (including `cancelled`), removing the `backlog → …` shared-flow prose and `/groom` skill mentions | `playbooks/groom/intake/_fixtures/fresh-request.md`, `answered-rerun.md`, `parked-plan-unnamed.md`, `parked-plan-named.md` | 2 | done |
| 1.3 | Update the hand-maintained README "Statuses" narrative and the CLAUDE.md status-chain sentence for `cancelled` on both machines | `README.md`, `CLAUDE.md` | 1 | done |

#### Task 1.1 DoD

- [x] `resolve_edges` returns a `cancelled` edge from every non-terminal status of both machines (superstate inheritance, no per-status duplication).
- [x] `booping playbook-transition groom cancelled` / `develop cancelled` legal from any non-terminal status against a scratch workdir; illegal from `ready-for-dev`/`awaiting-retro`/`fail`/`done`-style terminals.
- [x] Rendered `## State` tables list the inherited rows; committed reports regenerated.

#### Task 1.2 DoD

- [x] No fixture mentions `backlog`, the shared eight-status chain, or `/groom` as a skill.
- [x] Groom intake eval suite still passes (`playbooks/groom/intake/` suite) — assertions confirmed untouched by research.

#### Task 1.3 DoD

- [x] README Statuses section names `cancelled` with its meaning and writers (both machines).
- [x] No other README/CLAUDE.md sentence contradicts the new vocabulary.

---

### M2: shared `playbooks/_scripts/` root + parameterized `close-working-set` — 7 SP | done

**Goal**: one `close-working-set` script in `playbooks/_scripts/`, parameterized by hook-line argv; the engine resolves script hooks against the playbook dir first, then each discovery root, and passes trailing hook tokens to the script.

**Verify**: `just test` (new resolution + argv tests green); `bin/booping playbook-transition` exercised via the existing transition-test fixtures; `just playbook-reports retro learn` clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Engine: `_dispatch_script` receives the playbook's `search_roots`; resolution order playbook-dir `_scripts/` → each root's `_scripts/` (most-specific first); hook tokens after the script name are passed as argv (`script close-working-set --status done` → `argv[1:] = ["--status", "done"]`); missing script error names every path probed. Tests: root fallback, playbook-dir shadowing, argv pass-through, error message | `booping-python/src/booping/commands/playbook_transition.py`, `booping-python/tests/` (transition tests + a `playbooks-core`-style fixture with a root-level `_scripts/`) | 3 | done |
| 2.2 | Merge the two scripts into `playbooks/_scripts/close-working-set` with flags — exact contract: `--status <value>` (stamped on every sibling; required), `--verdicts` (validate non-empty `goal_verdicts:` in the workdir artifact and stamp `retro:` + `goal:` per plan; retro only), `--stage <dir>...` (extra vault dirs staged when present; learn passes `_lessons _booping`), `--prefix <word>` (commit message `{prefix}: {slug} → {status}`). Update both hook lines (`retro/playbook.yaml`: `script close-working-set --verdicts --status awaiting-learning --prefix retro`; `learn/playbook.yaml`: `script close-working-set --status done --stage _lessons _booping --prefix learn`), delete both old copies | `playbooks/_scripts/close-working-set`, `playbooks/retro/_scripts/close-working-set` (delete), `playbooks/learn/_scripts/close-working-set` (delete), `playbooks/retro/playbook.yaml`, `playbooks/learn/playbook.yaml` | 3 | done |
| 2.3 | Document the shared-root resolution + hook argv in CLAUDE.md (hook vocabulary paragraph) and `documentation/playbook.md` | `CLAUDE.md`, `documentation/playbook.md` | 1 | done |

#### Task 2.1 DoD

- [x] Resolution probes playbook dir first, then discovery roots most-specific-first; first hit wins.
- [x] Argv reaches the script; zero-arg hooks behave exactly as before (no regression in groom's `script commit-plan`).
- [x] `playbooks/_scripts/` is not listed as a playbook anywhere (`/playbook` listing, `Playbook.load_all`).

#### Task 2.2 DoD

- [x] Retro and learn transitions produce the same frontmatter stamps and commit messages as before the merge (compare against the pre-merge scripts' behavior on a scratch vault).
- [x] No `_scripts/close-working-set` remains under either playbook dir.
- [x] `drop-plan` and `commit-plan` untouched.

#### Task 2.3 DoD

- [x] CLAUDE.md hook-vocabulary paragraph states resolution order and argv semantics.
- [x] `documentation/playbook.md` run-state section matches.

---

### M3: dead engine code + stale examples — 2 SP | done

**Goal**: no retired-lifecycle vocabulary or dead code in `booping-python/`.

**Verify**: `just lint`, `just typecheck`, `just test` all green; `grep -rn 'config\["plan"\]\|DIR_PLAN_NAME\|macros\.now' booping-python/` returns nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Remove `Edge.skill` (slots, ctor, repr/eq/hash, `_parse_transition`) — zero read-sites and zero test refs confirmed; delete `DIR_PLAN_NAME`; fix the `config["plan"]` docstrings in `lifecycle.py` module header and `playbook.py` `StateMachine`; update stale examples — `scaffold.py:29` (`playbook.scaffold` → `core.setup_playbook.scaffold`), `macros.py` docstrings (`macros.now`/`macros.date` → `core.macros.date`), the three `--stub-macro` help strings in `render.py:38` / `scaffold.py:65` / `render_playbook.py:178` (`macros.now=…` → `core.macros.date=…`) | `booping-python/src/booping/context/lifecycle.py`, `context/playbook.py`, `utils.py`, `macros.py`, `commands/scaffold.py`, `commands/render.py`, `commands/render_playbook.py` | 2 | done |

#### Task 3.1 DoD

- [x] `Edge` has exactly `to`, `when`, `gates`, `hooks`; all tests green without edits (research confirmed zero test refs).
- [x] Every argparse help / docstring example names a config path that exists in `src/config.yaml`.

---

### M4: playbook bodies stop restating the machine — 5 SP | done

**Goal**: no status literal and no restated transition mechanics in any step body or manifest; bodies defer to the rendered `## State` section.

**Verify**: `just playbook-reports` clean (no STOP); `grep -rn 'awaiting-retro\|awaiting-learning\|playbook-transition' playbooks/*/[a-z]*/base.md` shows no literals/invocations outside `_reports/`; rendered reports diff reviewed.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Reword retro/learn intake entry validation to reference the run machine's initial status ("the status the `## State` section names as this run's entry") instead of spelling `awaiting-retro`/`awaiting-learning` — all 8 literal sites including the two STOP error strings, preserving the validation behavior | `playbooks/retro/intake/base.md`, `playbooks/learn/intake/base.md` | 2 | done |
| 4.2 | Delete the transition-restating blocks — `develop/provision/base.md:38-49`, `develop/wrap-up/base.md:26-35`, `retro/save/base.md:42-61`, `learn/transition/base.md:5-20` — leaving at most a one-line pointer ("advance the run per `## State`"); the wrap-up vault-commit prose block (37-44) stays per the commit rule; drop the retired `vault-commit`/`--also` sentences (`retro/save/base.md:53`, `learn/transition/base.md:13`) with their blocks | `playbooks/develop/provision/base.md`, `playbooks/develop/wrap-up/base.md`, `playbooks/retro/save/base.md`, `playbooks/learn/transition/base.md` | 2 | done |
| 4.3 | Delete the graph-restating bullet lists: `groom/playbook.md:21-27` (High Level Execution), `retro/playbook.md:37-44`, `learn/playbook.md:42-49` (High-level workflow) — the step table is the contract | `playbooks/groom/playbook.md`, `playbooks/retro/playbook.md`, `playbooks/learn/playbook.md` | 1 | done |

#### Task 4.1 DoD

- [x] Zero status-name literals in either body; validation and STOP behavior preserved in machine-relative wording.
- [x] Rendered step output still instructs the same checks (report diff reviewed).

#### Task 4.2 DoD

- [x] No step body contains a `playbook-transition` invocation, sample mutation report, or "report is authoritative" restatement.
- [x] Wrap-up's vault-commit prose intact; no `vault-commit`/`--also` mention repo-wide outside `_reports/` history.

#### Task 4.3 DoD

- [x] Manifests carry preamble/rules only — no step-order narration.

---

### M5: retired-skill fossils in playbooks, partials, docs — 4 SP | done

**Goal**: zero references to retired skills or machine-local files anywhere in the repo.

**Verify**: `grep -rn '/retro\b\|/learn\b\|/develop\b\|/groom\b\|/install\b\|skill_chat\|skill_install\|skill_help\|parallel to' playbooks/ src/ docs/ --include='*.md' --include='*.j2'` (excluding `_reports/`) shows only `/playbook <name>` forms; `just playbook-reports` clean.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite bare skill invocations to `/playbook <name>` form at the 9 sites (retro manifest trigger, `retro/synthesize/base.md:44`, `retro/save/prompt.md:8` + `base.md:67,93`, `develop/playbook.md:15`, `develop/wrap-up/prompt.md:6` + `base.md:50,63,83`, `learn/transition/base.md:34`); drop the "(playbook variant, parallel to /X)" clauses from the four manifest triggers; delete develop's "stays canonical / experiment" hard rule (`develop/playbook.md:29`) | `playbooks/retro/playbook.md`, `playbooks/retro/synthesize/base.md`, `playbooks/retro/save/prompt.md`, `playbooks/retro/save/base.md`, `playbooks/develop/playbook.md`, `playbooks/develop/wrap-up/prompt.md`, `playbooks/develop/wrap-up/base.md`, `playbooks/learn/playbook.md`, `playbooks/learn/transition/base.md`, `playbooks/groom/playbook.md` | 2 | done |
| 5.2 | Fold the correct routing content from the dead `src/templates/_partials/_learn_targets.j2` into the live `playbooks/learn/_partials/_learn_targets.j2` (drop the seven retired-skill rows and the "/learn candidates" phrasing), then delete the dead copy | `playbooks/learn/_partials/_learn_targets.j2`, `src/templates/_partials/_learn_targets.j2` (delete) | 1 | done |
| 5.3 | Drop the `evals.md` authority sentence (`playbook-authoring/playbook.md:13`); delete orphaned `docs/cross_validation.md`; fix `docs/learn_review_table.md:7-8` (legacy `lessons/` path → `_lessons/{N}_<kebab>.md`, retired `skill_develop.md` example → a live target); reword `docs/plan_templates/claude_skill.md:50` out-of-scope example without retired-skill names | `playbooks/playbook-authoring/playbook.md`, `docs/cross_validation.md` (delete), `docs/learn_review_table.md`, `docs/plan_templates/claude_skill.md` | 1 | done |

#### Task 5.1 DoD

- [x] Every handoff names `/playbook <name>`; no "parallel to" or "stays canonical" text survives.
- [x] Triggers still match their playbooks' use cases (listing sanity-checked via `/playbook` render).

#### Task 5.2 DoD

- [x] One `_learn_targets.j2` exists, under `playbooks/learn/_partials/`; its rows name only live targets.
- [x] `render-playbook learn` renders the routing table without STOP.

#### Task 5.3 DoD

- [x] `docs/cross_validation.md` gone; no dangling link to it.
- [x] `learn_review_table.md` examples match the `_lessons/` + `targets:` shape.

---

### M6: smaller fixes + regeneration sweep — 4 SP | done

**Goal**: bootstrap prompt, code-review skill prose, and branch config carry no dead or contradictory facts; every committed report regenerated.

**Verify**: `bin/booping render src/templates/skills/code-review.md.j2` clean; `just playbook-reports` clean with no residual diff after a second run; final greps from M4/M5 Verify re-run green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Delete the `specs_dir` line from the bootstrap-prompt block; reword the three hardcoded agent-id prose sites in `code-review.md.j2` (92, 123, 131) to point at the delegation table ("the researcher/developer agent from the table above"); reword `git.branches` `chore/` entry's `when: other` to a freeform descriptor (e.g. `anything not matching a task type`) | `src/templates/_partials/_playbook_driving.j2`, `src/templates/skills/code-review.md.j2`, `src/config.yaml` | 2 | done |
| 6.2 | Regenerate all committed reports (`just playbook-reports`), re-run `just lint typecheck test`, and sweep CLAUDE.md for any sentence invalidated by M1–M6 (hook vocabulary, `_learn_targets`, deleted docs, `specs_dir`) — stale-reference cleanup lands inside this sprint (lesson 0005) | `playbooks/*/_reports/output.md`, `CLAUDE.md` | 2 | done |

#### Task 6.1 DoD

- [x] Bootstrap prompt block has no `specs_dir`; `/playbook` skill renders cleanly.
- [x] Code-review prose names no agent id the delegation table doesn't govern; `disable_internal_agents` projects read consistent instructions.
- [x] No `when:` value collides with the task-type namespace without being one.

#### Task 6.2 DoD

- [x] `git status` clean after a second `just playbook-reports` run (deterministic reports).
- [x] CLAUDE.md contains no reference to deleted files, old script paths, or the pre-`cancelled` status sets.

---

## Final Verification

- [x] `just lint`, `just typecheck`, `just test` green.
- [x] `just playbook-reports` clean, no STOP in any output, byte-stable on re-run.
- [x] `bin/booping render src/templates/skills/code-review.md.j2` and `render-playbook` for all five touched playbooks reviewed — no stale state names, no prose duplicating rendered tables, no placeholder leaks.
- [x] Repo-wide greps: `config\["plan"\]`, `macros\.now`, `DIR_PLAN_NAME`, `vault-commit`, `skill_chat`, `specs_dir`, bare `/retro|/learn` invocations — all empty outside `_reports/` history and this plan.

## Out of scope

- Status-literal duplication between per-playbook `status` keys and their query specs (accepted; no reference mechanism designed).
- `code-review` skill's hardcoded statuses.
- The `migrate` gate exemption in `render_playbook.py` (stays as-is).
- Develop's mid-loop and wrap-up commit prose (stays prose per the commit rule).
- Restamping the vault's legacy `cancelled` plans (their status is now machine-legal anyway).

## CLAUDE.md impact

- Hook vocabulary paragraph: shared `_scripts/` resolution order + hook argv (M2.3).
- Status narrative + README Statuses: `cancelled` on groom/develop machines (M1.3).
- Final sweep for invalidated sentences (M6.2).
