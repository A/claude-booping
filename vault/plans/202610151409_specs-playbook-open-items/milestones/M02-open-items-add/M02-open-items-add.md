---
id: "02"
title: "booping specs open-items add files an item"
sp: 4
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M02: booping specs open-items add files an item

`booping specs open-items add` writes the next `open-items/OI-NNNN.md`, by hand or from an ADR's confirmation line, and prints its path.

**Scope**: `booping-python/src/booping/commands/specs.py` registers a nested `open-items` verb (`verbs.add_parser("open-items")` with its own subparsers — the group the later verbs join) and `add` with the flags of `index.md` `## I/O contract` → `add`. The logic lives in a new `booping-python/src/booping/specs/open_items.py`: next id = highest `OI-NNNN` in `{vault}/{core.specs.open_items.dir}` + 1, zero-padded to four (the `_run_next` rule in `specs.py`), file written through the `core.specs.open_items.scaffold` tree via the scaffold module in-process, `created_at` today. `--record adr/NNNN` without `--title`: resolve the ADR in the project tier, take the first bullet under `## Consequences` starting `Confirmation:`, title = its text after `Confirmation:` up to the first sentence end, truncated at 100 chars with `…`; defaults `direction: spec-to-code`, `source: adr`, `record: adr/NNNN#consequences`. `--direction` and `--source` accept only the values in `index.md` `## Architecture`. Every error is one `error: …` line on stderr, exit 1, nothing on stdout.

Tests: integration tier, txtar cases — add by hand prints `open-items/OI-0001.md` and writes the file; a second add numbers `OI-0002`; add from an ADR with a confirmation line; ADR without one is exit 1; bad `--direction` is exit 1; unknown ADR is exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `open-items` verb group and `add` by hand, numbering and scaffold. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/open_items.py` | 2 | done |
| 2.2 | `add --record adr/NNNN` confirmation extraction and defaults. | `booping-python/src/booping/specs/open_items.py` | 1 | done |
| 2.3 | The six txtar cases, expected output hand-written. | `booping-python/e2e/cases/specs/open-items-add-*.txtar` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `booping specs open-items --help` lists `add`; `add --help` lists `--title --direction --record --source --body`.
- [x] The file matches `index.md` "Open item file" key for key; stdout is the vault-relative path alone.

### Task 2.2

- [x] The title is the confirmation sentence, truncated at 100 chars with `…` when longer.
- [x] An explicit `--title`/`--direction`/`--source` overrides the ADR defaults.

### Task 2.3

- [x] Six cases, one per behaviour named in Tests; each failure case asserts stderr and an empty stdout.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/specs.py` — `add_parser`, `_run_next`, `_fail`: verb registration, numbering and error shape to copy.
- `booping-python/e2e/cases/specs/ls-on-a-missing-tier-directory-is-rejected.txtar` — case layout (`fixtures/cwd/.booping`, `vault/config.yaml`, `cmd`, `exit`, `stdout`, `stderr`).
- `src/specs/README.md` — the ADR body shape (`## Consequences`).

## Verify

`just e2e -k "open-items-add"`
