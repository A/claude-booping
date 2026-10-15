---
id: "06"
title: "Docs and CLAUDE.md name the mode"
sp: 2
status: in-progress
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M06: Docs and CLAUDE.md name the mode

The public docs and the repo guide name `core.autonomy`, the `defaults.md` sidecar and the migrate exception.

**Scope**: `documentation/project_config.md` gains `### core.autonomy` under `## Shared keys, directly under core`, after `### core.auto_migrate`, in its shape: default, both values and what each does to gates and questions, the two things that still stop, the STOP on an unknown value, a link to `docs/defaults.md`'s published equivalent or the sidecar's description; its `### core.auto_migrate` `true` bullet quotes the amended notice. `documentation/playbook.md` line 225 bullet ("Review gates pause after the batch") gains one sentence: in an `autonomous` project gates are auto-confirmed and logged — link to the new section. `CLAUDE.md`: `## Commands` CLI list gains `defaults` (`add`); `## Config` gains a `core.autonomy` bullet; `## Lifecycle` gains a **Defaults** bullet beside **Corrections** (`defaults.md` beside the run artefact, written only by `booping defaults add`, format `docs/defaults.md`).

Audience filter (rule/0008): the two `documentation/` pages say only what a plugin user sets and sees — no partial names, no module paths; CLAUDE.md keeps its developer voice.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | The two public pages. | `documentation/project_config.md`, `documentation/playbook.md` | 1 | pending |
| 6.2 | CLAUDE.md, three sections. | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] The new section restates no literal from `src/config.yaml` beyond the key, its default and its two values.
- [ ] No partial name, module path or internal file appears in either page.
- [ ] `just docs` builds without warnings about the changed pages.

### Task 6.2

- [ ] CLAUDE.md names the key, the verb and the sidecar once each, in the sections above.

Return: the list of changed files, nothing else.

## References

- `documentation/project_config.md` `### core.auto_migrate` — section shape.
- `CLAUDE.md` `## Lifecycle` **Corrections** bullet — the sibling bullet shape.

## Verify

`just docs`
