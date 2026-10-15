---
id: "03"
title: "Ideas, records and marks sections"
sp: 4
status: pending
plan: "plans/202610151903_computed-status-report/index.md"
---

# M03: Ideas, records and marks sections

`booping status` prints all five lines — `items`, `ideas`, `plans`, `records`, `marks`; `booping status ideas records marks` prints their tables.

**Scope**: in `booping-python/src/booping/specs/records.py` add `unreviewed(record) -> bool` (`not record.frontmatter.get("reviewed")`); `booping-python/src/booping/specs/site/pages.py` drops its `_unreviewed` and calls it. In `booping-python/src/booping/specs/open_items.py` add a `Mark` result (`kind`, `record`, `text`) and `marks(records, tier_root) -> list[Mark]` holding today's `mark_candidates` walk, with `_marks_in` returning the kind beside each title; `mark_candidates` becomes `[Candidate("mark", m.record, m.text) for m in marks(...)]`, so `scan` files exactly what it filed before.

In `booping-python/src/booping/status.py` load the project tier once per call — `booping.specs.tiers.resolve_tiers` → the `project` tier, `load_tier` with the types of `core.specs.format` (the way `commands/specs.py` does it); a tier root that does not exist yields no records. Add three sections in `SECTIONS` order `items, ideas, plans, records, marks`:

- `ideas` — `idea` records with `status: open` whose ref (`idea/NNNN`) is not the `record` (text before `#`) of any non-terminal item. Summary `ideas: {n} open, not taken` or `ideas: none`; detail `| ref | title | created_at |` by ref.
- `records` — records where `unreviewed` holds. Summary `records: {n} unreviewed — {type} {k}, …`, types in the format's schema order, zero counts omitted, or `records: none unreviewed`; detail `| ref | status | title |`, type order then number, `—` for a missing status.
- `marks` — `marks(...)` over the tier. Summary `marks: {n} — clarify {c}, unknown {u}` or `marks: none`; detail `| kind | record | text |` in record then document order.

Tables go through `booping.query.as_table` or the same cell rendering (`—` for empty). Tests: unit — `booping-python/tests/specs/open_items_test.py` gains a case asserting `marks` kinds on a record holding one `[clarify]` and one `[unknown]` sentence and a quoted `` `[clarify]` `` that is not a mark; integration — e2e `booping-python/e2e/cases/status/` cases over a vault with ideas `open` (one tracked by an open item, one not) and `accepted`, records with and without `reviewed`, and marks of both kinds: the five-line short report, and `status ideas records marks` detail; the existing `items/scan-*` and specs-site cases pass unchanged.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Shared `unreviewed`; `marks()` with kinds under `mark_candidates`; unit case. | `booping-python/src/booping/specs/records.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/open_items.py`, `booping-python/tests/specs/open_items_test.py` | 2 | pending |
| 3.2 | Project-tier load and the ideas, records and marks sections; e2e cases. | `booping-python/src/booping/status.py`, `booping-python/e2e/cases/status/*.txtar` | 2 | pending |

## Definition of Done

### Task 3.1

- [ ] `grep -n "_unreviewed" booping-python/src/booping/specs/site/pages.py` prints nothing.
- [ ] `uv run pytest e2e/cases/items tests/specs` passes unchanged except the new unit case.

### Task 3.2

- [ ] `bin/booping status` in this repo prints the five lines in the locked order and shape.
- [ ] The new status cases pass with every M01–M02 case.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/commands/specs.py` — how a tier is resolved and loaded (`_assemble`, `_select_tier`, `_known_types`).
- `booping-python/e2e/cases/items/scan-files-one-item-per-mark-and-finding.txtar` — a fixture with marks in tier records.
- `src/specs/README.md` — the record format, `reviewed`, marks.

## Verify

`cd booping-python && uv run pytest e2e/cases/status e2e/cases/items tests/specs -q`
