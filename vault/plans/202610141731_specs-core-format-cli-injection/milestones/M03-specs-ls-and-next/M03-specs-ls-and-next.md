---
id: "03"
title: "booping specs ls and next"
sp: 5
status: done
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M03: booping specs ls and next

`booping specs ls [--tier] [--type]` lists a tier's records and `booping specs next {type} [--tier]` prints the next free ref, exactly as the plan's I/O contract states.

**Scope**: new nested argparse group `specs` registered in `booping-python/src/booping/cli.py`, verbs in `booping-python/src/booping/commands/specs.py` (`add_parser(sub)` creating the group with `add_subparsers(dest="specs_verb", metavar="<verb>", required=True)`), built on M02's `resolve_tiers`, `types` and `load_tier`. Errors print `error: {message}` to stderr with the plan's exit codes, reusing the `_fail` shape from `commands/scaffold.py`. The verb logs one line via `booping.logger.log` when a vault is attached. `check` is a later milestone: do not register it here. Tests: txtar e2e cases under `booping-python/e2e/cases/specs/` for the CLI surface — `ls` over a project tier with two types (sort order, `-` for a value's status), `ls --type`, `ls --tier global` (fixture records under `home/Claude/_specs/{type}/` — `home_dir` defaults to `~/Claude/` — and the namespace pinned in `xdg/booping/config.yaml` as `core.specs.tiers.global.namespace`), `ls` on a missing tier directory (exit 1), `ls --type nope` (exit 1), `next` on a populated type, on an empty type (`{type}/0001`), with a gap in the numbers (highest + 1, not the gap), unknown type (exit 1).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `specs` group + `ls` verb with `--tier` (choices `core`, `global`, `project`, default `project`) and `--type`; output line `{type}/{NNNN}  {status}  {summary}`; e2e cases for `ls` per Scope. | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/specs.py`, `booping-python/e2e/cases/specs/ls-*.txtar` | 3 | done |
| 3.2 | `next {type}` verb with `--tier`; e2e cases for `next` per Scope. | `booping-python/src/booping/commands/specs.py`, `booping-python/e2e/cases/specs/next-*.txtar` | 2 | done |

## Definition of Done

### Task 3.1

- [x] `bin/booping specs --help` lists the verbs; `bin/booping specs ls --help` shows `--tier` and `--type`.
- [x] From the repo root, `bin/booping specs ls --type value` prints one line per file in `vault/specs/value/`, each `value/{NNNN}  -  {summary}`.
- [x] Missing tier directory → stderr ``error: no specs for tier `{tier}` at {root}``, exit 1, empty stdout.
- [x] `--tier project` with no project attached → stderr ``error: tier `project` is not available here``, exit 1.
- [x] Unknown type → stderr ``error: unknown type `{t}`; known: adr, conflict, idea, reference, rule, runbook, story, value``, exit 1.

### Task 3.2

- [x] From the repo root, `bin/booping specs next adr` prints the highest number in `vault/specs/adr/` plus one.
- [x] Empty or missing type directory → `{type}/0001`, exit 0.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/config_get.py` — a command module's shape (`add_parser`, `_run`, error handling).
- `booping-python/src/booping/commands/scaffold.py` — the `_fail(message, code)` helper.
- `booping-python/e2e/cases/render-playbook/the-lessons-section-is-a-count-sentence-then-one-heading-per-lesson.txtar` — a case with `home`/`cwd` fixture trees; copy its `.booping` marker and vault layout for the project tier. Case format: `booping-python/e2e/conftest.py` and the pytest-txtar README.

## Verify

```
just e2e -k specs
```

All selected cases pass.
