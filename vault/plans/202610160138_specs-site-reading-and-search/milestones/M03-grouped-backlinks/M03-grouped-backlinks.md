---
id: "03"
title: "Backlinks grouped by type and by section"
sp: 3
status: pending
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M03: Backlinks grouped by type and by section

"Referenced by" groups citing records by type, says through which relation or section each one links here, and lists which of this record's headings are linked.

**Scope**: new `booping-python/src/booping/specs/site/backlinks.py` (`backlink_groups(site, record, rendered) -> Backlinks(by_type: [TypeGroup(type, label, items: [Backlink(record, via: [str])])], by_section: [SectionGroup(heading, sources: [record])])`, a pure function over `Site.backlinks`, `Site.relations`, `Site.resolve_link` and the sources' `Rendered.links` / `Rendered.headings`), `pages.py` (`_record_view` passes the groups instead of the flat list; called after every body is rendered), `templates/record.html.j2` (the "Referenced by" section), `style.css` (`.via`), `src/config.yaml` (`by_section`, `via` in `en` and `ru`). Exactly `../../clarifications.md` C4. `model.py` and `machine.py` are not changed.

Tests (integration, new `booping-python/tests/specs/site_backlinks_test.py` over a fixture site built with `load_site`): a value cited by one rule through `values:` and by one ADR from its `## Decision` and `## Consequences` gives by-type groups in site type order with hand-derived `via` lists (`["Serves values"]`-style relation label; `["Decision", "Consequences"]`); a body link before any `##` reads as the source title; a link `value/0001-x.md#why` where `## Why` exists gives one by-section entry `Why ← adr/0001`, and an anchor naming no heading gives none. Rebaseline `site-*.txtar` goldens and read the diff: the "Referenced by" section only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `backlinks.py` and its tests. | `booping-python/src/booping/specs/site/backlinks.py`, `booping-python/tests/specs/site_backlinks_test.py` | 2 | pending |
| 3.2 | Wire into `_record_view` and `record.html.j2`; labels; CSS; golden rebaseline. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/style.css`, `src/config.yaml`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] By-type groups, `via` lists and by-section entries match C4 on the test fixtures, deterministic order throughout.

### Task 3.2

- [ ] "Referenced by" renders an `h3` per type, each item `rel_item` + `.via` line, then the `by_section` `h3` when non-empty; `nothing_references` when there are no backlinks.
- [ ] `by_section` and `via` resolve in `en` and `ru`.
- [ ] `site-*.txtar` goldens rebaselined; their diff is the "Referenced by" section only.

Return: the list of changed and created files, nothing else.

## References

- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `backlinks()` (by type, then by the viewed record's heading).
- `booping-python/src/booping/specs/site/model.py` — `_backlinks`, `resolve_link`, `relations`.

## Verify

`cd booping-python && uv run pytest tests/specs/site_backlinks_test.py tests/specs/site_pages_test.py e2e -k site -q`
