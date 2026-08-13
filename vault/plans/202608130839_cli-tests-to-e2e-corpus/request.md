# Request

> let's continue refactoring tests, take another cli command and cover it by e2e

## Task type

`refactoring` — the test layout changes, the shipped behaviour does not. Rules out `feature`: no new capability, flag or subcommand; the commands under test are not touched. Rules out `bug`: nothing diverges from expected behaviour — the units pass today, they are simply the wrong tier for surfaces that are pure process contracts.

## Problem

The e2e txtar corpus covers two commands — `scaffold` (38 cases) and `frontmatter-update` (34 cases). Everything else is still pytest units under `booping-python/tests/`, and for CLI surfaces those units are burden: each file re-implements its own `subprocess.run` harness, its own tmp-dir fixture and its own assertion style, to test a contract that is entirely argv in → files, stdout, stderr, exit code out. That is what a txtar case expresses directly.

Three files are already subprocess-driven against `bin/booping` and carry no library imports worth keeping:

| file | tests | surface |
| --- | --- | --- |
| `tests/commands/config_get_test.py` | 7 | dotted-key read across the three config tiers |
| `tests/commands/marker_set_test.py` | 9 | marker write, `@latest` resolution, formatting preservation, stderr receipt |
| `tests/commands/query_test.py` | 35 | 27 subprocess CLI tests + 8 `parse_where` argv-parsing units |

A fourth, `tests/query_test.py` (57 tests), is library-level — it imports `booping.query` internals — but most of what it asserts is query *semantics* reachable through `booping query`, because a case and the engine read the same YAML spec.

## Clarifications and Decisions

- Scope is the test tier only. No production code changes, no CLI surface changes, no config schema changes.
- `config-get` is kept as a command and reclassified as an extension API: it survives on read-back-after-write (setup writes the global config mid-run, so a render-time value is stale by construction) and on user-authored `_scripts/` hooks, for which it is the only way to read project config without importing `booping` internals.
- Migrate all four files' CLI-observable coverage into the corpus: `config-get`, `marker-set`, `query`.
- `parse_where`'s 8 units move too — argv clause shapes are observable through `--where` at the CLI.
- **The division of tiers**: e2e cases own query *semantics* — discovery, `where`, ordering operators, `sort`, `columns`, `root`, spec validation, output formats, error messages and exit codes — since a case and the engine read the same YAML query spec. Units keep only *that query objects work inside templates*: `Row` under Jinja and the `| query` filter, which no `booping query` invocation reaches.
- `tests/commands/config_get_test.py`, `tests/commands/marker_set_test.py` and `tests/commands/query_test.py` are deleted whole. `tests/query_test.py` shrinks to the template-integration tests rather than disappearing.
- Deletion follows the same cross-check discipline as the `scaffold` and `frontmatter-update` migrations: every unit assertion accounted for in a case before its file goes.
- Migration only otherwise: no txtar spec change, no upstream `pytest-txtar` work, no corpus reshape.

### Explicitly out of scope (raised, deferred by decision)

- Renaming `core.plans.milestones.table_columns` → `columns` so the mapping becomes a valid `QuerySpec`. Researched and confirmed as the right fix, but it is production work, not test work.
- Splitting `booping query --project`, which conflates *where to glob* with *which config tiers to merge* (`context/__init__.py:76`). This is why `refresh-milestone-table` shells out to `config-get` and hand-assembles the query rather than addressing the spec by dotted path: `--project {plan}` would pin the config to core only and silently drop a vault-level override of the spec — behaviour `tests/scripts/refresh_milestone_table_test.py:142` asserts today. Its own grooming run.
- A noun-verb CLI shape (`booping config get`, `booping config query`) as the eventual home for the extension-API reclassification. Horizon only; it argues for pinning these contracts in e2e first.
