---
id: "01"
title: "booping items command group"
sp: 4
status: done
plan: "plans/202610151825_user-request-items/index.md"
---

# M01: booping items command group

The item store's six verbs answer as `booping items {add|scan|list|plan|close|reopen}`, behaving exactly as `booping specs open-items …` did; `booping specs open-items` no longer exists.

**Scope**: a pure move, no behaviour change. Create `booping-python/src/booping/commands/items.py` holding the `items` parser (`add`, `scan`, `list`, `plan`, `close`, `reopen` — same flags, same help text, same output) and their `_run_*` functions, moved out of `booping-python/src/booping/commands/specs.py`; register it in `booping-python/src/booping/cli.py` beside `correction` and `defaults`. Helpers both modules need (`_assemble`, `_select_tier`, `_known_types`, `_format_dir`, `_resolve`, `_fail`) are imported by `items.py` from `commands/specs.py`, not copied. The group help reads `File, list and move items — user requests and specs-to-code gaps under {vault}/open-items`. Log lines name the subcommand `items` (`logger.log(..., subcommand="items", message="add {rel}")` and likewise per verb). Every error message or notice that names the old command (`specs open-items …`) names `items …`, including in `booping-python/src/booping/specs/open_items.py` and `booping-python/src/booping/correction.py`.

Corpus: move the 21 cases `booping-python/e2e/cases/specs/open-items-*.txtar` to `booping-python/e2e/cases/items/`, dropping the `open-items-` prefix from the file name (`items/add-by-hand-files-the-first-item.txtar` …); in each, `booping specs open-items` becomes `booping items` on the `cmd` lines and in expected output. `playbooks/_scripts/open-items-follow-plan` calls `"$BOOPING" items "$verb" --plan …` and its header comment names `booping items close|reopen --plan …` as the reconcile; `booping-python/e2e/cases/playbook-transition/open-items-follow-plan-absorbs-a-failing-cli.txtar` follows.

Tests: integration tier, the moved e2e corpus — every existing case passes unchanged except the command name; one new case `items/specs-open-items-is-gone.txtar`: `booping specs open-items list` exits 2 with argparse's invalid-choice error on stderr (expected text taken from the run, hand-checked).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Move the parser and runners to `commands/items.py`, register the group, rename log subcommand and messages. | `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/cli.py`, `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/correction.py` | 2 | done |
| 1.2 | Move the 21 cases, update the follow-plan script and its case, add the gone case. | `booping-python/e2e/cases/items/*.txtar`, `booping-python/e2e/cases/playbook-transition/open-items-follow-plan-absorbs-a-failing-cli.txtar`, `playbooks/_scripts/open-items-follow-plan` | 2 | done |

## Definition of Done

### Task 1.1

- [x] `bin/booping items --help` lists the six verbs; each verb's `--help` matches its old `specs open-items` help.
- [x] `bin/booping specs --help` no longer lists `open-items`.
- [x] `grep -rn "specs open-items" booping-python/src` prints nothing.

### Task 1.2

- [x] `booping-python/e2e/cases/specs/` holds no `open-items-*` case; `booping-python/e2e/cases/items/` holds the 21 moved cases plus the gone case.
- [x] `grep -n "specs open-items" playbooks/_scripts/open-items-follow-plan` prints nothing.

Return: the list of changed, moved and created files, nothing else.

## References

- `booping-python/src/booping/commands/correction.py`, `booping-python/src/booping/commands/defaults.py` — shape of a top-level command module and its registration in `cli.py`.
- `booping-python/e2e/README.md` — the case format.

## Verify

`cd booping-python && uv run pytest e2e/cases/items e2e/cases/playbook-transition e2e/cases/correction -q`
