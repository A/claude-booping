# Framing brief

## Request

> we done setting up and refactoring e2e tests on scaffold command. Now give me next command to refactor from fragile unit tests to e2e.

## Task type

`refactoring` — internal test-structure change, no user-visible behavior change. Not `feature`: no new capability, the CLI contract stays identical. Not `bug`: nothing observed diverging from expected; the units pass, they are merely fragile.

## Problem

The e2e contract-corpus pilot (plan 202608111422) converted `scaffold`'s tests into a txtar corpus under `booping-python/e2e/cases/scaffold/`, and the runner extraction (plan 202608121206) moved the runner into the published `pytest-txtar` plugin. Every other CLI command still lives on unit tests under `booping-python/tests/commands/`, which assert through Python internals rather than the CLI contract.

Next candidate: `frontmatter-update` — 571 lines of unit tests (`tests/commands/frontmatter_update_test.py`), the largest single-command unit suite after the playbook pair, and the same contract shape scaffold had: argv in → file mutation + unified-diff on stdout → exit code. Its tests migrate to txtar cases under `e2e/cases/frontmatter-update/`; units covering the CLI contract get deleted.

## Clarifications and Decisions

- Next command: `frontmatter-update` — largest fragile suite, cleanest txtar fit (argv → file mutation + diff stdout).
- Unit fate: delete `frontmatter_update_test.py` wholesale — corpus is the contract, same as the scaffold pilot.
- Scope: single command this sprint; `marker-set` and others groomed in their own runs.
