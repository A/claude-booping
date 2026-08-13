---
id: "06"
title: "render-playbook lessons surfaces"
sp: 3
status: done
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M06: render-playbook lessons surfaces

Lesson injection — which target reaches which surface, in what format, and which lesson fault notices — is pinned by txtar cases.

**Scope**: `render-playbook` lesson discovery and rendering, including `--no-lessons`. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. Ported from the `lessons` section of `tests/test_render_playbook.py` (lines 1313–1634) plus the inline-surface case left by M04. Lessons are planted as markdown files with a `targets:` list under `fixtures/home/Claude/_lessons/` and `fixtures/cwd/{vault}/_lessons/`, so both discovery roots are expressible without touching the plugin.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Composed-surface cases: the `## Lessons` section's locked format and its placement between preamble and step table, a lesson targeting the playbook rendering there, no lessons producing no section, and a lesson body containing Jinja braces staying unrendered | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 6.2 | Step-surface and routing cases: a `{playbook}/{step}` target reaching the `--step` render in its locked format and not the composed one, a `{playbook}` target absent from the step surface, a lesson targeting a different playbook rendering nowhere, step lessons on a Jinja playbook, step lessons on the inline surface, and `--no-lessons` suppressing both surfaces | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 6.3 | Lesson notice and flag cases: an unknown step target as a non-blocking note, an untargeted lesson note, the legacy lesson-directory note, a clean fixture producing neither, a name clash across roots as a blocking notice, `--help` listing `--no-lessons`, and an unknown `--step` still exiting 1 with lessons present | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |

## Definition of Done

### Task 6.1

- [x] The `## Lessons` section is pinned in full — its count sentence, the per-lesson heading shape, and the body — for a fixture with two lessons.
- [x] The section appears after the preamble and before `## Playbook Steps`, asserted by pinning the whole stdout.
- [x] A fixture with no lessons renders no `## Lessons` heading.
- [x] A lesson body containing `{{ … }}` renders those braces literally, on a `jinja: true` playbook.

### Task 6.2

- [x] A `{playbook}/{step}` lesson appears in that step's `--step` output in its locked format and is absent from the composed render's step section.
- [x] A `{playbook}` lesson is absent from every `--step` output.
- [x] A lesson targeting another playbook appears in neither surface.
- [x] Step lessons render on a `jinja: true` playbook and are appended to an inlined step section.
- [x] `--no-lessons` removes the `## Lessons` section from the composed render and the step-lesson block from the `--step` render, asserted as two cases over one fixture.

### Task 6.3

- [x] Each notice fixture renders at exit 0 with its full text pinned; the unknown-step-target and untargeted-lesson notices are `**Note` lines and the render survives.
- [x] The name-clash fixture renders a `**STOP` notice naming both roots.
- [x] A fixture with neither a legacy directory nor an untargeted lesson renders no lesson notice at all.
- [x] `booping render-playbook --help` output pins the `--no-lessons` entry.
- [x] `--step nope` on a lesson-carrying playbook still exits 1.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
