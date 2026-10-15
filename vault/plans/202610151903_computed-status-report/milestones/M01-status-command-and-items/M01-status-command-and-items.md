---
id: "01"
title: "booping status command and the items section"
sp: 3
status: in-progress
plan: "plans/202610151903_computed-status-report/index.md"
---

# M01: booping status command and the items section

`booping status` exists: with no argument it prints the `items:` short line; `booping status items` (or `--detail`) prints `## items` with `booping items list`'s table.

**Scope**: create `booping-python/src/booping/status.py` — a frozen `Section` dataclass (`name`, `summary(ctx) -> str`, `detail(ctx) -> str`) and the ordered tuple `SECTIONS`, holding only `items` in this milestone; M02 and M03 append `plans`, `ideas`, `records`, `marks` in the canonical order `items, ideas, plans, records, marks`, and part (3) of the request will append `runs`. `summary`/`detail` take a `Context` and return text; nothing in the module prints or writes. The items section reads `open_items.machine`, `open_statuses`, `index_rows` and `index_table` (no copy of their logic): summary `items: {n} {status}, … — request {r}, backlog {b}, spec gap {g}` — statuses in `open_statuses` order, zero counts omitted; `request`/`backlog` are the request-source constants already defined in `open_items.py`, spec gap counts every other source; no non-terminal item → `items: none`. Detail is `index_table` of the non-terminal rows, or `none`.

Create `booping-python/src/booping/commands/status.py`: `add_parser(sub)` builds `status` with help `Print the project status computed from the vault — short by default, detail per section`, a positional `section` (`nargs="*"`, `choices` = the names in `SECTIONS`) and `--detail`. No section and no `--detail` → print each section's summary line. Otherwise print, for the named sections (all of them under `--detail`), deduplicated and in `SECTIONS` order, `## {name}`, a blank line, the detail body, sections separated by one blank line. Errors through the module's `_fail` (`error: {message}`, exit 1) for no attached project or no vault, the same message `items list` gives. Log once: `logger.log(vault=ctx.vault, subcommand="status", message="status {sections or 'short'}")`. Register in `booping-python/src/booping/cli.py` beside `items_cmd`.

Tests (integration tier, e2e corpus `booping-python/e2e/cases/status/`, expectations hand-derived from the fixture): short report over items in `open`, `planned` and a terminal status with `request`, `backlog` and `adr` sources; `items: none` on a vault with no items; `status items` detail equals `items list`'s table for the same fixture; `status --detail` with only `items` registered; `status bogus` exits 2 with argparse's invalid-choice error (text taken from the run, hand-checked); no project exits 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `status.py` with `Section`, `SECTIONS` and the items section; `commands/status.py` parser, printing, logging; registration. | `booping-python/src/booping/status.py`, `booping-python/src/booping/commands/status.py`, `booping-python/src/booping/cli.py` | 2 | pending |
| 1.2 | e2e cases for the items section, detail, bad section and no project. | `booping-python/e2e/cases/status/*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `bin/booping status --help` shows the positional `section` with its choices and `--detail`.
- [ ] `bin/booping status` in this repo prints one `items:` line in the locked shape.
- [ ] `status.py` imports from `booping.specs.open_items` and holds no item-status or source literal beyond the constants that module exports.

### Task 1.2

- [ ] `booping-python/e2e/cases/status/` holds the six cases above, all passing.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/commands/items.py` — command module shape, `_run_list`, `_fail`, logging; `booping-python/src/booping/cli.py` — registration.
- `booping-python/e2e/cases/items/list-shows-open-and-planned-items.txtar` — case shape and fixture items.
- `booping-python/e2e/README.md` — the case format.

## Verify

`cd booping-python && uv run pytest e2e/cases/status e2e/cases/items -q`
