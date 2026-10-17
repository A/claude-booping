---
id: "05"
title: "scan files items from marks and check findings"
sp: 4
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M05: scan files items from marks and check findings

`booping specs open-items scan` files one item per `[clarify]`/`[unknown]` mark and per `specs check` finding in a tier, skipping any already tracked.

**Scope**: `scan [--tier T]` (default `project`) in `booping-python/src/booping/commands/specs.py`, logic in `booping-python/src/booping/specs/open_items.py`, exactly per `index.md` `## I/O contract` → `scan`. Marks: a mark at the start of a list item or sentence (`src/specs/README.md` `## Marks`), record `{type}/{NNNN}#{slug of the nearest heading above}` (`slug` in `booping-python/src/booping/specs/site/markdown.py`, GitHub's heading anchor — reused, not reimplemented). Check findings: reuse `booping-python/src/booping/specs/check.py`'s finding list in-process, never its printed output. Dedup key `(source, record, title)` against every item file of any status. Items are filed through M02's add function, not a second writer.

Tests: integration tier, txtar cases — a tier with one `[clarify]`, one `[unknown]` and one broken link files three items and prints `3 created, 0 already tracked`; a second scan prints `0 created, 3 already tracked`; a scan after one item is closed `dropped` still files nothing for it.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Mark scanning with heading anchors. | `booping-python/src/booping/specs/open_items.py` | 1 | done |
| 5.2 | Check-finding items and the dedup key. | `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/commands/specs.py` | 2 | done |
| 5.3 | The three cases. | `booping-python/e2e/cases/specs/open-items-scan-*.txtar` | 1 | done |

## Definition of Done

### Task 5.1

- [x] A mark mid-sentence (not at an item or sentence start) is not filed.
- [x] The anchor is `site/markdown.py`'s `slug` of that heading.

### Task 5.2

- [x] Check findings come from the check module's data, not parsed text.
- [x] The final line is exactly `{n} created, {m} already tracked`.

### Task 5.3

- [x] Three cases, one per behaviour named in Tests.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/specs/check.py` — `Finding` and the check entry point.
- `booping-python/src/booping/specs/site/markdown.py` — `slug`, the heading anchor.
- `booping-python/e2e/cases/specs/` — any `check-*.txtar` case for a tier fixture with a broken link.

## Verify

`just e2e -k "open-items-scan"`
