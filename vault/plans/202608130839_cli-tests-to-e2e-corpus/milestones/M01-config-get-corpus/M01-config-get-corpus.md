---
id: "01"
title: "config-get corpus — three config tiers, value shapes, errors"
sp: 3
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M01: config-get corpus — three config tiers, value shapes, errors

`booping config-get` is covered by txtar cases under `e2e/cases/config-get/`, and its unit file is gone.

**Scope**: the `config-get` subcommand only — no other command, no production code. Files: new `booping-python/e2e/cases/config-get/*.txtar`; deleted `booping-python/tests/commands/config_get_test.py`. The three config tiers reach the sandbox as core (the plugin's own `src/config.yaml`), global (`fixtures/xdg/booping/config.yaml`) and project (a `fixtures/cwd/.booping` marker plus the vault's `config.yaml`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Value-shape cases: a scalar string prints raw on one line and unexpanded (`home_dir`); an int at a dotted path; a mapping prints as YAML; a list prints as YAML | `booping-python/e2e/cases/config-get/*.txtar` | 1 | done |
| 1.2 | Tier cases: core-only value outside any project; a global-tier override winning over core; a project-tier override winning over global; a key present only in the project tier | `booping-python/e2e/cases/config-get/*.txtar` | 1 | done |
| 1.3 | Error and help cases: a missing nested key and a missing top-level key each exit 1 with `error: key not found: {key}` and empty stdout; `--help` lists the subcommand. Then cross-check every assertion in `config_get_test.py` against a named case and delete the file | `booping-python/e2e/cases/config-get/*.txtar`, `booping-python/tests/commands/config_get_test.py` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `booping config-get home_dir` prints the configured value followed by a newline, with `~` unexpanded and no quoting.
- [x] A dotted path to an integer (`core.sprint.default_threshold_sp`) prints the bare number.
- [x] A mapping (`core.plans.milestones`) prints as YAML with its keys in declaration order.
- [x] A list (`core.plans.glob`) prints as a YAML sequence.

### Task 1.2

- [x] A case with no `.booping` marker in `cwd` resolves core + global only and exits 0.
- [x] A `fixtures/xdg/booping/config.yaml` setting `home_dir` wins over the core default.
- [x] A project-tier `config.yaml` value wins over the same key set in the global tier.
- [x] A key that exists only in the project tier resolves, proving the merge is a deep merge and not a tier swap.

### Task 1.3

- [x] `booping config-get nope.key` and `booping config-get nope` both exit 1, print nothing on stdout, and print `error: key not found: {key}` on stderr.
- [x] `booping config-get --help` exits 0 and its output names the dotted-key argument.
- [x] A cross-check table in the sprint's commit message or the milestone body maps each of the 7 tests in `config_get_test.py` to the case that replaces it.
- [x] `booping-python/tests/commands/config_get_test.py` is deleted and `grep -rn config_get_test booping-python` returns nothing.

## Verify

```
cd booping-python && uv run pytest e2e -k config-get
```

Every case passes with no `--txtar-update` needed, and a second `uv run pytest e2e -k config-get --txtar-update` leaves the working tree clean.
