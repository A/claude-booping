---
id: "04"
title: "render-playbook Jinja modes and inline steps"
sp: 4
status: done
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M04: render-playbook Jinja modes and inline steps

Opt-in Jinja and the inline-steps surface — what renders through the context env, what stays verbatim, and which failure is blocking — are pinned by txtar cases.

**Scope**: `render-playbook` with `jinja: true` and `inline_steps: true` manifests and the `--inline-steps` flag. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. Ported from the `opt-in Jinja` and `inline steps` sections of `tests/test_render_playbook.py` (lines 779–1075), excluding the macro-stamp case (M05) and the step-lessons inline surface (M06). Fixture bodies that must fail to render carry deliberately broken Jinja, so their cases assert the in-band notice rather than a traceback.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Jinja-mode cases: a non-Jinja playbook's render is byte-identical to its authored bodies; a `jinja: true` preamble renders an expression and an include; a step's `summary` and `detached` values render through the context; a `detached` expression rendering empty falls back to a runner-performed step; a non-Jinja playbook's step frontmatter stays verbatim | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 4.2 | Fetch-line cases: a first-wave step and a later-wave step both show the `--step` fetch command, the fetch line's shape is identical across Jinja and non-Jinja playbooks, and no section anywhere renders the older read-a-link form | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 4.3 | Inline-steps cases: a manifest `inline_steps: true` and the `--inline-steps` flag each embed every non-detached step's body and drop its fetch line; detached steps keep fetch form; an inlined Jinja body renders through the context | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 4.4 | Render-failure cases: a broken inlined body is a blocking `**STOP` notice; the same break in an orphan step is not; a broken step frontmatter is an in-band stop; a Jinja playbook with no resolvable context stops; a broken step body does not abort the surrounding compose; and a `--step` fetch of a broken body reports the error in band at exit 0 | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] A non-Jinja fixture whose bodies contain `{{ … }}` renders those braces untouched.
- [x] A `jinja: true` fixture's preamble shows an evaluated expression and the content of an included partial.
- [x] A step whose `summary:` and `detached:` frontmatter values are Jinja expressions renders the evaluated values in both the step table and the step section.
- [x] A `detached:` expression evaluating to an empty string renders the step as runner-performed, with no delegation bullet.

### Task 4.2

- [x] Both a first-wave and a later-wave step section carry `booping render-playbook {name} --step {step}`.
- [x] Two cases over a Jinja and a non-Jinja fixture show identical fetch-line shapes.
- [x] No case's pinned stdout contains the read-a-link fetch form.

### Task 4.3

- [x] A manifest carrying `inline_steps: true` embeds every non-detached body in its section and no `Run:` fetch line appears for those steps.
- [x] The same fixture rendered with `--inline-steps` instead of the manifest key produces the same stdout, asserted as two cases over one fixture.
- [x] A detached step in an inline render keeps its fetch line.
- [x] An inlined `jinja: true` body renders its expressions through the context rather than embedding them raw.

### Task 4.4

- [x] A broken inlined body renders a `**STOP — tell the user:**` notice naming the step, at exit 0.
- [x] The same broken body in a step wired into no graph renders only a `**Note` line, and the rest of the render survives.
- [x] A step whose frontmatter fails to parse under Jinja renders an in-band stop naming the step.
- [x] A `jinja: true` playbook rendered with no vault attached renders cleanly at exit 0 rather than a traceback. (The original wording asked for the `_NO_CONTEXT` stop notice; that path is unreachable from the CLI — `render_playbook._run` always passes an assembled context — so it is recorded as not-portable in M08's cross-check rather than cased.)
- [x] `--step` on a broken body prints the in-band error at exit 0.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
