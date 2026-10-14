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

None yet.

## D7 — M01 import grep

M01's DoD grep `rg -n 'LessonTarget|context.lesson import' booping-python/src` still matches two `from booping.context.lesson import Lesson` lines (`commands/render_playbook.py`, `context/__init__.py`): the `Lesson` model stays in `context/lesson.py` until M04 by the milestone's own scope. Read as "nothing imports target parsing from `context/lesson.py`" — the milestone's stated goal — which holds; `LessonTarget` is gone. The worker also repointed two test files outside the contract's list (`tests/templates/test_{agent,skill}_rules.py`), required once the shim was not kept. Full pytest, typecheck and both e2e corpora green with no expected output edited.
