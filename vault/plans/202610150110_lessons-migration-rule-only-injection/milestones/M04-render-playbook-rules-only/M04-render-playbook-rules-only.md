---
id: "04"
title: "render-playbook and the context load rules only; --no-lessons removed"
sp: 5
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M04: render-playbook and the context load rules only; --no-lessons removed

`render-playbook` (composed and `--step`, inline steps included) injects `## Rules` only: no `## Lessons` section, no lesson notice, no `--no-lessons` flag; the context no longer loads `{home_dir}/_lessons/` or `{vault}/_lessons/`.

**Scope**: `booping-python/src/booping/commands/render_playbook.py` — remove the `--no-lessons` flag, the `include_lessons` parameter of `compose()` / `compose_step()` and every branch it gates, `_lesson_notices()`, `_render_lessons()`, `_targeted()` for lessons, the `_UNKNOWN_STEP_TARGET` / `_LEGACY_LESSONS` / `_UNTARGETED_LESSON` notices (`clarifications.md` C11), the `Lesson` import; keep the `_Targeted` protocol and `playbook_targeted` / `step_targeted` (rules use them). Delete `src/templates/_partials/_playbook_lessons.j2`. `booping-python/src/booping/context/__init__.py` — remove the `targeted_lessons` field and its load; `context/lesson.py` — delete `load_targeted` and `_merge_by_filename` (the `Lesson` model, `load_dir` and `load_all` stay: `Context.lessons`, the legacy `{vault}/lessons/` cross-check set, is parked — C3). `context/playbook.py` — delete `legacy_lesson_dirs`; `context/project.py:87` comment drops `_lessons/`. Passing `--no-lessons` is an argparse error from now on (C2 of plan 202610142150: removed, not aliased).

Tests: integration through the txtar corpus. Delete the lesson-only cases under `booping-python/e2e/cases/render-playbook/`: `a-lesson-body-is-never-jinja-rendered`, `a-lesson-targeting-another-playbook-renders-nowhere`, `a-lesson-targeting-an-unknown-step-is-a-non-blocking-note`, `an-unknown-step-still-exits-1-with-lessons-present`, `an-untargeted-lesson-is-a-non-blocking-note`, `a-playbook-with-no-lessons-renders-no-lessons-section`, `a-step-targeted-lesson-reaches-only-the-step-surface`, `legacy-lesson-directories-are-a-non-blocking-note`, `step-lessons-are-appended-to-an-inlined-step-section`, `step-lessons-render-on-a-jinja-playbook`, `the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson`, `the-no-lessons-flag-removes-the-composed-lessons-section`, `the-no-lessons-flag-removes-the-step-lesson-block`. Rename and rewrite `step-rules-are-appended-to-an-inlined-step-section-before-its-lessons` and `the-rules-section-sits-directly-before-the-lessons-section` so they assert the rules placement alone. `help-lists-every-flag-including-no-lessons` → `help-lists-every-flag`, without `--no-lessons`. One new case: a vault holding a targeted `_lessons/` file and a targeted rule renders the rule and no `## Lessons` and no lesson notice, on the composed and the `--step` surface. Any other case whose fixture carries `_lessons/` only incidentally (`a-playbook-name-in-two-roots-blocks-the-render`, `debug-context/an-attached-vault-assembles-without-error`) is checked and trimmed so it still asserts what its name says. Unit: delete `tests/context/assemble_test.py`'s `targeted_lessons` assertions and test, `tests/context/playbook_test.py`'s `legacy_lesson_dirs` tests; revisit `tests/rendering_test.py:207`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Code removal across render-playbook and the context as Scope lists; delete `_playbook_lessons.j2`. | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/src/booping/context/lesson.py`, `booping-python/src/booping/context/playbook.py`, `booping-python/src/booping/context/project.py`, `src/templates/_partials/_playbook_lessons.j2` | 3 | done |
| 4.2 | e2e and unit test changes as Scope lists, including the one new case with hand-written expected output. | `booping-python/e2e/cases/render-playbook/*.txtar`, `booping-python/e2e/cases/debug-context/an-attached-vault-assembles-without-error.txtar`, `booping-python/tests/context/assemble_test.py`, `booping-python/tests/context/playbook_test.py`, `booping-python/tests/rendering_test.py` | 2 | done |

## Definition of Done

### Task 4.1

- [x] `rg -n -i 'targeted_lessons|no.lessons|include_lessons|legacy_lesson|_playbook_lessons|load_targeted' booping-python/src src` prints nothing.
- [x] `bin/booping render-playbook groom --help` lists `--no-rules` and not `--no-lessons`; `bin/booping render-playbook groom --no-lessons` exits 2.
- [x] `bin/booping render-playbook groom` on this repo renders no `## Lessons` section while `vault/_lessons/` still exists.

### Task 4.2

- [x] Every case in Scope's delete list is gone; the renamed cases keep their rules assertions and lose every lessons line.
- [x] The new case's expected output is hand-written, not produced by running the code first.
- [x] `rg -l -i 'lesson' booping-python/e2e/cases/render-playbook` lists only the new case.

Return: the list of changed files, nothing else.

## References

- `booping-python/e2e/cases/render-playbook/the-no-rules-flag-removes-the-step-rules-block.txtar` — case shape with a rules fixture.
- `booping-python/e2e/cases/render-playbook/the-rules-section-sits-directly-before-the-lessons-section.txtar` — the case to rewrite.

## Verify

`just e2e -k "render and playbook"`
