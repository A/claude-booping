---
id: "03"
title: "add --record files an open item"
sp: 3
status: done
plan: "plans/202610151532_corrections-log/index.md"
---

# M03: add --record files an open item

`booping correction add --record REF` also files an open item with `source: correction` and links it from the entry.

**Scope**: `booping-python/src/booping/specs/open_items.py` — `"correction"` appended to `SOURCES`; `booping-python/src/booping/commands/specs.py` — the `--source` help names it. `booping-python/src/booping/correction.py` and `commands/correction.py` — `--record` validated per `index.md` `## I/O contract`; the item filed in-process through `open_items`' add function (no subprocess) with title `{step}: {said}` whitespace-normalised and truncated at 100 chars with `…` (open_items' `truncate`), `direction: conflict`, `source: correction`, `record: REF`, body the one line `Logged as [{sidecar}#R{n}]({link relative to the item})`; the entry gets `**Record:**` per `index.md` `### corrections.md`; stdout gains the item path as its second line. A bad `--record` is exit 1 with neither file written.

Tests: integration tier, txtar cases — `--record value/0007` writes the entry with `**Record:**` and `open-items/OI-0001.md` with the fields above, stdout two lines; `--record booping:rule/0002` keeps the namespace; `--record nonsense` is exit 1, nothing written; `booping specs open-items add --source correction` by hand is accepted.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `correction` source value and its help. | `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/commands/specs.py` | 1 | done |
| 3.2 | `--record` on `correction add`: validation, item filing, entry and stdout. | `booping-python/src/booping/correction.py`, `booping-python/src/booping/commands/correction.py` | 1 | done |
| 3.3 | The txtar cases named in Tests. | `booping-python/e2e/cases/correction/add-record-*.txtar`, `booping-python/e2e/cases/specs/open-items-add-correction-source.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `booping specs open-items add --help` names `correction` among the sources.

### Task 3.2

- [x] The item file matches the open-item scaffold key for key with the values in Scope; the entry's link and the item's back link resolve relative to their own files.
- [x] A bad `--record` writes neither the entry nor an item.

### Task 3.3

- [x] One case per behaviour named in Tests.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/specs/open_items.py` — `SOURCES`, the add function, `truncate`.
- `booping-python/e2e/cases/specs/open-items-add-by-hand-files-the-first-item.txtar` — expected open-item file.

## Verify

`just e2e -k "correction and record or open-items-add-correction"`
