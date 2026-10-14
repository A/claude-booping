# Develop defaults — autonomous run

Run on 2026-10-15, owner unavailable. Every point the runner settled itself, with the reason.

## D1 — branch

The provision gate asks the user to confirm a branch name. The owner's invocation pins the worktree branch `feat/specs` and forbids switching or creating branches, so the sprint reuses `feat/specs` as is; the gate is taken as confirmed by that instruction.

## D2 — intake drift

Plan `commit:` is `0c846dd`, HEAD `632d7e1`. The three commits between are groom's own vault commits on this plan; no file in any task's `Files` column changed. Treated as no drift.

## D3 — repo commit message format

The develop step body asks for `{agent}: {plan title} {message}`; rule/0022 requires Conventional Commits with a scope, and every earlier sprint on this branch follows rule/0022. A rule outranks the step's default, so milestone commits read `feat(…): …` / `docs(…): …`.

## D4 — snapshot policy

Lesson 0013 / rule/0013 forbid `just snapshots-accept` from a run. The owner's standing permission for this feature (2026-10-14, plan C12) overrides it for this run only: accepted only when every drifted hunk is a change this plan describes, each accepted report listed under Accepted snapshots below. Any other drift stops the run.

## D5 — review gates

Autonomous run: gates auto-confirmed; no questions asked.

## D6 — milestone groups

The configured ceiling is one milestone per briefing, so nine briefings, one per milestone, in id order.

## Accepted snapshots

- `playbooks/develop/_reports/output.md` (M02) — one hunk: develop-loop `base.md`'s briefing line reworded from lesson context to `agent:{id}` rules, M02 task 2.2. `learn` did not drift: the hermetic fixture vault holds no playbook-targeted lesson, so the removed `**Lessons:**` block never rendered there.
- `playbooks/learn/_reports/output.md` (M03) — five hunks, all the lesson removal M03 names: `_learn_targets.j2` wording, dedup-sweep summary and lookup set, the retired `update existing at _lessons/{file}` verdict and its write handling, and the transition summary no longer naming a lesson deletion.
- `playbooks/setup/_reports/output.md` (M06) — one hunk: setup-project's vault-tree list drops `_lessons/`, M06 task 6.1.
- `playbooks/migrate/_reports/output.md` (M07) — three hunks, the recorded and latest migration id `3` → `4`. **Outside C12's predicted set** (C12 said `migrate` must not drift, thinking of its worked-example receipts, which did not change). The hunks are the direct render of M07 task 7.3's planned bump of `playbooks/_fixtures/vault/.booping` to 4 (C9) — without that bump every hermetic render would STOP on the migration gate — so every hunk is a change the plan describes and it was accepted; committed separately (`test(migrate): …`) for easy review or revert.

## D7 — M01 import grep

M01's DoD grep `rg -n 'LessonTarget|context.lesson import' booping-python/src` still matches two `from booping.context.lesson import Lesson` lines (`commands/render_playbook.py`, `context/__init__.py`): the `Lesson` model stays in `context/lesson.py` until M04 by the milestone's own scope. Read as "nothing imports target parsing from `context/lesson.py`" — the milestone's stated goal — which holds; `LessonTarget` is gone. The worker also repointed two test files outside the contract's list (`tests/templates/test_{agent,skill}_rules.py`), required once the shim was not kept. Full pytest, typecheck and both e2e corpora green with no expected output edited.

## D8 — M02 extra test file

The worker also rewrote `tests/templates/test_skill_rules.py`, outside the contract's list: its body test located the rules section by the `## Lessons` heading the milestone removes.

## D9 — M03 scope and evidence

The worker also edited `playbooks/learn/write/{base,fable-5}.md` and `playbooks/learn/transition/{base,prompt}.md`, outside the contract's list: they handled the retired lesson-conversion verdict, and M03's own DoD grep (`_lessons` over `playbooks/learn`) cannot pass without them. No learn eval fixture or assert named a lesson file (the `extract-candidates` NO-LESSON-PATH negative assert stays valid), so no suite changed and no smoke run was due — the playbook preamble also bars the runner from launching evals. `render-playbook learn` does not print state hooks, so the closing edge's `--stage specs` is read off `playbooks/learn/playbook.yaml` instead.

## D10 — M04 grep and extra edits

M04's DoD pattern `load_targeted` also matches `load_targeted_rules`, the rules loader; with a word boundary (`load_targeted\b`) the grep prints nothing. The worker also edited `tests/context/lesson_test.py` (deleted `load_targeted` tests), `tests/templates/test_agent_rules.py` (stale `targeted_lessons` key) and three rules e2e cases whose fixtures carried lessons (DoD 4.2 allows only the new case to mention lessons) — all forced by the removal. No snapshot drift.

## D11 — M05 fixture route

M05 asks for a fixture plugin root holding the shared directory; a txtar case cannot create one (`get_plugin_root()` always resolves the real checkout, fixtures write only under the sandbox `home`, `xdg`, `cwd`). The case instead sets core `path: ~/../cwd/vault/specs` and project `path: null` in the sandbox vault's own `config.yaml`, so both tiers come out of `resolve_tiers()` through the real config merge pointing at one directory — the DoD's "never by stubbing tiers" holds. The worker's hand mutation of the `seen` check failed the render case and was reverted.

## D12 — M06 grep residue

M06's `rg -n '_lessons' src/config.yaml playbooks/setup` still matches four lines under `playbooks/setup/_specs/` — playbook-authoring design history, intentionally stale per CLAUDE.md and excluded by the plan's own Final Verification grep. Left as is.

## D13 — M07 decisions

- **Link text for a removed lesson without a retro.** C5 says plain text; the rule schema requires a link in every `## Follows from` item (mdcheck fails rule/0015 otherwise). The replacement reads `` `_lessons/{file}` (removed by [migration 004](https://github.com/A/claude-booping/blob/master/migrations/004_lessons_to_rules/migration.md)) `` — C5's wording with "migration 004" linked to the shipped migration on the repo's default branch `master`; converted rules without a retro link the same URL under `## Follows from`.
- **Fixture marker force-added.** `.booping` is gitignored repo-wide; the fixture's `repo/.booping` is committed with `git add -f`, as `playbooks/_fixtures/vault/.booping` already is.
- **Own vault marker not committed.** The repo-root `.booping` (now `latest_migration: 4`) is gitignored local state; another checkout of this branch STOPs its renders until it runs `/playbook migrate`, which is the migration's intended path.
- **Fixture location.** `check.sh` requires the copy at `/tmp/m004` because the fixture config pins `home_dir: /tmp/m004/home`.
- **Idempotence diff.** The second application's `diff -r` differs only in `vault/.booping.log` (the CLI invocation log every `booping` call appends to); empty otherwise.
- **anton:rule/0001–0003** were not reported dangling: their `sources` resolve through `{home_dir}/claude-booping` to the main checkout, which still holds the lessons until this branch merges. The owner fixes them by hand (C5). `~/Dev/@A/notes` status identical before and after.
