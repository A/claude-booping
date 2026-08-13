---
id: "02"
title: "marker-set corpus — writes, @latest, formatting preservation, log"
sp: 3
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M02: marker-set corpus — writes, @latest, formatting preservation, log

`booping marker-set` is covered by txtar cases under `e2e/cases/marker-set/`, and its unit file is gone.

**Scope**: the `marker-set` subcommand only. Files: new `booping-python/e2e/cases/marker-set/*.txtar`; deleted `booping-python/tests/commands/marker_set_test.py`. The marker under test is a `fixtures/cwd/.booping` carrying a comment and a quoted value, so preservation is asserted by the `expected/cwd/.booping` section rather than by parsing.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Write cases: sets a key and prints one stderr line, stdout empty; changes only the target line, leaving comments, quoting and key order intact; the value is absolute, never incremented; a run from a subdirectory finds the marker by walking up | `booping-python/e2e/cases/marker-set/*.txtar` | 1 | done |
| 2.2 | Resolution and read-back cases: `@latest` resolves to the highest shipped migration id; a second `cmd` line reads the written value back with `config-get`, proving the write reaches the merged config; one `.booping.log` line is appended with the timestamp wildcarded | `booping-python/e2e/cases/marker-set/*.txtar` | 1 | done |
| 2.3 | Error cases: a malformed pair exits 1; a non-integer `latest_migration` exits 1; no marker anywhere up the tree exits 2. Then cross-check every assertion in `marker_set_test.py` against a named case and delete the file | `booping-python/e2e/cases/marker-set/*.txtar`, `booping-python/tests/commands/marker_set_test.py` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `booping marker-set latest_migration=3` exits 0, prints nothing on stdout, and prints one line on stderr naming the marker and the pair.
- [x] The `expected/cwd/.booping` section shows the fixture's leading comment, its quoted `project_name` and its key order byte-for-byte unchanged, with only the target line differing.
- [x] Setting an id twice in a row lands the literal value both times — the second write does not increment or accumulate.
- Descoped: a case whose `cmd` runs in a nested fixture directory — `pytest-txtar` runs every `cmd` in the single `cwd_root` (`sandbox.py:49`, `TxtarSpec.cwd_root`) and per-case cwd would be an upstream change this plan puts out of scope. Marker walk-up stays covered by `tests/context/project_test.py::test_load_cwd_from_subdirectory_walks_up`.

### Task 2.2

- [x] `booping marker-set latest_migration=@latest` writes the highest `id` among the plugin's shipped `migrations/*/migration.md`, asserted by the resulting marker rather than a hardcoded number where the wildcard suffices.
- [x] A two-line case (`marker-set …` then `config-get …`, or `debug-context`) shows the written value resolving through the project tier; the first line's exit code is 0 and the last line's is asserted.
- [x] `expected/cwd/{vault}/.booping.log` carries exactly one appended line, its timestamp covered by `[..]`.

### Task 2.3

- [x] A pair with no `=` exits 1 with a message naming the malformed argument.
- [x] `latest_migration=abc` exits 1 and the marker on disk is unchanged.
- [x] A run with no `.booping` anywhere up the tree exits 2 with a message saying so.
- [x] A cross-check table in the sprint's commit message or the milestone body maps each of the 9 tests in `marker_set_test.py` to the case that replaces it.
- [x] `booping-python/tests/commands/marker_set_test.py` is deleted and `grep -rn marker_set_test booping-python` returns nothing.

## Verify

```
cd booping-python && uv run pytest e2e -k marker-set
```

Every case passes with no `--txtar-update` needed, and a second run with `--txtar-update` leaves the working tree clean.
