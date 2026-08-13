---
title: "Migrate config-get, marker-set and query tests to the txtar e2e corpus"
type: "refactoring"
status: in-progress
sp: 25
related_to: null
created: 2026-08-13 09:21
planned: null
started: 2026-08-13 10:13
completed: null
code_reviews: []
sessions:
- 6508e2be-210f-48b1-8d27-38655f5cc56a
- 4ab6841d-6dfd-46ae-bd29-e1e3cc653214
retro: null
summary: config-get, marker-set and query units become txtar e2e cases; units 
  keep only query-in-templates coverage
commit: 849d82a42dd675d94c39b96f1e977f2e411774bf
agents.cross-review: ab9126cf4287fa199
reviewed_at: 2026-08-13 09:47
---

# Migrate config-get, marker-set and query tests to the txtar e2e corpus

## Context

Three commands are still covered by hand-rolled pytest units that each re-implement the same harness — a `subprocess.run(bin/booping)` wrapper, a tmp-dir vault fixture, an assertion style — to test contracts that are entirely argv in → files, stdout, stderr, exit code out: `tests/commands/config_get_test.py` (7 tests), `tests/commands/marker_set_test.py` (9), `tests/commands/query_test.py` (35). A fourth, `tests/query_test.py` (57 tests), reaches the same query semantics one layer down, through direct `booping.query` imports.

The pilot (plan 202608111422) established the txtar corpus for `scaffold`, the runner extraction (plan 202608121206) moved the runner into the published `pytest-txtar` 0.1.0, and the `frontmatter-update` migration (plan 202608121417) proved the port-then-delete loop on 34 cases. This plan applies that loop to `config-get`, `marker-set` and `query`, and draws the tier line for the library-level file. No user-visible behavior change, no production code touched.

## Decisions

- **The tier line**: e2e cases own query *semantics* — discovery, `where`, ordering operators, `sort`, `columns`, `root`, spec validation, output formats, error text and exit codes. A case and the engine read the same YAML spec, so the CLI observes all of it. Units keep only *that query objects work inside templates*: `Row` under Jinja and the `| query` filter, which no `booping query` invocation reaches (user call).
- **Unit fate**: `config_get_test.py`, `marker_set_test.py` and `commands/query_test.py` are deleted wholesale after cross-check. `tests/query_test.py` shrinks to its template-integration classes rather than disappearing.
- **`parse_where`'s 8 units migrate**: every clause shape it asserts (`k=v`, `k!=v`, `k:in=a, b`, `k=a=b`, `id:gt=-1`, malformed pairs, empty ordering operand) is observable through `--where` at the CLI, as rows returned or as the error message and exit code.
- **Deletion placement**: `config-get` and `marker-set` each delete their own unit file inside their own milestone — the files are independent and the cross-check is small. `query`'s two files interlock, so their cross-check and deletion land together in the closing milestone.
- **Fixture economy**: `pytest-txtar` has no shared fixtures — each case restates its tree. Cases carry only the files they need, never the whole 4-file vault fixture the units share, or the corpus bloats without adding signal.
- **Read-back chains**: `marker-set`'s effect is asserted by a second `cmd` line (`marker-set …` then `config-get …`) rather than a second mechanism — the format concatenates output and compares the last line's exit code.
- **Gap cases are in scope, behavior fixes are not**: a behavior the units never covered gets a case; a bug found while porting is recorded in the milestone, not fixed here.

## Architecture

Cases live in `booping-python/e2e/cases/{config-get,marker-set,query}/*.txtar`, one kebab-named file per behavior, collected by the `pytest-txtar` plugin through the existing `e2e/conftest.py` spec — `commands={booping: bin/booping}`, `roots=(home, xdg, cwd)`, `cwd_root=cwd`, `env={HOME: home, XDG_CONFIG_HOME: xdg}`. That spec is unchanged by this plan: no runner work, no new root, no new token.

The three config tiers map onto the sandbox directly, which is what makes `config-get` expressible at all: core is the plugin's own `src/config.yaml`, the global tier is `fixtures/xdg/booping/config.yaml`, and the project tier is a `fixtures/cwd/.booping` marker plus the vault's `config.yaml` under `fixtures/cwd/`. `query`'s vault-relative globs resolve against that same attached vault, or against `--project` when a case pins one.

