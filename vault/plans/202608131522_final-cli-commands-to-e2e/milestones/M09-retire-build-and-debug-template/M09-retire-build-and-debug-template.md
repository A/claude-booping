---
id: "09"
title: "retiring build and debug-template"
sp: 4
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M09: retiring build and debug-template

The build stage and the `debug-template` stub are deleted, the plugin drops to one rendering pipeline, and every reference to either goes with them.

**Scope**: the `build` and `debug-template` subcommands, the build-time template tree, and every document describing them. Files: deleted `booping-python/src/booping/commands/build.py`, `booping-python/tests/commands/build_test.py`, `src/files/`, `src/config_files.yaml`; edited `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/debug.py`, `justfile`, `CLAUDE.md`, `docs/plan_templates/claude_skill.md`, `vault/docs/_specs/targets.md`.

The three build outputs — `skills/playbook/SKILL.md`, `agents/booping-developer.md`, `agents/booping-researcher.md` — must not change by a single byte. Each source template's only Jinja expression is an `effort:` frontmatter value, and the committed output already carries that value inlined, so the templates are deleted rather than promoted, and the outputs simply stop having an upstream. `git diff -- skills/ agents/` staying empty is the check that this held.

`booping/commands/debug.py` survives — it also owns `debug-context`. Only the `debug-template` parser registration and its `_not_implemented` handler are removed.

`tests/commands/` becomes empty except for the one surviving unit M04 placed there; if that file is the only occupant, leave it — the directory disappearing is not the goal, the CLI-shaped tests leaving it is.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Delete `commands/build.py`, its import and registration in `cli.py`, and `tests/commands/build_test.py`; remove the `debug-template` parser registration and `_not_implemented` from `commands/debug.py` | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/build.py`, `booping-python/src/booping/commands/debug.py`, `booping-python/tests/commands/build_test.py` | 1 | pending |
| 9.2 | Delete `src/files/` and `src/config_files.yaml`, and delete the `build` and `dev` recipes from the justfile — `dev` watches only build inputs and has no other job | `src/files/`, `src/config_files.yaml`, `justfile` | 1 | pending |
| 9.3 | Rewrite CLAUDE.md: drop the `just build` command line, drop the `src/config_files.yaml` and `src/files/<rel>.j2` layout entries, rewrite the `skills/`+`agents/` entry from build artefacts to hand-authored thin shells, drop both retired subcommands from the CLI list, collapse `## Rendering pipelines` to the single runtime stage, strip the `src/files/**` clause and the drift-signal sentence from the editing conventions, and repoint the closing principle at `skills/playbook/SKILL.md` | `CLAUDE.md` | 1 | pending |
| 9.4 | Sweep the remaining references: the `just build` item in the claude-skill plan template's checklist, and the two build-artefact lines in the vault's docs spec | `docs/plan_templates/claude_skill.md`, `vault/docs/_specs/targets.md` | 1 | pending |

## Definition of Done

### Task 9.1

- [ ] `bin/booping --help` lists eleven subcommands with no `build` and no `debug-template`.
- [ ] `bin/booping build` and `bin/booping debug-template` both fail as unknown subcommands.
- [ ] `bin/booping debug-context` still works.
- [ ] `uv run ruff check src/booping/cli.py src/booping/commands/debug.py` is clean — no unused import left behind by either deletion.

### Task 9.2

- [ ] Before deleting anything, `git status --porcelain skills/ agents/` is empty and the three files carry `effort: medium`, `effort: medium` and `effort: high` respectively — if any drifted mid-sprint, resolve that before proceeding rather than deleting the only source that explains the value.
- [ ] `src/files/` and `src/config_files.yaml` no longer exist.
- [ ] `just --list` shows neither `build` nor `dev`.
- [ ] `git diff --stat -- skills/ agents/` is empty: the three rendered files are byte-identical to their pre-milestone state.

### Task 9.3

- [ ] CLAUDE.md contains no occurrence of `src/files`, `config_files`, `just build` or `booping build`.
- [ ] `## Rendering pipelines` describes one stage — runtime rendering at skill load — and is no longer a numbered list of two.
- [ ] The `skills/<name>/SKILL.md`, `agents/<name>.md` layout entry describes them as hand-authored, with the "never hand-edit" instruction gone.
- [ ] The editing-conventions bullet no longer names `git diff -- skills/ agents/` as a drift signal.

### Task 9.4

- [ ] `docs/plan_templates/claude_skill.md`'s checklist item names only the runtime render, not `just build`.
- [ ] `vault/docs/_specs/targets.md` describes `skills/**/SKILL.md` and `agents/*.md` as source, and no longer lists `src/files/**` as a Jinja source.
- [ ] `rg -n "booping build|src/files|config_files|just build" --glob '!vault/plans/**'` returns nothing.

## Verify

```
bin/booping --help && just --list && git diff --stat -- skills/ agents/ && rg -n "booping build|src/files|config_files|just build" --glob '!vault/plans/**'
```

Help lists eleven subcommands with no `build` and no `debug-template`, `just --list` shows neither retired recipe, `git diff --stat` prints nothing for the three rendered files, and the final `rg` finds no surviving reference (exit 1, no matches).
