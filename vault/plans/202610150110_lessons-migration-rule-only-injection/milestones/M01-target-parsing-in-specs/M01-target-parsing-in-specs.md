---
id: "01"
title: "Target parsing lives in specs/targets.py"
sp: 3
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M01: Target parsing lives in specs/targets.py

`parse_target` and its result types live in `booping-python/src/booping/specs/targets.py` as `Target`, `TargetRejection`, `parse_target`; nothing imports target parsing from `context/lesson.py` any more.

**Scope**: move `_NAME`, the four target regexes, `LessonTarget` (renamed `Target`), `TargetRejection` and `parse_target` out of `booping-python/src/booping/context/lesson.py` into a new `booping-python/src/booping/specs/targets.py`, unchanged in behaviour; repoint `specs/rules.py`, `specs/check.py`, `commands/render_playbook.py` and the remaining `context/lesson.py` (its `Lesson` model keeps parsing targets until M04) at it. Drop `check.py`'s unused `Lesson` import. Wording: `src/specs/README.md` `## Check` and the comment line of `booping-python/e2e/cases/specs/check-targets-must-pair-with-brief-and-parse.txtar` say "a target", not "a lesson target" (`clarifications.md` C10). No re-export shim in `context/lesson.py`.

Tests: the classifier's unit tests move with it to `booping-python/tests/specs/targets_test.py` (pure parsing with tricky branches — the one place a unit tier fits): playbook, `playbook/step`, `agent:{id}`, `skill:{name}`, and each rejection; the `specs check` targets e2e case stays green unchanged in behaviour.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Create `specs/targets.py` with the moved classifier (`LessonTarget` → `Target`); repoint every importer; delete the moved code from `context/lesson.py`. | `booping-python/src/booping/specs/targets.py`, `booping-python/src/booping/context/lesson.py`, `booping-python/src/booping/specs/rules.py`, `booping-python/src/booping/specs/check.py`, `booping-python/src/booping/commands/render_playbook.py` | 2 | done |
| 1.2 | Move the target-parsing unit tests to `tests/specs/targets_test.py` (from wherever they live today — `tests/context/lesson_test.py`, `tests/specs/rules_test.py`); reword the README sentence and the e2e case comment. | `booping-python/tests/specs/targets_test.py`, `src/specs/README.md`, `booping-python/e2e/cases/specs/check-targets-must-pair-with-brief-and-parse.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `rg -n 'LessonTarget|context.lesson import' booping-python/src` prints nothing.
- [x] `specs/targets.py` holds the only target regexes in the package.
- [x] No behaviour change: every existing e2e case passes without its expected output edited.

### Task 1.2

- [x] `tests/specs/targets_test.py` covers each accepted form and each rejection, parametrized, expectations hand-written.
- [x] `rg -n -i 'lesson target' src/specs booping-python/e2e` prints nothing.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/specs/tiers.py` — module shape in the `specs` package.
- `booping-python/tests/specs/tiers_test.py` — unit-test shape in `tests/specs/`.

## Verify

`cd booping-python && uv run pytest tests/specs -q`