Volatile spans use the `[..]` wildcard (log timestamps); sandbox absolute paths normalize to `{HOME}` / `{XDG}` / `{CWD}`. Rebaseline flow: `cd booping-python && uv run pytest e2e --txtar-update -k <expr>`. Runner: `just e2e`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [config-get corpus — three config tiers, value shapes, errors](milestones/M01-config-get-corpus/M01-config-get-corpus.md) | 3 | done |
| 02 | [marker-set corpus — writes, @latest, formatting preservation, log](milestones/M02-marker-set-corpus/M02-marker-set-corpus.md) | 3 | done |
| 03 | [query corpus — spec addressing, flag errors, exit codes](milestones/M03-query-addressing-and-errors/M03-query-addressing-and-errors.md) | 4 | done |
| 04 | [query corpus — output formats, projection, frontmatter warnings](milestones/M04-query-output-and-projection/M04-query-output-and-projection.md) | 3 | pending |
| 05 | [query corpus — where clauses, ordering operators, sort](milestones/M05-query-filtering-semantics/M05-query-filtering-semantics.md) | 5 | pending |
| 06 | [query corpus — discovery, slug identity, spec validation, root](milestones/M06-query-discovery-and-spec-validation/M06-query-discovery-and-spec-validation.md) | 4 | pending |
| 07 | [Cross-check, delete the CLI query units, shrink the library file](milestones/M07-cross-check-and-unit-deletion/M07-cross-check-and-unit-deletion.md) | 3 | pending |

## I/O contract

The three CLI surfaces under test — unchanged by this plan, restated as the corpus contract.

**`booping config-get <dotted.key>`**

- **stdout**: scalars as raw text plus a newline, unexpanded; mappings and lists as YAML.
- **stderr**: `error: key not found: {key}`; `error: could not load config: {exc}`.
- **Exit codes**: `0` success, `1` key not found, `2` config load failure.
- **No project required** — resolves core + global outside any project.

**`booping marker-set <key>=<value>`**

- **stdout**: empty.
- **stderr**: one authoritative line naming the marker and the pair written.
- **Exit codes**: `0` success, non-zero on a missing marker or a malformed pair.
- **Side effects**: rewrites the repo's `.booping` preserving comments, quoting and key order; `@latest` resolves to the highest shipped migration id; appends one `.booping.log` line.

**`booping query (--config DOTTED.PATH | --glob PATTERN...) [--where CLAUSE]... [--sort FIELD] [--columns LIST] [--output table|json|yaml|paths] [--project PATH]`**

- **stdout**: `table` (default, pipes escaped and newlines collapsed), `json` (array of objects), `yaml`, or `paths` (one vault-relative path per line).
- **stderr**: `error: {message}` for spec and flag errors; `warning: skipping {path} — unparseable frontmatter ({exc})` per bad file, run continuing.
- **Exit codes**: `0` success including zero matches, `1` user error (malformed `--where`, unknown config path, non-mapping config value, both or neither addressing form, unknown `--output`, unknown spec key, unknown `root:`), `2` no vault resolved or unreadable vault.

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck, e2e).
- [ ] `cd booping-python && uv run pytest e2e` passes with no `--txtar-update` needed on a clean run.
- [ ] `tests/commands/config_get_test.py`, `tests/commands/marker_set_test.py` and `tests/commands/query_test.py` deleted; `grep -rn "config_get_test\|marker_set_test\|commands/query_test"` returns nothing.
- [ ] `tests/query_test.py` retains only template-integration coverage — no test in it asserts query semantics reachable through `booping query`.
- [ ] Unit-vs-corpus cross-check recorded in the DoD of each deleting milestone: every deleted assertion maps to a named case.

## Out of scope

- Renaming `core.plans.milestones.table_columns` → `columns` so the mapping validates as a `QuerySpec`, and splitting `booping query --project` (which conflates the glob root with the config tiers it merges, `context/__init__.py:76`). Both researched and confirmed as real, both production work — own grooming run.
- Any behavior change to `config-get`, `marker-set` or `query`, including a noun-verb CLI reshape (`booping config get`).
- Any change to `pytest-txtar`, the `e2e/conftest.py` spec, or the case format.
- The remaining unit files (`playbook_state_test.py`, `playbook_transition_test.py`, `render_test.py`, `build_test.py`, `test_render_playbook.py`) — own grooming runs.
- Permission and OS-level fault coverage — not expressible in the format ("fixtures carry content, not permissions"), and no test in scope asserts one.

## CLAUDE.md impact

No CLAUDE.md changes required — the `booping-python/` layout entry already describes `e2e/` as the contract corpus owned by the `pytest-txtar` spec, and `just e2e` is already documented. This plan adds cases under that structure and deletes units, changing neither.
